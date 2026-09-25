def success_response(data=None, message=None, status_code=200):
    """
    Build a standardized successful API response.
    """

    response = {
        "success": True,
    }

    if message is not None:
        response["message"] = message

    if data is not None:
        response["data"] = data

    return response, status_code


def error_response(message, status_code=400):
    """
    Build a standardized error API response.
    """

    return {
        "success": False,
        "message": message,
    }, status_code