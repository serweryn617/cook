class ProcessError(Exception):
    def __init__(self, message, return_code):
        super().__init__(message)
        self.return_code = return_code
