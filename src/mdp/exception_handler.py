import sys
import inspect


def exception_handler(log_type):
    def decorator(func):
        def inner(*args, **kwargs):
            try:
                func(*args, **kwargs)
            except Exception:
                _, value, traceback = sys.exc_info()
                print('TYPE %s \nFILE %s \nFUNC %s \nLINE %s \nERRR %s \nINPT %s' % (log_type, inspect.getfile(
                    func), func.__name__, str(traceback.tb_next.tb_lineno), str(value), str(args) + str(kwargs)))

        return inner

    return decorator
