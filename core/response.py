from rest_framework.response import Response


def api_response(*, data=None, error=None, error_code=None, status=200):
    return Response(
        {
            "data": data,
            "error": {"message": error, "code": error_code} if error else None,
        },
        status=status,
    )