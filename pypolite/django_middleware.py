import json
from .profanity import SimpleChecker

try:
    from django.http import JsonResponse
    from django.conf import settings
except ImportError as e:
    raise ImportError(
        "Django is not installed. To use PyPolite with Django, run:\n\n"
        "    pip install pypolite[django]\n"
    ) from e


class PyPoliteDjangoMiddleware:
    """
    Middleware to check API request fields for profanity/abusive words.
    Blocks requests with status 400 if profanity is detected.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.profanity_words = getattr(settings, "PYPOLITE_WORDS", ["badword", "abuse"])
        self.endpoints_to_check = getattr(settings, "PYPOLITE_ENDPOINTS", ["/api/"])
        self.fields_to_check = getattr(settings, "PYPOLITE_FIELDS", ["message", "comment"])
        self.simple_checker = SimpleChecker(profanity_words=self.profanity_words)

    def __call__(self, request):
        if request.path in self.endpoints_to_check and request.method in ["POST", "PUT", "PATCH"]:
            try:
                if request.content_type == "application/json":
                    body_unicode = request.body.decode("utf-8")
                    if body_unicode:
                        data = json.loads(body_unicode)

                        for field in self.fields_to_check:
                            if field in data and isinstance(data[field], str):
                                if self.simple_checker.contains_profanity(data[field]):
                                    return JsonResponse(
                                        {"error": f"Profanity detected in field '{field}'."},
                                        status=400
                                    )
            except Exception:
                # Don’t break app if parsing fails
                pass

        return self.get_response(request)
