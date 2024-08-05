class UserError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class ServerError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)
