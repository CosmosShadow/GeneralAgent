class Tools():
    def __init__(self, funs=[]):
        self.funs = funs

    def add_funs(self, funs):
        self.funs += funs

    def get_funs_description(self):
        return '\n\n'.join([get_function_signature(fun) for fun in self.funs])

def get_function_signature(func):
    """Returns a description string of function"""
    import inspect
    sig = inspect.signature(func)
    sig_str = str(sig)
    desc = f"{func.__name__}{sig_str}"
    if func.__doc__:
        desc += ': ' + func.__doc__.strip()
    return desc