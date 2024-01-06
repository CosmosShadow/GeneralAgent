# FunctionSearcher: Provide a search function to find the most similar tools for Python Code Interpreter.

class FunctionSearcher:

    def __init__(self, name):
        """
        @param name: package name of all functions, like 'tools'. Then agent can use the functions in python interpreter like `tools.function_name()`
        """
        self._name = name
        self._functions_dict = {}

    def __setattr__(self, name, value):
        if name.startswith('_'):
            object.__setattr__(self, name, value)
        else:
            self._functions_dict[name] = value

    def __getattr__(self, name):
        if name.startswith('_'):
            return object.__getattr__(self, name)
        else:
            return self._functions_dict.get(name, None)
        
    def _add_functions(self, functions):
        """
        Add functions to tool manager
        @param functions: a dict of functions
        """
        for fun in functions:
            self._functions_dict[fun.__name__] = fun

    def _delete_functions(self, functions):
        """
        Delete functions from tool manager
        @param functions: a list of function names
        """
        for fun in functions:
            self._functions_dict.pop(fun.__name__, None)

    def _load_functions(self, directory):
        """
        Load functions from python directory (recursively)
        @param directory: the path of python directory
        """
        self._functions_dict = {}
        from GeneralAgent.skills.python_envs import load_functions_with_directory
        funcs = load_functions_with_directory(directory)
        for fun in funcs:
            self._functions_dict[fun.__name__] = fun

    def _search_function(self, query) -> str:
        """
        search function by description and return the function signatures
        @param query: the query string
        @return: the most similar function signatures
        """
        from GeneralAgent.skills.llm_inference import search_similar_texts
        from GeneralAgent.skills.python_envs import get_function_signature
        signatures = [get_function_signature(x, self._name) for x in self._functions_dict.values()]
        results = search_similar_texts(query, signatures, top_k=5)
        return '\n'.join(results)