from Response import SuccessResponse, ErrorResponse


class FibonacciHandler:
    @staticmethod
    def handle_request(path_splitted):
        if len(path_splitted) >= 3 and path_splitted[2]:
            n_str = path_splitted[2]
            try:
                index = int(n_str)
                if index < 0:
                    raise ValueError("Negative index")

                a, b = 0, 1
                for _ in range(index):
                    a, b = b, a + b
                return SuccessResponse(a, 200)
            except ValueError as e:
                if str(e) == "Negative index":
                    return ErrorResponse("Negative index", 400)
                else:
                    return ErrorResponse("Invalid index", 422)
        else:
            return ErrorResponse("Missing index", 422)
