#Errors raised by the feature modules. The UI shows their message to the user.


class ServiceError(Exception):

class ValidationError(ServiceError):
    pass
class PermissionDenied(ServiceError):
    pass
class AuthError(ServiceError):
    pass
class NotFound(ServiceError):
    pass
class Conflict(ServiceError):
    pass
