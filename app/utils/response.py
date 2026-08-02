def error_response(message: str, status_code: int, details=None):
    body = {
        "success": False,
        "message": message,
        "status_code": status_code,
    }
    if details is not None:
        body["details"] = details
    return body