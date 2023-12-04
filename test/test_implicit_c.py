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
