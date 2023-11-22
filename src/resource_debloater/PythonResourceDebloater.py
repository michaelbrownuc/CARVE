"""
Python Resource Debloater
"""

# Standard Library Imports
import logging

# Third Party Imports
import libcst as cst
# Local Imports
from resource_debloater.ResourceDebloater import ResourceDebloater


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
        self.annotation_sequence = "##["
        self.tree = None

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
            self.tree = cst.parse_module(f.read())

    def write_to_disk(self):
        """
        Replace the file on disk with the new debloated file.
        :return: None
        """
        with open(self.location, 'w') as f:
            f.write(self.tree.code)

    def debloat(self):
        """
        Iterates through the file and debloats the selected features subject to dependency constraints
        :return: None
        """
        logging.info(f"Beginning debloating pass on {self.location}")
