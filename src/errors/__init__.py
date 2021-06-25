class WeminderAPIError(Exception):
    """Base class for errors"""
    
    message = ''
    status = 0

    def json(self):
        return f"{{ \"error\": \"{self.message}\", \"status\": \"{self.status}\" }}"

class NotFoundError(WeminderAPIError):
    def __init__(self, request: str):
        super(NotFoundError, self).__init__(request)
        self.message = f"{request} not found"
        self.status = 404

class BadRequestError(WeminderAPIError):
    def __init__(self, message: str):
        super(BadRequestError, self).__init__(message)
        self.message = message
        self.status = 400

class InternalErrorError(WeminderAPIError):
    def __init__(self, message: str):
        super(InternalErrorError, self).__init__(message)
        self.message = message
        self.status = 500