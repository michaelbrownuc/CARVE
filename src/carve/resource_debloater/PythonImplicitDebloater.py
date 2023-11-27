"""
Python Implicit Annotation Debloater
"""

import re
import libcst as cst
import libcst.matchers as m

class PythonImplicitDebloater(cst.CSTTransformer):
    """Transformer for debloating Python code with implicit annotations"""

    def debloat_comment(comment_str: str) -> bool:
        """Return whether comment matches an implicit debloat annotation"""
        # TODO Only debloat if annotation matches
        return re.search("###\[.*\]~", comment_str) is not None

    def leave_FunctionDef(self, original_node: cst.FunctionDef, updated_node: cst.FunctionDef) -> cst.FunctionDef:
        """Debloat function if there is an implicit annotation directly before"""
        # TODO Preserve comments before annotation
        if len(original_node.leading_lines) > 0:
            last_line = original_node.leading_lines[-1]
            if m.matches(last_line, m.EmptyLine(comment=m.Comment(m.MatchIfTrue(PythonImplicitDebloater.debloat_comment)))):
                indent = last_line.indent
                return cst.EmptyLine(indent=indent, comment=cst.Comment("# Function Debloated"), newline=cst.Newline())
        return updated_node

    def leave_If(self, original_node: cst.If, updated_node: cst.If) -> cst.If:
        """Debloat If statement if there is an implicit annotation directly before

        Debloat entire If statement if there is no else, otherwise just debloat branch body
        """
        if len(original_node.leading_lines) > 0:
            last_line = original_node.leading_lines[-1]
            if m.matches(last_line, m.EmptyLine(comment=m.Comment(m.MatchIfTrue(PythonImplicitDebloater.debloat_comment)))):
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
        if len(original_node.leading_lines) > 0:
            last_line = original_node.leading_lines[-1]
            if m.matches(last_line, m.EmptyLine(comment=m.Comment(m.MatchIfTrue(PythonImplicitDebloater.debloat_comment)))):
                indent = last_line.indent
                # TODO fix indentation of replacement code
                return cst.EmptyLine(indent=indent, comment=cst.Comment("# Else Statement Debloated"), newline=cst.Newline())
        return updated_node
