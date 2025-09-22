import json
from .profanity import SimpleChecker

try:
    from flask import request, jsonify
except ImportError as e:
    raise ImportError(
        "Flask is not installed. To use PyPolite with Flask, run:\n\n"
        "    pip install pypolite[flask]\n"
    ) from e


class PyPoliteFlaskMiddleware:
    """
    Middleware to check API request fields for profanity/abusive words.
    Blocks requests with status 400 if profanity is detected.
    """

    def __init__(self, app=None, profanity_words=None, endpoints=None, fields=None):
        self.app = app
        self.profanity_words = profanity_words or ["badword", "abuse"]
        self.endpoints_to_check = endpoints or ["/api/"]
        self.fields_to_check = fields or ["message", "comment"]
        self.simple_checker = SimpleChecker(profanity_words=self.profanity_words)

        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """Attach middleware to Flask app."""
        app.before_request(self.check_request)

    def check_request(self):
        if request.path in self.endpoints_to_check and request.method in ["POST", "PUT", "PATCH"]:
            try:
                if request.is_json:
                    data = request.get_json(silent=True) or {}

                    for field in self.fields_to_check:
                        if field in data and isinstance(data[field], str):
                            if self.simple_checker.contains_profanity(data[field]):
                                return jsonify({"error": f"Profanity detected in field '{field}'."}), 400
            except Exception:
                # Don’t break the app if parsing fails
                pass
