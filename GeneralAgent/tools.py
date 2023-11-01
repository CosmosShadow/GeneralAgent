class Tools():
    def __init__(self, funs=[]):
        self.funs = funs

    def add_funs(self, funs):
        self.funs += funs

    def get_funs_description(self):
        from GeneralAgent import skills
        return '\n\n'.join([skills.get_function_signature(fun) for fun in self.funs])

