"""Test C Debloater

Some code inputs are from the libmodus project in sample/libmodbus
"""
from carve.resource_debloater.CResourceDebloater import CResourceDebloater


def test_if_single():
    input = \
"""
///[Variant_A]
if (condition == 1) {
    fprintf(stderr, "Condition is one.\\n");
}
else if (condition == 2) {
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
else if (condition == 2) {
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
else if (condition == 2) {
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
else if (condition == 2) {
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
else if (condition == 2) {
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
else if (condition == 2) {
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
else if (condition == 2) {
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
else if (condition == 2) {
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
else if (condition == 2) {
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
else if (condition == 2) {
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

def test_if_condition_multiline():
    input = \
"""
///[Variant_A]
if (condition == 1 ||
    condition < 2 ||
    condition > 0) {
    fprintf(stderr, "Condition is one.\\n");
}
else if (condition == 2) {
    fprintf(stderr, "Condition is two.\\n");
}
"""
    expected = \
"""
/// If / Else If Code Block Debloated.
if (condition == 1 ||
    condition < 2 ||
    condition > 0) {
}
else if (condition == 2) {
    fprintf(stderr, "Condition is two.\\n");
}
"""
    debloater = CResourceDebloater(location="dummy", target_features={"Variant_A"})
    debloater.lines = input.splitlines(keepends=True)
    location = 1
    debloater.process_implicit_annotation(location)
    output = "".join(debloater.lines)
    assert output == expected

def test_if_else_condition_multiline():
    input = \
"""
if (condition == 1) {
    fprintf(stderr, "Condition is one.\\n");
}
///[Variant_A]
else if (condition == 2 &&
        condition > 1 &&
        condition < 3) {
    fprintf(stderr, "Condition is two.\\n");
}
"""
    expected = \
"""
if (condition == 1) {
    fprintf(stderr, "Condition is one.\\n");
}
/// If / Else If Code Block Debloated.
else if (condition == 2 &&
        condition > 1 &&
        condition < 3) {
}
"""
    debloater = CResourceDebloater(location="dummy", target_features={"Variant_A"})
    debloater.lines = input.splitlines(keepends=True)
    location = 4
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

def test_else():
    input = \
"""
if (a == b) {
    fprintf(stderr, "a equals b\\n");
}
///[Variant_A]
else {
    return -1;
}
"""
    expected = \
"""
if (a == b) {
    fprintf(stderr, "a equals b\\n");
}
/// Code Block Debloated.

"""
    debloater = CResourceDebloater(location="dummy", target_features={"Variant_A"})
    debloater.lines = input.splitlines(keepends=True)
    location = 4
    debloater.process_implicit_annotation(location)
    output = "".join(debloater.lines)
    assert output == expected

def test_else_one_line():
    input = \
"""
if (a == b) {
    fprintf(stderr, "a equals b\\n");
}
///[Variant_A]
else { return -1; }
"""
    expected = \
"""
if (a == b) {
    fprintf(stderr, "a equals b\\n");
}
/// Code Block Debloated.

"""
    debloater = CResourceDebloater(location="dummy", target_features={"Variant_A"})
    debloater.lines = input.splitlines(keepends=True)
    location = 4
    debloater.process_implicit_annotation(location)
    output = "".join(debloater.lines)
    assert output == expected


def test_struct_typedef():
    input = \
"""
///[Variant_A]
typedef struct _mystruct {
    int field_a;
    int field_b;
    int field_c;
} mystruct;
"""
    expected = \
"""
/// Code Block Debloated.

"""
    debloater = CResourceDebloater(location="dummy", target_features={"Variant_A"})
    debloater.lines = input.splitlines(keepends=True)
    location = 1
    debloater.process_implicit_annotation(location)
    output = "".join(debloater.lines)
    assert output == expected


def test_struct_standard():
    input = \
"""
///[Variant_A]
struct _mystruct
{
    int field_a;
    int field_b;
    int field_c;
};
"""
    expected = \
"""
/// Code Block Debloated.

"""
    debloater = CResourceDebloater(location="dummy", target_features={"Variant_A"})
    debloater.lines = input.splitlines(keepends=True)
    location = 1
    debloater.process_implicit_annotation(location)
    output = "".join(debloater.lines)
    assert output == expected

def test_case_label():
    input = \
"""
switch (switchval) {
    case CASE1:
        break;
    case CASE2:
    ///[Variant_A]
    case CASE3:
        fprintf(stderr, "case 3\\n");
        break;
}
"""
    expected = \
"""
switch (switchval) {
    case CASE1:
        break;
    case CASE2:
/// Case Label Debloated.

        fprintf(stderr, "case 3\\n");
        break;
}
"""
    debloater = CResourceDebloater(location="dummy", target_features={"Variant_A"})
    debloater.lines = input.splitlines(keepends=True)
    location = 5
    debloater.process_implicit_annotation(location)
    output = "".join(debloater.lines)
    assert output == expected


def test_case_body():
    input = \
"""
switch (switchval) {
    case CASE1:
    case CASE2:
        break;
    ///[Variant_A]
    case CASE3:
        fprintf(stderr, "case 3\\n");
        break;
    case CASE4:
}
"""
    expected = \
"""
switch (switchval) {
    case CASE1:
    case CASE2:
        break;
/// Case Block Debloated.

    case CASE4:
}
"""
    debloater = CResourceDebloater(location="dummy", target_features={"Variant_A"})
    debloater.lines = input.splitlines(keepends=True)
    location = 5
    debloater.process_implicit_annotation(location)
    output = "".join(debloater.lines)
    assert output == expected


def test_case_body_first():
    input = \
"""
switch (switchval) {
    ///[Variant_A]
    case CASE1:
    case CASE2:
        break;
    case CASE3:
        fprintf(stderr, "case 3\\n");
        break;
    case CASE4:
}
"""
    expected = \
"""
switch (switchval) {
/// Case Block Debloated.

    case CASE2:
        break;
    case CASE3:
        fprintf(stderr, "case 3\\n");
        break;
    case CASE4:
}
"""
    debloater = CResourceDebloater(location="dummy", target_features={"Variant_A"})
    debloater.lines = input.splitlines(keepends=True)
    location = 2
    debloater.process_implicit_annotation(location)
    output = "".join(debloater.lines)
    assert output == expected

def test_case_body_last():
    input = \
"""
switch (switchval) {
    case CASE1:
    case CASE2:
        break;
    case CASE3:
        fprintf(stderr, "case 3\\n");
        break;
    ///[Variant_A]
    case CASE4:
}
"""
    expected = \
"""
switch (switchval) {
    case CASE1:
    case CASE2:
        break;
    case CASE3:
        fprintf(stderr, "case 3\\n");
        break;
/// Case Block Debloated.

}
"""
    debloater = CResourceDebloater(location="dummy", target_features={"Variant_A"})
    debloater.lines = input.splitlines(keepends=True)
    location = 8
    debloater.process_implicit_annotation(location)
    output = "".join(debloater.lines)
    assert output == expected

def test_case_body_default():
    input = \
"""
switch (switchval) {
    case CASE1:
        break;
    ///[Variant_A]
    case CASE2:
        fprintf(stderr, "case 2\\n");
    default:
        fprintf(stderr, "default\\n");
}
"""
    expected = \
"""
switch (switchval) {
    case CASE1:
        break;
/// Case Block Debloated.

    default:
        fprintf(stderr, "default\\n");
}
"""
    debloater = CResourceDebloater(location="dummy", target_features={"Variant_A"})
    debloater.lines = input.splitlines(keepends=True)
    location = 4
    debloater.process_implicit_annotation(location)
    output = "".join(debloater.lines)
    assert output == expected

def test_simple_statement():
    input = \
"""
if (condition == 1)
{
    ///[Variant_A]
    fprintf(stderr, "Condition is one.\\n");
}
else {
    fprintf(stderr, "Condition is something else.\\n");
}
"""
    expected = \
"""
if (condition == 1)
{
/// Statement Debloated.

}
else {
    fprintf(stderr, "Condition is something else.\\n");
}
"""
    debloater = CResourceDebloater(location="dummy", target_features={"Variant_A"})
    debloater.lines = input.splitlines(keepends=True)
    location = 3
    debloater.process_implicit_annotation(location)
    output = "".join(debloater.lines)
    assert output == expected

def test_get_construct_statement():
    line = "fprintf(stderr, \"Condition is one.\\n\");"
    res = CResourceDebloater.get_construct(line)
    expected = "Statement"
    assert res == expected

def test_get_construct_if():
    line = "if (cfsetispeed(&tios, speed) < 0)"
    res = CResourceDebloater.get_construct(line)
    expected = "IfBranch"
    assert res == expected

def test_get_construct_struct():
    line = "struct _modbus {"
    res = CResourceDebloater.get_construct(line)
    expected = "StructDefinition"
    assert res == expected

def test_get_construct_func():
    line = "static int _modbus_rtu_pre_check_confirmation(modbus_t *ctx, const uint8_t *req, const uint8_t *rsp, int rsp_length)"
    res = CResourceDebloater.get_construct(line)
    expected = "FunctionDefinition"
    assert res == expected

def test_get_construct_case():
    line = "case MODBUS_FC_READ_DISCRETE_INPUTS: "
    res = CResourceDebloater.get_construct(line)
    expected = "Case"
    assert res == expected

def test_get_construct_else_if():
    line = "        else if (strcmp(argv[1], \"tcppi\") == 0) {"
    res = CResourceDebloater.get_construct(line)
    expected = "ElseIfBranch"
    assert res == expected

def test_get_construct_else():
    line = "    else {   "
    res = CResourceDebloater.get_construct(line)
    expected = "ElseBranch"
    assert res == expected

def test_get_construct_else_no_brace():
    line = "    else "
    res = CResourceDebloater.get_construct(line)
    expected = "ElseBranch"
    assert res == expected

def test_get_construct_no_match():
    line = "else if switch break case"
    res = CResourceDebloater.get_construct(line)
    expected = "Statement"
    assert res == expected
