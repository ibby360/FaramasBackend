def format_response(status, message, data=None):
    """
    Helper function to format the response for API calls.
    
    :param status: HTTP status code
    :param message: Message to be included in the response
    :param data: Optional data to be included in the response
    :return: Formatted response dictionary
    """
    response = {
        'status': status,
        'message': message,
    }
    if data is not None:
        response['data'] = data
    return response