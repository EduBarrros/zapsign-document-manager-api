from rest_framework.response import Response


def api_response(*, data=None, error=None, error_code=None, status=200):
    return Response(
        {
            "data": data,
            "error": {"message": error, "code": error_code} if error else None,
        },
        status=status,
    )


def error(*, message, code, status):
    return api_response(error=message, error_code=code, status=status)