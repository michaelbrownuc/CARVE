"""
Resource Debloater
"""

# Standard Library Imports
import logging
import os
import sys
from pathlib import Path

# Third Party Imports

# Local Imports


class ResourceDebloater(object):
    """
    The primary purpose of the ResourceDebloater class is to serve as a parent class for language specific file
    debloaters that can be instantiated in this project.  It provides the basic interface necessary for instantiating a
    resource debloater and handles common tasks such as reading the file from disk into a data structure.
    """

    def __init__(self, location: Path, target_features):
        """
        ResourceDebloater constructor
        :param str location: Filepath of the file on disk to debloat.
        :param set target_features: List of features to be debloated from the file.
        """

        self.location = location
        self.target_features = target_features
        self.lines = []

    def read_from_disk(self):
        """
        Reads the file from disk, saving each line into the object's internal representation
        :return: None
        """
        logging.info(f"Reading {self.location} from disk")
        file = open(self.location, "r")
        self.lines = file.readlines()
        file.close()

    def debloat(self):
        """
        Defined as an abstract method.  Logs error and exits if invoked, as derived classes of ResourceDebloater should
        implement this function.
        """
        logging.error("No debloater defined, interface debloater was invoked.  Aborting.")
        sys.exit("No debloater defined, interface debloater was invoked.  Aborting.")

    def write_to_disk(self):
        """
        Replace the file on disk with the new debloated file.
        :return: None
        """
        logging.info(f"Writing debloated version of {self.location} to disk.  Removing old version.")
        os.remove(self.location)
        file = open(self.location, "w")
        file.writelines(self.lines)
        file.close()
