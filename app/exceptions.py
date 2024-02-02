# List of common exceptions.

class NotFoundException(Exception) : 
    pass

class InvalidPassword(Exception): 
    pass

class WrongOptionException(Exception):
    pass

class ValidationException(Exception):
    pass

class InvalidLength(Exception):
    pass

class UserCreationException(Exception):
    pass

# Use of this is optional. Useful when raising exceptions in services. 
class ErrorMessage:
    def __init__(self, message, status_code):
        self.message = message
        self.status_code = status_code