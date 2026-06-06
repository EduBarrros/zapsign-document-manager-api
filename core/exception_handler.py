import logging
from rest_framework.views import exception_handler
from core.response import error
from core.exceptions import DomainException

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if isinstance(exc, DomainException):
        return error(
            message=str(exc),
            code=exc.__class__.__name__.replace("Exception", "").upper(),
            status=400
        )

    if response is not None:
        return error(
            message=str(response.data),
            code="DRF_ERROR",
            status=response.status_code
        )

    return error(
        message="Internal server error",
        code="INTERNAL_ERROR",
        status=500
    )