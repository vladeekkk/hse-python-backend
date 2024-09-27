from Response import SuccessResponse, ErrorResponse
import json


class MeanHandler:
    @staticmethod
    def handle_request(body):
        try:
            body_data = json.loads(body.decode("utf-8"))
            if not isinstance(body_data, list) or not all(
                    isinstance(x, (int, float)) for x in body_data
            ):
                raise ValueError("Invalid input")
            if len(body_data) == 0:
                raise ValueError("Empty array")
            mean_value = sum(body_data) / len(body_data)
            return SuccessResponse(mean_value, 200)
        except (
                ValueError,
                json.JSONDecodeError,
        ) as e:  # если тело не массив чисел или оно пустое
            if str(e) == "Empty array":
                return ErrorResponse("Empty array", 400)
            else:
                return ErrorResponse("Invalid input", 422)
