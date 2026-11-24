#Custom exceptions
#Errors raised by the feature modules. The UI shows hypothetically their message to the user.


class ServiceError(Exception):
    pass
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
