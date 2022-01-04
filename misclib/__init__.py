import functools


# region [decorator]
def try_catch(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            ret = func(*args, **kwargs)
            ret_msg = f'[{func.__name__}] ret: {ret}'
        except Exception as e:
            ret = False
            ret_msg = f'[{func.__name__}] exception!!!\n{type(e).__name__}!!! {e}'
        return ret, ret_msg

    return wrapper
# endregion [decorator]
