"""Test cases for PythonImplicitDebloater"""
from carve.resource_debloater.PythonImplicitDebloater import PythonImplicitDebloater
import libcst as cst


def test_if():
    input = \
    """
a = 1
###[Variant_A]~
if a == 2:
    print("a is 2")
else:
    print(f"a is {a}")
    """
    expected = \
    """
a = 1
###[Variant_A]~
if a == 2:
    # If Statement Branch Debloated
else:
    print(f"a is {a}")
    """
    module = cst.parse_module(input)
    modified = module.visit(PythonImplicitDebloater())
    assert modified.code == expected

def test_if_no_else():
    input = \
    """
a = 1
###[Variant_A]~
if a == 2:
    print("a is 2")
a = 2
    """
    expected = \
    """
a = 1
# If Statement Debloated
a = 2
    """
    module = cst.parse_module(input)
    modified = module.visit(PythonImplicitDebloater())
    assert modified.code == expected

def test_else():
    input = \
    """
a = 1
if a == 2:
    print("a is 2")
###[Variant_A]~
else:
    print(f"a is {a}")
    """
    expected = \
    """
a = 1
if a == 2:
    print("a is 2")
###[Variant_A]~
else:
    # Else Statement Debloated
    """
    module = cst.parse_module(input)
    modified = module.visit(PythonImplicitDebloater())
    assert modified.code == expected

def test_function():
    input = \
    """
a = 1
###[Variant_A]~
def func(a):
    a += 1
    print(a)
a = 2
    """
    expected = \
    """
a = 1
# Function Debloated
a = 2
    """
    module = cst.parse_module(input)
    modified = module.visit(PythonImplicitDebloater())
    assert modified.code == expected
