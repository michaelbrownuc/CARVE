"""
Python Resource Debloater
"""

# Standard Library Imports
import logging
from typing import Set
import re

# Third Party Imports
import libcst as cst

# Local Imports
from carve.resource_debloater.ResourceDebloater import ResourceDebloater
from carve.resource_debloater.PythonImplicitDebloater import PythonImplicitDebloater

class PythonResourceDebloater(ResourceDebloater):
    """
    This class implements a resource debloater for the Python language.
    """

    def __init__(self, location: str, target_features: Set[str]):
        """
        PythonResourceDebloater constructor
        :param str location: Filepath of the file on disk to debloat.
        :param set target_features: List of features to be debloated from the file.
        """
        super(PythonResourceDebloater, self).__init__(location, target_features)

        # If you desire to use a different mapping sequence, it can be adjusted here.
        self.annotation_sequence = self.PYTHON_ANNOTATION_SEQUENCE
        self.module = None

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

    def debloat_explicit_comment(self, comment_str: str) -> bool:
        """Return whether the comment is an explicit annotation with only target features"""
        # determine if explicit annotation
        if re.search(f"^\\s*{self.annotation_sequence}\\[.*\\](~|!)\\s*$", comment_str) is not None:
            comment_features = PythonResourceDebloater.get_features(comment_str)
            # debloat if features in comment are subset of target debloated features
            return self.target_features.issuperset(comment_features)
        return False

    def debloat_explicit(self):
        """Debloat explicit annotations"""
        self.lines = self.module.code.splitlines(keepends=True)
        # Search the source code for explicit debloater annotations and process them.
        current_line = 0
        while current_line < len(self.lines):
            if self.debloat_explicit_comment(self.lines[current_line]):
                    logging.info("Processing annotation found on line " + str(current_line))
                    self.process_explicit_annotation(current_line)
            current_line += 1
        self.module = cst.parse_module("".join(self.lines))
        self.lines = []

    def debloat_implicit(self):
        """Debloat implicit annotations"""
        modified = self.module.visit(PythonImplicitDebloater(self.target_features))
        self.module = modified

    def debloat(self):
        """
        Debloats file based on target features

        Note: This first debloats explicit annotations, than makes a second pass debloating implicit annotations.
        :return: None
        """
        logging.info(f"Beginning debloating pass on {self.location}")
        self.debloat_explicit()
        self.debloat_implicit()
