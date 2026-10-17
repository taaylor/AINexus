from typing import Protocol


class IUseCase[InputData, OutputData](Protocol):
    async def execute(self, *, input_data: InputData) -> OutputData:
        pass
