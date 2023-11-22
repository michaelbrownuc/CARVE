"""
Python Resource Debloater
"""

# Standard Library Imports
import logging
import re

# Third Party Imports
import libcst as cst
import libcst.matchers as m
# Local Imports
from resource_debloater.ResourceDebloater import ResourceDebloater

class PythonImplicitDebloater(cst.CSTTransformer):
    """Transformer for debloating Python code with implicit annotations"""

    def debloat_comment(comment_str: str) -> bool:
        # TODO Only debloat if annotation matches
        return re.search("###\[.*\]~", comment_str) is not None

    def leave_FunctionDef(self, original_node: cst.FunctionDef, updated_node: cst.FunctionDef) -> cst.FunctionDef:
        # debloat function if the comment directly before it is an annotation
        # TODO Preserve comments before annotation
        if len(original_node.leading_lines) > 0:
            last_line = original_node.leading_lines[-1]
            if m.matches(last_line, m.EmptyLine(comment=m.Comment(m.MatchIfTrue(PythonImplicitDebloater.debloat_comment)))):
                indent = last_line.indent
                return cst.EmptyLine(indent=indent, comment=cst.Comment("# Function Debloated"), newline=cst.Newline())
        return updated_node

class PythonResourceDebloater(ResourceDebloater):
    """
    This class implements a resource debloater for the Python language.
    """

    def __init__(self, location, target_features):
        """
        PythonResourceDebloater constructor
        :param str location: Filepath of the file on disk to debloat.
        :param set target_features: List of features to be debloated from the file.
        """
        super(PythonResourceDebloater, self).__init__(location, target_features)

        # If you desire to use a different mapping sequence, it can be adjusted here.
        self.annotation_sequence = "###["
        self.module = None

    @staticmethod
    def get_features(line):
        """
        Returns a set of features specified in the annotation.
        :param str line: line of code containing an annotation.
        :return: A set of the features specified in the annotation.
        """
        feature_list = line.split("][")

        first_trim_point = feature_list[0].find("[") + 1
        feature_list[0] = feature_list[0][first_trim_point:]

        last_trim_point = feature_list[len(feature_list)-1].find("]")
        feature_list[len(feature_list)-1] = feature_list[len(feature_list)-1][:last_trim_point]

        return set(feature_list)

    def process_annotation(self, annotation_line):
        """
        Processes an implicit or explicit (! and ~) debloating operation annotated at the specified line.
        :param int annotation_line: Line where annotation to be processed is located.
        :return: None
        """
        raise NotImplementedError

    def read_from_disk(self):
        """
        Reads the file from disk and parses a Concrete Syntax Tree
        :return: None
        """
        with open(self.location, 'r') as f:
            self.module = cst.parse_module(f.read())

    def write_to_disk(self):
        """
        Replace the file on disk with the new debloated file.
        :return: None
        """
        with open(self.location, 'w') as f:
            f.write(self.module.code)

    def debloat(self):
        """
        Iterates through the file and debloats the selected features subject to dependency constraints
        :return: None
        """
        logging.info(f"Beginning debloating pass on {self.location}")
        modified = self.module.visit(PythonImplicitDebloater())
        self.module = modified
