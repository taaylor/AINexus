-- Подключаем JWT-библиотеку и валидаторы для стандартных и пользовательских claims.
local jwt = require "resty.jwt"
local validators = require "resty.jwt-validators"
local redis = require "resty.redis"

-- Настройки circuit breaker: 3 ошибки открывают его на 3 секунды.
local redis_failure_limit = 3
local redis_cooldown_seconds = 3

-- Подключаемся к Redis, авторизуемся и выбираем нужную базу.
local function prepare_redis_connection(redis_client)
    -- Подключаемся к Redis из конфигурации Nginx.
    local ok, err = redis_client:connect(
        os.getenv("REDIS_HOST") or "redis",
        tonumber(os.getenv("REDIS_PORT") or "6379")
    )
    if not ok then
        return false, err
    end

    -- Авторизуемся, если для Redis задан пароль.
    local password = os.getenv("REDIS_PASSWORD")
    if password and password ~= "" then
        ok, err = redis_client:auth(password)
        if not ok then
            return false, err
        end
    end

    -- Выбираем ту же Redis-базу, что использует auth-сервис.
    ok, err = redis_client:select(tonumber(os.getenv("REDIS_DB") or "0"))
    if not ok then
        return false, err
    end

    return true
end

-- Пропускаем Redis-проверку при сбое Redis и сохраняем работу API.
local function allow_request_without_redis(circuit, redis_client, error_message)
    -- Закрываем неисправное соединение, чтобы не возвращать его в пул.
    if redis_client then
        redis_client:close()
    end

    -- Увеличиваем число последовательных ошибок Redis.
    local failures, err = circuit:incr("failures", 1, 0)

    if not failures then
        ngx.log(ngx.ERR, "Could not update Redis circuit breaker: ", err)
        return false
    end

    -- Открываем circuit после достижения порога ошибок.
    if failures >= redis_failure_limit then
        circuit:set("open_until", ngx.now() + redis_cooldown_seconds)
        circuit:delete("probe")
        ngx.log(ngx.WARN, "Redis circuit breaker opened: ", error_message)
    else
        ngx.log(ngx.WARN, "Redis check failed: ", error_message)
    end

    return false
end

-- Проверяем, отозвана ли сессия; при сбое Redis возвращаем fail-open результат.
local function is_session_revoked(session_id)
    -- Берём общее состояние circuit breaker для worker-процессов Nginx.
    local circuit = ngx.shared.redis_circuit
    local open_until = circuit:get("open_until")

    -- Пропускаем Redis, пока circuit открыт.
    if open_until and open_until > ngx.now() then
        return false
    end

    -- После паузы допускаем только один пробный запрос к Redis.
    if open_until then
        local probe_acquired = circuit:add("probe", "1", 1)
        if not probe_acquired then
            return false
        end
    end

    -- Создаём Redis-клиент с коротким timeout.
    local redis_client = redis:new()
    redis_client:set_timeout(100)

    -- Подготавливаем соединение перед чтением ключа отозванной сессии.
    local ok, err = prepare_redis_connection(redis_client)
    if not ok then
        return allow_request_without_redis(circuit, redis_client, err)
    end

    -- Ищем ключ отзыва в том же формате, который использует auth-сервис.
    local revoked, get_err = redis_client:get("auth:revoked-session:" .. session_id)
    if revoked == nil then
        return allow_request_without_redis(circuit, redis_client, get_err)
    end

    -- Возвращаем рабочее соединение в keepalive-пул для следующих запросов.
    local keepalive_ok, keepalive_err = redis_client:set_keepalive(10000, 100)
    if not keepalive_ok then
        ngx.log(ngx.WARN, "Could not return Redis connection to pool: ", keepalive_err)
    end

    -- Успешный Redis-ответ сбрасывает ошибки и закрывает circuit.
    circuit:delete("failures")
    circuit:delete("open_until")
    circuit:delete("probe")

    -- Любое существующее значение ключа означает отозванную сессию.
    return revoked ~= ngx.null
end

-- Разрешаем только алгоритм, которым auth-сервис подписывает access-токены.
jwt:set_alg_whitelist({ RS256 = 1 })

-- Возвращаем стандартный ответ для отсутствующего или невалидного Bearer-токена.
local function reject_unauthorized()
    -- Сохраняем заголовок для стандартных HTTP-клиентов.
    ngx.header["WWW-Authenticate"] = 'Bearer realm="auth-service"'

    -- Указываем, что тело ответа содержит JSON.
    ngx.header["Content-Type"] = "application/json; charset=utf-8"

    -- Устанавливаем HTTP-статус 401 перед отправкой тела.
    ngx.status = ngx.HTTP_UNAUTHORIZED

    -- Возвращаем единый JSON-ответ вместо стандартной HTML-страницы Nginx.
    ngx.print('{"detail":"Unauthorized"}')

    -- Завершаем запрос, не заменяя установленный выше статус 401.
    return ngx.exit(ngx.HTTP_OK)
end

-- Достаём Authorization и требуем формат "Bearer <token>".
local authorization = ngx.var.http_authorization
if not authorization then
    return reject_unauthorized()
end

local scheme, token = authorization:match("^(%S+)%s+(.+)$")
if not scheme or scheme:lower() ~= "bearer" then
    return reject_unauthorized()
end

-- Описываем обязательные claims и правила их проверки:
-- срок действия и время выпуска, тип токена, ID пользователя и сессии,
-- username и два флага пользователя должны присутствовать в подписанном токене.
local claim_spec = {
    exp = validators.required(validators.is_not_expired()),
    iat = validators.required(function(value)
        return type(value) == "number" and value <= ngx.time()
    end),
    token_type = validators.equals("access"),
    id = validators.required(),
    session_id = validators.required(),
    username = validators.required(),
    is_platform_admin = function(value)
        return value ~= nil
    end,
    is_verified_email = function(value)
        return value ~= nil
    end,
}

-- Проверяем подпись и claims JWT публичным ключом auth-сервиса.
-- Ошибка в библиотеке, подписи или любом claim отклоняет запрос с 401.
local ok, jwt_obj = pcall(jwt.verify, jwt, jwt_public_key, token, claim_spec)
if not ok or not jwt_obj or not jwt_obj.verified or not jwt_obj.valid then
    return reject_unauthorized()
end

-- Перезаписываем одноимённые входящие заголовки значениями только из проверенного JWT.
local claims = jwt_obj.payload

-- Отклоняем сессию, если Redis подтвердил, что она была отозвана.
if is_session_revoked(claims.session_id) then
    return reject_unauthorized()
end

ngx.req.set_header("X-Session-ID", claims.session_id)
ngx.req.set_header("X-User-ID", claims.id)
ngx.req.set_header("X-Username", claims.username)
ngx.req.set_header("X-Is-Platform-Admin", tostring(claims.is_platform_admin))
ngx.req.set_header("X-Is-Verified-Email", tostring(claims.is_verified_email))
