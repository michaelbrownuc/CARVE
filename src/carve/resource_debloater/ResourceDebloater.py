"""
Resource Debloater
"""

# Standard Library Imports
import logging
import os
import sys
from pathlib import Path
from typing import Set

# Third Party Imports

# Local Imports


class ResourceDebloater(object):
    """
    The primary purpose of the ResourceDebloater class is to serve as a parent class for language specific file
    debloaters that can be instantiated in this project.  It provides the basic interface necessary for instantiating a
    resource debloater and handles common tasks such as reading the file from disk into a data structure.
    """

    def __init__(self, location: Path, target_features: Set[str]):
        """
        ResourceDebloater constructor
        :param str location: Filepath of the file on disk to debloat.
        :param set target_features: List of features to be debloated from the file.
        """

        self.location = location
        self.target_features = target_features
        self.lines = []
        self.annotation_sequence = None

    def read_from_disk(self) -> None:
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

    def write_to_disk(self) -> None:
        """
        Replace the file on disk with the new debloated file.
        :return: None
        """
        logging.info(f"Writing debloated version of {self.location} to disk.")
        file = open(self.location, "w")
        file.writelines(self.lines)
        file.close()

    @staticmethod
    def get_features(line: str) -> Set[str]:
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

    def process_explicit_annotation(self, annotation_line: int) -> None:
        """
        Process annotation if explicit (! or ~)

        Explicit annotations are debloated as a group of lines. File annotations (!) debloat all lines.
        Segment annotations (~) debloat all lines between an opening and closing explicit annotation.

        :param int annotation_line: Line where annotation to be processed is located.
        :return: None
        """

        last_char = self.lines[annotation_line].strip()[-1]
        # debloat full file
        if last_char == "!":
            self.lines = []
            self.lines.append(f"{self.annotation_sequence}File Debloated.\n")
            self.lines.append("\n")
        # debloat segment
        elif last_char == "~":
            segment_end = None
            search_line = annotation_line + 1
            replacement_code = []

            # Check for replacement code following the segment debloat annotation.  If found, remove and store for later
            if self.lines[search_line].find(f"{self.annotation_sequence}^") > -1:
                self.lines.pop(search_line)

                while self.lines[search_line].find(f"{self.annotation_sequence}^") < 0:
                    replacement_code.append(self.lines.pop(search_line).replace(self.annotation_sequence, ""))

                self.lines.pop(search_line)

            while search_line < len(self.lines):
                if self.lines[search_line].find(f"{self.annotation_sequence}~") > -1:
                    segment_end = search_line
                    break
                else:
                    search_line += 1

            if segment_end is None:
                logging.error("No termination annotation found for segment annotation on line " + str(annotation_line) +
                              ".  Marking location and skipping this annotation.")
                self.lines.insert(annotation_line+1, f"{self.annotation_sequence} Segment NOT removed due to lack of termination annotation.\n")
            else:
                while segment_end != annotation_line:
                    self.lines.pop(segment_end)
                    segment_end -= 1
                self.lines[annotation_line] = f"{self.annotation_sequence} Segment Debloated.\n"
                self.lines.insert(annotation_line + 1, "\n")

                # Insert replacement code if it exists
                if len(replacement_code) > 0:
                    insert_point = 2
                    self.lines.insert(annotation_line + insert_point, f"{self.annotation_sequence} Code Inserted:\n")
                    insert_point += 1

                    for replacement_line in replacement_code:
                        self.lines.insert(annotation_line + insert_point, replacement_line)
                        insert_point += 1

                    self.lines.insert(annotation_line + insert_point, "\n")
        else:
            logging.error("Tried to debloat annotation that isn't explicit" + str(annotation_line) +
                            ".  Marking location and skipping this annotation.")
            self.lines.insert(annotation_line+1, f"{self.annotation_sequence} Segment NOT removed because unexpectedly not explicit annotation.\n")
