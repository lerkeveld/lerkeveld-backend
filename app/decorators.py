from functools import wraps
from threading import Thread


def async(func):
    """
    A decorator which transforms the function to a function which starts a new
    thread which executes the function with the same arguments.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        thr = Thread(target=func, args=args, kwargs=kwargs)
        thr.start()
    return wrapper
