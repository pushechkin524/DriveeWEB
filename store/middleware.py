import threading

_thread_local = threading.local()


def get_current_user():
    """Return the user saved for the current thread (may be None)."""
    return getattr(_thread_local, "user", None)


class CurrentUserMiddleware:
    """
    Saves request.user in thread‑local storage so signals can log the actor.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _thread_local.user = getattr(request, "user", None)
        response = self.get_response(request)
        _thread_local.user = None
        return response
