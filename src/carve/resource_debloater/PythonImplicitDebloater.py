"""
Python Implicit Annotation Debloater
"""

import re
import libcst as cst
import libcst.matchers as m
from typing import Set, Union
from carve.resource_debloater.ResourceDebloater import ResourceDebloater
from libcst._nodes.internal import CodegenState
import logging

class EmptyLineStatement(cst.EmptyLine):
    """Modified EmptyLine node to be compatible with SimpleStatementLine."""

    def _codegen_impl(self, state: CodegenState, default_semicolon) -> None:
        """Original EmptyLine._codegen_impl(), with added argument default_semicolon

        The added argument makes this class compatible with SimpleStatementLine.body, because
        that field expects a Sequence[BaseSmallStatement]. A BaseSmallStatement has a
        default_semicolon argument in _codegen_impl()."""
        if self.indent:
            state.add_indent_tokens()
        self.whitespace._codegen(state)
        comment = self.comment
        if comment is not None:
            comment._codegen(state)
        self.newline._codegen(state)

class PythonImplicitDebloater(cst.CSTTransformer):
    """Transformer for debloating Python code with implicit annotations"""
    def __init__(self, features: Set[str]):
        self.features = features
        self.annotation_sequence = ResourceDebloater.PYTHON_ANNOTATION_SEQUENCE


    def debloat_comment(self, comment_str: str) -> bool:
        """Return whether the comment is an implicit annotation with valid features"""
        # determine if implicit annotation
        if re.search(f"^\\s*{self.annotation_sequence}\\[.*\\]\\s*$", comment_str) is not None:
            comment_features = ResourceDebloater.get_features(comment_str)
            # debloat if features in comment are subset of target debloated features
            return self.features.issuperset(comment_features)
        return False

    def node_is_annotated(self, node: Union[cst.FunctionDef, cst.If, cst.Else, cst.SimpleStatementLine]) -> bool:
        """Return whether node is immediately preceded by an annotation with valid tags"""
        if len(node.leading_lines) > 0:
            last_line = node.leading_lines[-1]
            return m.matches(last_line, m.EmptyLine(comment=m.Comment(m.MatchIfTrue(self.debloat_comment))))
        return False

    def leave_FunctionDef(self, original_node: cst.FunctionDef, updated_node: cst.FunctionDef) -> cst.FunctionDef:
        """Debloat function if there is an implicit annotation directly before"""
        if self.node_is_annotated(updated_node):
            new_leading_lines = updated_node.leading_lines[:-1]
            return cst.SimpleStatementLine(leading_lines=new_leading_lines, body=[EmptyLineStatement(indent=False, comment=cst.Comment(f"{self.annotation_sequence} Function Debloated"), newline=cst.Newline())])
        return updated_node

    def leave_If(self, original_node: cst.If, updated_node: cst.If) -> cst.If:
        """Debloat If statement if there is an implicit annotation directly before

        Debloat entire If statement if there is no else, otherwise just debloat branch body
        """
        if self.node_is_annotated(updated_node):
            new_leading_lines = updated_node.leading_lines[:-1]
            # debloat entire statement if there is no else branch
            if updated_node.orelse is None:
                return cst.SimpleStatementLine(leading_lines=new_leading_lines, body=[EmptyLineStatement(indent=False, comment=cst.Comment(f"{self.annotation_sequence} If Statement Debloated"), newline=cst.Newline())])
            else:
                modified_node = updated_node.with_deep_changes(updated_node.body, body=[cst.EmptyLine(comment=cst.Comment(f"{self.annotation_sequence} If Statement Branch Debloated"), newline=cst.Newline())])
                modified_node = modified_node.with_changes(leading_lines=new_leading_lines)
                return modified_node

        return updated_node

    def leave_Else(self, original_node: cst.Else, updated_node: cst.Else) -> cst.Else:
        """Debloat Else statement"""
        if self.node_is_annotated(updated_node):
            new_leading_lines = updated_node.leading_lines[:-1]
            modified_node = updated_node.with_deep_changes(updated_node.body, body=[cst.EmptyLine(comment=cst.Comment(f"{self.annotation_sequence} Else Statement Debloated"), newline=cst.Newline())])
            modified_node = modified_node.with_changes(leading_lines=new_leading_lines)
            return modified_node
        return updated_node

    def leave_SimpleStatementLine(self, original_node: cst.SimpleStatementLine, updated_node: cst.SimpleStatementLine) -> cst.SimpleStatementLine:
        """Debloat single statement"""
        if self.node_is_annotated(updated_node):
            new_leading_lines = updated_node.leading_lines[:-1]
            return updated_node.with_changes(body=[EmptyLineStatement(indent=False, comment=cst.Comment(f"{self.annotation_sequence} Statement Debloated"), newline=cst.Newline())], leading_lines=new_leading_lines)
        return updated_node

    def visit_Module(self, original_node: cst.Module):
        """Warn if there are any annotations at the beginning of module

        The Python debloater will ignore implicit annotations that are at the beginning of a file
        (before any line that isn't whitespace/comments). This is due to how the Python parser under
        the hood groups these comments with the module itself.
        """
        for line in original_node.header:
            if m.matches(line, m.EmptyLine(comment=m.Comment(m.MatchIfTrue(self.debloat_comment)))):
                logging.warning(f"Ignoring implicit annotation in header: {line.comment.value}")
        return original_node

    def leave_ClassDef(self, original_node: cst.ClassDef, updated_node: cst.ClassDef):
        """Debloat Class definition"""
        if self.node_is_annotated(updated_node):
            new_leading_lines = updated_node.leading_lines[:-1]
            return cst.SimpleStatementLine(leading_lines=new_leading_lines, body=[EmptyLineStatement(indent=False, comment=cst.Comment(f"{self.annotation_sequence} Class Definition Debloated"), newline=cst.Newline())])
        return updated_node
