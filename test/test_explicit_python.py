"""Test cases for Python-specific explicit debloating"""
from carve.resource_debloater.PythonResourceDebloater import PythonResourceDebloater
import libcst as cst

def test_explicit_python_segment():
    input = \
    """
a = 1
###[Variant_A]~
if a == 2:
    print("a is 2")
else:
    print(f"a is {a}")
###~
a = 2
    """
    expected = \
    """
a = 1
### Segment Debloated.



a = 2
    """
    debloater = PythonResourceDebloater(location="dummy", target_features={"Variant_A"})
    debloater.module = cst.parse_module(input)
    debloater.debloat_explicit()
    assert debloater.module.code == expected

def test_explicit_python_file():
    input = \
    """
###[Variant_A]!
a = 1
if a == 2:
    print("a is 2")
else:
    print(f"a is {a}")
a = 2
    """
    expected = \
    """### File Debloated.


"""
    debloater = PythonResourceDebloater(location="dummy", target_features={"Variant_A"})
    debloater.module = cst.parse_module(input)
    debloater.debloat_explicit()
    assert debloater.module.code == expected
