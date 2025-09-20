# PyPolite

**PyPolite** is a lightweight middleware to detect and block profanity/abusive words in API requests.
Supports **Django**, **Flask**, and **FastAPI**. Requests containing forbidden words are blocked with a `400` response.

---

## Features

* Middleware for **Django**, **Flask**, and **FastAPI**.
* Configurable profanity word list.
* Configurable endpoints and request fields to check.
* Safe fallback if request body is not JSON.
* Optional framework-specific installation.

---

## Installation

Install the package for your framework:

**Django**

```bash
pip install pypolite[django]
```

**Flask**

```bash
pip install pypolite[flask]
```

**FastAPI**

```bash
pip install pypolite[fastapi]
```

Or install core only (without framework dependencies):

```bash
pip install pypolite
```

---

## Usage

### Django

```python
# settings.py
PYPOLITE_WORDS = ["idiot", "stupid"]
PYPOLITE_FIELDS = ["message", "comment"]
PYPOLITE_ENDPOINTS = ["/api/"]

# middleware.py
from pypolite.django_middleware import PyPoliteDjangoMiddleware
MIDDLEWARE = [
    # other middleware...
    "pypolite.django_middleware.PyPoliteDjangoMiddleware",
]
```

### Flask

```python
from flask import Flask
from pypolite.flask_middleware import PyPoliteFlaskMiddleware

app = Flask(__name__)
PyPoliteFlaskMiddleware(app, profanity_words=["idiot", "stupid"], endpoints=["/echo/"], fields=["message"])
```

### FastAPI

```python
from fastapi import FastAPI
from pypolite.fastapi_middleware import PyPoliteFastAPIMiddleware

app = FastAPI()
PyPoliteFastAPIMiddleware(app, profanity_words=["idiot", "stupid"], endpoints=["/echo/"], fields=["message"])
```

---

## Helper Function

You can directly use the profanity check function:

```python
from pypolite.profanity import contains_profanity_words

text = "You are stupid!"
words = ["idiot", "stupid"]

if contains_profanity_words(text, words):
    print("Profanity detected!")
```

---

## Running Tests

We use `pytest` for testing. To run tests:

```bash
pip install -e .[test]  # optional: include pytest in extras
pytest -v
```

Tests include:

* Unit tests for `contains_profanity_words`
* Middleware integration tests for Django, Flask, and FastAPI

---

## Contributing

We welcome contributions!

1. Fork the repo.
2. Create a feature branch (`git checkout -b feature/my-feature`).
3. Write tests for your feature.
4. Ensure all tests pass (`pytest -v`).
5. Commit and push (`git commit -am 'Add new feature' && git push`).
6. Open a pull request.

---

## License

MIT License © Kathan Naik


