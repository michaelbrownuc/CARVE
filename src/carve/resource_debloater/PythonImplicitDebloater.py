"""
Python Implicit Annotation Debloater
"""

import re
import libcst as cst
import libcst.matchers as m
from typing import Set
from carve.resource_debloater.ResourceDebloater import ResourceDebloater

class PythonImplicitDebloater(cst.CSTTransformer):
    """Transformer for debloating Python code with implicit annotations"""
    # TODO Preserve comments before annotation
    def __init__(self, features: Set[str]):
        self.features = features


    def debloat_comment(self, comment_str: str) -> bool:
        """Return whether the comment is an implicit annotation with valid features"""
        # determine if implicit annotation
        if re.search(r"^\s*###\[.*\]\s*$", comment_str) is not None:
            comment_features = ResourceDebloater.get_features(comment_str)
            # debloat if features in comment are subset of target debloated features
            return self.features.issuperset(comment_features)
        return False

    def leave_FunctionDef(self, original_node: cst.FunctionDef, updated_node: cst.FunctionDef) -> cst.FunctionDef:
        """Debloat function if there is an implicit annotation directly before"""
        if len(original_node.leading_lines) > 0:
            last_line = original_node.leading_lines[-1]
            if m.matches(last_line, m.EmptyLine(comment=m.Comment(m.MatchIfTrue(self.debloat_comment)))):
                indent = last_line.indent
                return cst.EmptyLine(indent=indent, comment=cst.Comment("# Function Debloated"), newline=cst.Newline())
        return updated_node

    def leave_If(self, original_node: cst.If, updated_node: cst.If) -> cst.If:
        """Debloat If statement if there is an implicit annotation directly before

        Debloat entire If statement if there is no else, otherwise just debloat branch body
        """
        # TODO debloat annotation label too
        if len(original_node.leading_lines) > 0:
            last_line = original_node.leading_lines[-1]
            if m.matches(last_line, m.EmptyLine(comment=m.Comment(m.MatchIfTrue(self.debloat_comment)))):
                indent = last_line.indent
                # debloat entire statement if there is no else branch
                if original_node.orelse is None:
                    return cst.EmptyLine(indent=indent, comment=cst.Comment("# If Statement Debloated"), newline=cst.Newline())
                else:
                    # TODO fix indentation of replacement code
                    modified_node = updated_node.with_deep_changes(updated_node.body, body=[cst.EmptyLine(indent=indent, comment=cst.Comment("# If Statement Branch Debloated"), newline=cst.Newline())])
                    return modified_node

        return updated_node

    def leave_Else(self, original_node: cst.Else, updated_node: cst.Else) -> cst.Else:
        """Debloat Else statement"""
        # TODO debloat annotation label too
        if len(original_node.leading_lines) > 0:
            last_line = original_node.leading_lines[-1]
            if m.matches(last_line, m.EmptyLine(comment=m.Comment(m.MatchIfTrue(self.debloat_comment)))):
                indent = last_line.indent
                # TODO fix indentation of replacement code
                modified_node = updated_node.with_deep_changes(updated_node.body, body=[cst.EmptyLine(indent=indent, comment=cst.Comment("# Else Statement Debloated"), newline=cst.Newline())])
                return modified_node
        return updated_node

    def leave_SimpleStatementLine(self, original_node: cst.SimpleStatementLine, updated_node: cst.SimpleStatementLine) -> cst.SimpleStatementLine:
        """Debloat single statement"""
        if len(original_node.leading_lines) > 0:
            last_line = original_node.leading_lines[-1]
            if m.matches(last_line, m.EmptyLine(comment=m.Comment(m.MatchIfTrue(self.debloat_comment)))):
                indent = last_line.indent
                return cst.EmptyLine(indent=indent, comment=cst.Comment("# Statement Debloated"), newline=cst.Newline())
        return updated_node

    def leave_Module(self, original_node: cst.Module, updated_node: cst.Module) -> cst.Module:
        """Debloat first statement in Module

        This function is necessary because libcst stores the leading comments in a module in the module.header field, not the
        node.leading_lines field as usual. If the very first statement is annotated, then this method will debloat it.
        """
        if len(original_node.header) > 0:
            last_line = original_node.header[-1]
            if m.matches(last_line, m.EmptyLine(comment=m.Comment(m.MatchIfTrue(self.debloat_comment)))):
                indent = last_line.indent
                # remove first statement and last line of header (annotation comment)
                comment_line = cst.EmptyLine(indent=indent, comment=cst.Comment("# Statement Debloated"), newline=cst.Newline())
                modified_body = list(original_node.body[1:])
                modified_body.insert(0, comment_line)
                modified_header = original_node.header[:-1]
                modified_node = updated_node.with_changes(body=modified_body, header=modified_header)
                return modified_node
        return updated_node
