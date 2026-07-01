class ProcessError(Exception):
    def __init__(self, message: str, return_code: int) -> None:
        super().__init__(message)
        self.return_code = return_code


class ConfigurationError(Exception):
    pass
