from rest_framework.response import Response


def success_response(data=None, status=200):
    return Response({
        "success": True,
        "data": data,
        "error": None
    }, status=status)


def error_response(error_dict, status=400):
    return Response({
        "success": False,
        "data": None,
        "error": error_dict
    }, status=status)
