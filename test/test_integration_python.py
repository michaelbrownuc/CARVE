"""Integrations tests for Python debloating"""
from carve.resource_debloater.PythonResourceDebloater import PythonResourceDebloater
import libcst as cst
def test_if_integration():
    input = \
    """
a = 1
###[Variant_A][Variant_B]
if a:
    a += 1
    print(a)
###[Variant_C]~
else:
    print(b)
###~
a = 2
    """
    expected = \
    """
a = 1
### If Statement Debloated

### Segment Debloated.

a = 2
    """
    debloater = PythonResourceDebloater(location="dummy",target_features={"Variant_A", "Variant_B", "Variant_C"})
    debloater.module = cst.parse_module(input)
    debloater.debloat()
    assert debloater.module.code == expected
