import json
from .profanity import contains_profanity_words

try:
    from fastapi import FastAPI, Request
    from fastapi.responses import JSONResponse
except ImportError as e:
    raise ImportError(
        "FastAPI is not installed. To use PyPolite with FastAPI, run:\n\n"
        "    pip install pypolite[fastapi]\n"
    ) from e


class PyPoliteFastAPIMiddleware:
    """
    Middleware to check API request fields for profanity/abusive words.
    Blocks requests with status 400 if profanity is detected.
    """

    def __init__(self, app: FastAPI, profanity_words=None, endpoints=None, fields=None):
        self.app = app
        self.profanity_words = profanity_words or ["badword", "abuse"]
        self.endpoints_to_check = endpoints or ["/api/"]
        self.fields_to_check = fields or ["message", "comment"]

        app.middleware("http")(self.middleware)

    async def middleware(self, request: Request, call_next):
        if (
            request.url.path in self.endpoints_to_check
            and request.method in ["POST", "PUT", "PATCH"]
        ):
            try:
                if request.headers.get("content-type") == "application/json":
                    body = await request.body()
                    if body:
                        data = json.loads(body.decode())

                        for field in self.fields_to_check:
                            if field in data and isinstance(data[field], str):
                                if contains_profanity_words(data[field], self.profanity_words):
                                    return JSONResponse(
                                        {"error": f"Profanity detected in field '{field}'."},
                                        status_code=400,
                                    )
            except Exception:
                # Don’t break app if parsing fails
                pass

        return await call_next(request)
