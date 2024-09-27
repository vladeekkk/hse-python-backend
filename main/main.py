from typing import Any, Awaitable, Callable

from Response import ErrorResponse
from QueryParser import QueryParser
from FactorialHandler import FactorialHandler
from FibonacciHandler import FibonacciHandler
from MeanHandler import MeanHandler

async def app(
    scope: dict[str, Any],
    receive: Callable[[], Awaitable[dict[str, Any]]],
    send: Callable[[dict[str, Any]], Awaitable[None]],
) -> None:
    assert scope["type"] == "http"

    if scope["path"] == "/factorial" and scope["method"] == "GET":
        query_params = scope.get("query_string", b"").decode("utf-8")
        params = QueryParser.parse(query_params)
        response = FactorialHandler.handle_request(params)

    elif scope["path"].startswith("/fibonacci/") and scope["method"] == "GET":
        path_splitted = scope["path"].split("/")
        response = FibonacciHandler.handle_request(path_splitted)

    elif scope["path"] == "/mean" and scope["method"] == "GET":
        body = b""
        while True:
            message = await receive()
            if message["type"] != "http.request":
                continue
            body += message.get("body", b"")
            if not message.get("more_body", False):
                break
        response = MeanHandler.handle_request(body)
    else:  # левый запрос
        response = ErrorResponse("Not Found", 404)

    await send_json_response(send, response)

async def send_json_response(send, response):
    message, status_code = response.get_response()
    await send(
        {
            "type": "http.response.start",
            "status": status_code,
            "headers": [(b"content-type", b"application/json")],
        }
    )
    await send(
        {
            "type": "http.response.body",
            "body": message.encode("utf-8"),
        }
    )
