"""Test cases for shared explicit debloating logic"""
from carve.resource_debloater.CResourceDebloater import CResourceDebloater

def test_explicit_c_segment():
    input = \
    """
///[Variant_TCP]~
MODBUS_API modbus_t* modbus_new_tcp(const char *ip_address, int port);
MODBUS_API int modbus_tcp_listen(modbus_t *ctx, int nb_connection);
MODBUS_API int modbus_tcp_accept(modbus_t *ctx, int *s);
///~
    """
    expected = \
    """
/// Segment Debloated.



    """
    debloater = CResourceDebloater(location="dummy", target_features={"Variant_TCP"})
    debloater.lines = input.split("\n")
    location = 1
    debloater.process_explicit_annotation(location)
    output = "\n".join(debloater.lines)
    assert output == expected
