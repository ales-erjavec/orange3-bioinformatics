"""

"""
import time
import threading
from functools import wraps

import requests

from . import conf

REST_API = "https://rest.kegg.jp/"


def rate_limit(max_requests=3, window_seconds=1):
    """
    Decorator to rate limit a function.

    Args:
        max_requests: Maximum allowed calls within the time window.
        window_seconds: Time window in seconds.
    """
    def decorator(func):
        request_timestamps = []
        lock = threading.Lock()
        @wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal request_timestamps
            now = time.time()
            with lock:
                # Remove timestamps outside the current window
                request_timestamps = [
                    t for t in request_timestamps if now - t < window_seconds
                ]
                if len(request_timestamps) >= max_requests:
                    # Calculate when the oldest request in the window expires
                    try_after = window_seconds - (now - request_timestamps[0])
                    time.sleep(try_after)
                    now = time.time()
                request_timestamps.append(now)

            return func(*args, **kwargs)
        return wrapper
    return decorator


class KEGGLimitedSession(requests.Session):
    @rate_limit(max_requests=3, window_seconds=1)
    def send(self, *args, **kwargs):
        return super().send(*args, **kwargs)


def slumber_service():
    """
    Return a rest based service using `slumber` package
    """
    import slumber

    if not hasattr(slumber_service, "_cached"):

        class DecodeSerializer(slumber.serialize.BaseSerializer):
            key = "decode"
            content_types = ["text/plain"]

            def loads(self, data):
                return data

        # for python 2/3 compatibility
        serializer = slumber.serialize.Serializer(default="decode", serializers=[DecodeSerializer()])
        slumber_service._cached = slumber.API(REST_API, serializer=serializer, session=KEGGLimitedSession())
    return slumber_service._cached


default_service = slumber_service

web_service = slumber_service
