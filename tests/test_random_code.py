


from griffe.tests import temporary_visited_module
from pysource_codegen import generate
from pysource_minimize import minimize
import pytest

@pytest.mark.parametrize("seed",range(200))
def test_visit_arbitrary_code(seed):
    code=generate(seed)
    
    def contains_bug(code):
        try:
            with temporary_visited_module(code) as module:
                return not bool(module)
        except:
            return True

    if contains_bug(code):
        
        new_code=minimize(code,contains_bug)

        print("the following code can not be parsed:")
        print(new_code)

        with temporary_visited_module(new_code) as module:
            return module is None





