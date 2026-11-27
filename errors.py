#Custom exceptions
#we should use these to raise Errors for the feature modules. 
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
