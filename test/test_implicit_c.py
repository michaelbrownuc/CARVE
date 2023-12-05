"""Test C Debloater"""
from carve.resource_debloater.CResourceDebloater import CResourceDebloater


def test_if_single():
    input = \
"""
///[Variant_A]
if (condition == 1) {
    fprintf(stderr, "Condition is one.\\n");
}
else if (condition == 1) {
    fprintf(stderr, "Condition is two.\\n");
}
else {
    fprintf(stderr, "Condition is something else.\\n");
}
"""
    expected = \
"""
/// If / Else If Code Block Debloated.
if (condition == 1) {
}
else if (condition == 1) {
    fprintf(stderr, "Condition is two.\\n");
}
else {
    fprintf(stderr, "Condition is something else.\\n");
}
"""
    debloater = CResourceDebloater(location="dummy", target_features={"Variant_A"})
    debloater.lines = input.splitlines(keepends=True)
    location = 1
    debloater.process_implicit_annotation(location)
    output = "".join(debloater.lines)
    assert output == expected


def test_if_brace_break():
    input = \
"""
///[Variant_A]
if (condition == 1)
{
    fprintf(stderr, "Condition is one.\\n");
}
else if (condition == 1) {
    fprintf(stderr, "Condition is two.\\n");
}
else {
    fprintf(stderr, "Condition is something else.\\n");
}
"""
    expected = \
"""
/// If / Else If Code Block Debloated.
if (condition == 1)
{
}
else if (condition == 1) {
    fprintf(stderr, "Condition is two.\\n");
}
else {
    fprintf(stderr, "Condition is something else.\\n");
}
"""
    debloater = CResourceDebloater(location="dummy", target_features={"Variant_A"})
    debloater.lines = input.splitlines(keepends=True)
    location = 1
    debloater.process_implicit_annotation(location)
    output = "".join(debloater.lines)
    assert output == expected

def test_if_multiline():
    input = \
"""
///[Variant_A]
if (condition == 1) {
    fprintf(stderr, "Condition is one.\\n");
    fprintf(stderr, "Condition is not zero.\\n");
    fprintf(stderr, "Condition is not two.\\n");
}
else if (condition == 1) {
    fprintf(stderr, "Condition is two.\\n");
}
else {
    fprintf(stderr, "Condition is something else.\\n");
}
"""
    expected = \
"""
/// If / Else If Code Block Debloated.
if (condition == 1) {
}
else if (condition == 1) {
    fprintf(stderr, "Condition is two.\\n");
}
else {
    fprintf(stderr, "Condition is something else.\\n");
}
"""
    debloater = CResourceDebloater(location="dummy", target_features={"Variant_A"})
    debloater.lines = input.splitlines(keepends=True)
    location = 1
    debloater.process_implicit_annotation(location)
    output = "".join(debloater.lines)
    assert output == expected

def test_if_else_multiline():
    input = \
"""
if (condition == 1) {
    fprintf(stderr, "Condition is one.\\n");
}
///[Variant_A]
else if (condition == 1) {
    fprintf(stderr, "Condition is two.\\n");
    fprintf(stderr, "Condition is not one.\\n");
    fprintf(stderr, "Condition is not something else.\\n");
}
else {
    fprintf(stderr, "Condition is something else.\\n");
}
"""
    expected = \
"""
if (condition == 1) {
    fprintf(stderr, "Condition is one.\\n");
}
/// If / Else If Code Block Debloated.
else if (condition == 1) {
}
else {
    fprintf(stderr, "Condition is something else.\\n");
}
"""
    debloater = CResourceDebloater(location="dummy", target_features={"Variant_A"})
    debloater.lines = input.splitlines(keepends=True)
    location = 4
    debloater.process_implicit_annotation(location)
    output = "".join(debloater.lines)
    assert output == expected


def test_if_nested():
    input = \
"""
///[Variant_A]
if (condition == 1) {
    fprintf(stderr, "Condition is one.\\n");
    if (condition == 1) {
        fprintf(stderr, "Condition is one.\\n");
    }
}
else if (condition == 1) {
    fprintf(stderr, "Condition is two.\\n");
}
else {
    fprintf(stderr, "Condition is something else.\\n");
}
"""
    expected = \
"""
/// If / Else If Code Block Debloated.
if (condition == 1) {
}
else if (condition == 1) {
    fprintf(stderr, "Condition is two.\\n");
}
else {
    fprintf(stderr, "Condition is something else.\\n");
}
"""
    debloater = CResourceDebloater(location="dummy", target_features={"Variant_A"})
    debloater.lines = input.splitlines(keepends=True)
    location = 1
    debloater.process_implicit_annotation(location)
    output = "".join(debloater.lines)
    assert output == expected


def test_func_def():
    input = \
"""
// sample from sample/libmodbus/src/modbus-tcp.c
///[Variant_A]
static int _modbus_tcp_select(modbus_t *ctx, fd_set *rset, struct timeval *tv, int length_to_read)
{
    int s_rc;
    while ((s_rc = select(ctx->s+1, rset, NULL, NULL, tv)) == -1) {
        if (errno == EINTR) {
            if (ctx->debug) {
                fprintf(stderr, "A non blocked signal was caught\n");
            }
            /* Necessary after an error */
            FD_ZERO(rset);
            FD_SET(ctx->s, rset);
        } else {
            return -1;
        }
    }

    if (s_rc == 0) {
        errno = ETIMEDOUT;
        return -1;
    }

    return s_rc;
}
"""
    expected = \
"""
// sample from sample/libmodbus/src/modbus-tcp.c
/// Code Block Debloated.

"""
    debloater = CResourceDebloater(location="dummy", target_features={"Variant_A"})
    debloater.lines = input.splitlines(keepends=True)
    location = 2
    debloater.process_implicit_annotation(location)
    output = "".join(debloater.lines)
    assert output == expected
