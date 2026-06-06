class DomainException(Exception):
    def __init__(self, message="Error", code="DOMAIN_ERROR"):
        super().__init__(message)
        self.message = message
        self.code = code


class ValidationException(DomainException):
    pass


class AuthenticationException(DomainException):
    def __init__(self, message="Credenciais inválidas"):
        super().__init__(message, code="AUTH_INVALID")


class PermissionException(DomainException):
    pass


class NotFoundException(DomainException):
    pass


class IntegrationException(DomainException):
    pass


class PDFProcessingException(DomainException):
    pass