-- Подключаем JWT-библиотеку и валидаторы для стандартных и пользовательских claims.
local jwt = require "resty.jwt"
local validators = require "resty.jwt-validators"

-- Разрешаем только алгоритм, которым auth-сервис подписывает access-токены.
jwt:set_alg_whitelist({ RS256 = 1 })

-- Возвращаем стандартный ответ для отсутствующего или невалидного Bearer-токена.
local function reject_unauthorized()
    ngx.header["WWW-Authenticate"] = 'Bearer realm="auth-service"'
    return ngx.exit(ngx.HTTP_UNAUTHORIZED)
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

ngx.req.set_header("X-Session-ID", claims.session_id)
ngx.req.set_header("X-User-ID", claims.id)
ngx.req.set_header("X-Username", claims.username)
ngx.req.set_header("X-Is-Platform-Admin", tostring(claims.is_platform_admin))
ngx.req.set_header("X-Is-Verified-Email", tostring(claims.is_verified_email))
