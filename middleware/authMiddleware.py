from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from fastapi.responses import JSONResponse
import jwt
from datetime import datetime, timezone
from utils.utils import my_response as apiResponse
from dotenv import load_dotenv
import os

load_dotenv(".env")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

LOGIN_EXEMPT_URLS = [
    '/user/userApi/loginTeacher/',
    '/user/userApi/verifyCodeLogin/',
    '/user/userApi/loginPassword/',
]

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Get the request path
        path = request.url.path
        # If the path is not in the LOGIN_EXEMPT_URLS, proceed with authentication checks
        if path not in LOGIN_EXEMPT_URLS:
            # Check the authentication status
            authentication = await self.check_authentication(request)
            # If the user is not authenticated, return a 401 Unauthorized response
            if not authentication["authenticated"]:
                return JSONResponse(
                    status_code=401,
                    content=apiResponse(
                        status_code=401,
                        message="کاربر احراز هویت نشده است، توکن وارد نشده است",
                        data=None
                    )
                )

            # Get user information from the token
            try:
                payload = await self.decodeJWTToken(authentication.get("token"))
            except Exception as e:
                # Check if any exception occurred during token decoding
                return JSONResponse(
                    status_code=401,
                    content=apiResponse(
                        status_code=401,
                        message="توکن معتبر نمی‌باشد",
                        data=None
                    )
                )

            if (not payload["user_id"]):
                return JSONResponse(
                    status_code=401,
                    content=apiResponse(
                        status_code=401,
                        message="توکن معتبر نمی‌باشد",
                        data=None
                    )
                )

            # Add user information to request state
            request.scope.update({'user': payload})

        # Proceed with the request processing
        response = await call_next(request)
        return response

    async def decodeJWTToken(self, rawToken: str) -> dict:
        try:
            token = rawToken.replace("Bearer ", "").strip()
            decoded_token: dict = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
            if decoded_token.get("exp", 0) < datetime.now(timezone.utc).timestamp():
                return JSONResponse(
                    status_code=401,
                    content=apiResponse(
                        status_code=401,
                        message="توکن منقضی شده است",
                        data=None
                    )
                )

            return decoded_token

        except jwt.ExpiredSignatureError:
            return JSONResponse(
                status_code=401,
                content= apiResponse (
                    status_code=401,
                    message="توکن منقضی شده است",
                    data=None
                )
            )
        except jwt.InvalidTokenError:
            return JSONResponse(
                status_code=401,
                content=apiResponse(
                    status_code=401,
                    message="توکن معتبر نمیباشد",
                    data=None
                )
            )

    async def check_authentication(self, request: Request):
        # Get the authorization header from the request
        auth_header = request.headers.get("authorization")
        if not auth_header:
            return {"authenticated": False, "token": None}

        # Split the token from the header
        token_parts = auth_header.split(" ")
        if len(token_parts) != 2 or token_parts[0].lower() != "bearer":
            return {"authenticated": False, "token": None}

        # If the header is valid, return authenticated as True
        return {"authenticated": True, "token": token_parts[1]}
