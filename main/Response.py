import json

class ErrorResponse:
    def __init__(self, error_message, status_code):
        self.response_body = json.dumps({"error": error_message})
        self.status_code = status_code

    def get_response(self):
        return self.response_body, self.status_code

class SuccessResponse:
    def __init__(self, success_message, status_code):
        self.response_body = json.dumps({"result": success_message})
        self.status_code = status_code

    def get_response(self):
        return self.response_body, self.status_code
