import json
import os
from django.conf import settings
from functools import lru_cache


@lru_cache(maxsize=1)
def load_errors():
    path = os.path.join(settings.BASE_DIR, "tasks", "errors", "errors.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_error(key: str, details=None):
    errors = load_errors()
    error = errors.get(key, {
        "code": "000000",
        "message": "An unknown error occurred."
    })
    if details is not None:
        error["detail"] = details
    return error
