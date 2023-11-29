"""Test cases for PythonImplicitDebloater"""
from carve.resource_debloater.PythonImplicitDebloater import PythonImplicitDebloater
import libcst as cst


def test_if():
    input = \
    """
a = 1
###[Variant_A]
if a == 2:
    print("a is 2")
else:
    print(f"a is {a}")
    """
    expected = \
    """
a = 1
if a == 2:
    ### If Statement Branch Debloated
else:
    print(f"a is {a}")
    """
    module = cst.parse_module(input)
    modified = module.visit(PythonImplicitDebloater(features={"Variant_A"}))
    assert modified.code == expected

def test_if_no_else():
    input = \
    """
a = 1
###[Variant_A]
if a == 2:
    print("a is 2")
a = 2
    """
    expected = \
    """
a = 1
### If Statement Debloated

a = 2
    """
    module = cst.parse_module(input)
    modified = module.visit(PythonImplicitDebloater(features={"Variant_A"}))
    assert modified.code == expected

def test_else():
    input = \
    """
a = 1
if a == 2:
    print("a is 2")
###[Variant_A]
else:
    print(f"a is {a}")
    """
    expected = \
    """
a = 1
if a == 2:
    print("a is 2")
else:
    ### Else Statement Debloated
    """
    module = cst.parse_module(input)
    modified = module.visit(PythonImplicitDebloater(features={"Variant_A"}))
    assert modified.code == expected

def test_function():
    input = \
    """
a = 1
###[Variant_A]
def func(a):
    a += 1
    print(a)
a = 2
    """
    expected = \
    """
a = 1
### Function Debloated

a = 2
    """
    module = cst.parse_module(input)
    modified = module.visit(PythonImplicitDebloater(features={"Variant_A"}))
    assert modified.code == expected


def test_single_statement():
    input = \
    """
print("hello world")
a = 1
a += 1
###[Variant_A]
print(f"a is {a}")
    """
    expected = \
    """
print("hello world")
a = 1
a += 1
### Statement Debloated

    """
    module = cst.parse_module(input)
    modified = module.visit(PythonImplicitDebloater(features={"Variant_A"}))
    assert modified.code == expected


def test_leading_statement():
    """CARVE will ignore leading implicit annotations"""
    input = \
    """

###[Variant_A]
def func(a):
    a += 1
    print(a)
a = 2
    """
    expected = \
    """

###[Variant_A]
def func(a):
    a += 1
    print(a)
a = 2
    """
    module = cst.parse_module(input)
    modified = module.visit(PythonImplicitDebloater(features={"Variant_A"}))
    assert modified.code == expected

def test_if_no_match():
    input = \
    """
a = 1
###[Variant_A]
if a == 2:
    print("a is 2")
else:
    print(f"a is {a}")
    """
    expected = \
    """
a = 1
###[Variant_A]
if a == 2:
    print("a is 2")
else:
    print(f"a is {a}")
    """
    module = cst.parse_module(input)
    modified = module.visit(PythonImplicitDebloater(features={"Variant_B"}))
    assert modified.code == expected


def test_function_multi():
    input = \
    """
a = 1
###[Variant_A][Variant_B]
def func(a):
    a += 1
    print(a)
a = 2
    """
    expected = \
    """
a = 1
### Function Debloated

a = 2
    """
    module = cst.parse_module(input)
    modified = module.visit(PythonImplicitDebloater(features={"Variant_A", "Variant_B", "Variant_C"}))
    assert modified.code == expected

def test_function_multi_no_match():
    input = \
    """
a = 1
###[Variant_A][Variant_B][Variant_D]
def func(a):
    a += 1
    print(a)
a = 2
    """
    expected = \
    """
a = 1
###[Variant_A][Variant_B][Variant_D]
def func(a):
    a += 1
    print(a)
a = 2
    """
    module = cst.parse_module(input)
    modified = module.visit(PythonImplicitDebloater(features={"Variant_A", "Variant_B", "Variant_C"}))
    assert modified.code == expected

def test_function_explicit_no_match():
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
###[Variant_A]~
def func(a):
    a += 1
    print(a)
a = 2
    """
    module = cst.parse_module(input)
    modified = module.visit(PythonImplicitDebloater(features={"Variant_A"}))
    assert modified.code == expected

def test_if_no_else_leading_comment():
    input = \
    """
a = 1
# keep this comment
# and this comment
###[Variant_A]
if a == 2:
    print("a is 2")
a = 2
    """
    expected = \
    """
a = 1
# keep this comment
# and this comment
### If Statement Debloated

a = 2
    """
    module = cst.parse_module(input)
    modified = module.visit(PythonImplicitDebloater(features={"Variant_A"}))
    assert modified.code == expected

def test_single_statement_leading_comment():
    input = \
    """
print("hello world")
a = 1
a += 1
# keep this comment
# and this comment
###[Variant_A]
print(f"a is {a}")
    """
    expected = \
    """
print("hello world")
a = 1
a += 1
# keep this comment
# and this comment
### Statement Debloated

    """
    module = cst.parse_module(input)
    modified = module.visit(PythonImplicitDebloater(features={"Variant_A"}))
    assert modified.code == expected

def test_preserve_indents_function():
    input = \
"""
if (a > 0):
    if (b == 1):
        ###[Variant_A]
        def closure(c):
            return c + a
"""
    expected = \
"""
if (a > 0):
    if (b == 1):
        ### Function Debloated

"""
    module = cst.parse_module(input)
    modified = module.visit(PythonImplicitDebloater(features={"Variant_A"}))
    assert modified.code == expected

def test_preserve_indents_statement():
    input = \
"""
if (a > 0):
    if (b == 1):
        ###[Variant_A]
        return c + a
"""
    expected = \
"""
if (a > 0):
    if (b == 1):
        ### Statement Debloated

"""
    module = cst.parse_module(input)
    modified = module.visit(PythonImplicitDebloater(features={"Variant_A"}))
    assert modified.code == expected

def test_preserve_indents_if():
    input = \
"""
if (a > 0):
    if (b == 1):
        ###[Variant_A]
        if(a==b):
            print("a equals b")
        ###[Variant_A]
        else:
            print("a doesn't equal b")
        ###[Variant_A]
        if(a<b):
            print("a less than b")
"""
    expected = \
"""
if (a > 0):
    if (b == 1):
        if(a==b):
            ### If Statement Branch Debloated
        else:
            ### Else Statement Debloated
        ### If Statement Debloated

"""
    module = cst.parse_module(input)
    modified = module.visit(PythonImplicitDebloater(features={"Variant_A"}))
    assert modified.code == expected

def test_if_multine():
    input = \
    """
a = 1
###[Variant_A]
if a == 2 \\
    and a == 3:
    print("a is 2 or 3")
else:
    print(f"a is {a}")
    """
    expected = \
    """
a = 1
if a == 2 \\
    and a == 3:
    ### If Statement Branch Debloated
else:
    print(f"a is {a}")
    """
    module = cst.parse_module(input)
    modified = module.visit(PythonImplicitDebloater(features={"Variant_A"}))
    assert modified.code == expected
