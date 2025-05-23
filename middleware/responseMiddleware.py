from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
import json

class ResponseWrapperMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        content = b""
        async for chunk in response.body_iterator:
            content += chunk

        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            data = content.decode()

        print(data)

        if isinstance(data, dict):
            status_code = data.pop("code", 500)
            print(status_code)
            message = data.pop("message", "عملیات با موفقیت انجام شد.")
            payload = data.get("data", None)
        else:
            status_code = 500
            message = "خروجی دیکشتری نمیباشد!! با پشتیبانی تماس بگیرید"
            payload = data
        is_success = 200 <= status_code < 300

        custom_response = {
            "status": is_success,
            "code": status_code,
            "message": message,
            "data": payload
        }

        return JSONResponse(status_code=status_code, content=custom_response)
