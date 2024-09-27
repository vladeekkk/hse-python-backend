from Response import SuccessResponse, ErrorResponse


class FactorialHandler:
    @staticmethod
    def handle_request(params):
        if "n" in params:
            n_value = params["n"]
            try:
                number = int(n_value)
                if number < 0:
                    raise ValueError("Negative number")
                result = 1
                for i in range(2, number + 1):
                    result *= i
                return SuccessResponse(result, 200)
            except ValueError as e:
                if str(e) == "Negative number":
                    return ErrorResponse("Negative number", 400)
                else:
                    return ErrorResponse("Invalid parameter 'n'", 422)
        else:
            return ErrorResponse("Missing parameter 'n'", 422)
