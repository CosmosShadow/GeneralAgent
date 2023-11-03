
def get_function_signature(func):
    """Returns a description string of function"""
    import inspect
    sig = inspect.signature(func)
    sig_str = str(sig)
    desc = f"{func.__name__}{sig_str}"
    if func.__doc__:
        desc += ': ' + func.__doc__.strip()
    if inspect.iscoroutinefunction(func):
        desc = "async " + desc
    return desc