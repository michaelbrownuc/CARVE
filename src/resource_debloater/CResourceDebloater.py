"""
C Resource Debloater
"""

# Standard Library Imports
import logging
import re
import sys

# Third Party Imports

# Local Imports
from resource_debloater.ResourceDebloater import ResourceDebloater


class CResourceDebloater(ResourceDebloater):
    """
    This class implements a resource debloater for the C language.  It currently supports debloating the following types
    of explicit mappings (which are actually language agnostic):
        Debloating the entire file (file still exists, but contains no code)
        Debloating specified segments of code, with or without replacement
    
    It also supports the following C-specific implicit mappings:
            If / else if / else
            function definition
            statement
            cases in a switch statement (aware of fall through mechanics)
    """

    def __init__(self, location, target_features):
        """
        CResourceDebloater constructor
        :param str location: Filepath of the file on disk to debloat.
        :param set target_features: List of features to be debloated from the file.
        """
        super(CResourceDebloater, self).__init__(location, target_features)
        
        # If you desire to use a different mapping sequence, it can be adjusted here.
        self.annotation_sequence = "///["

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

    @staticmethod
    def get_construct(line):
        """
        Returns a string detailing the construct found at the line number.  Currently supports identifying the following
        constructs:
            Function definitions
            Switch cases
            Execution branches (if, else if, else)
            Individual statements

        :param str line: line of code immediately following an annotation
        :return:
        """
        
        if re.search("case\s\s*\w\w*\s*:\w*", line.strip()) is not None:
            return "Case"
        elif re.search("\selse\s\s*if\s*(\s*\S*\s*)", " " + line.strip()) is not None:
            return "ElseIfBranch"
        elif re.search("\sif\s*(\s*\S*\s*)", " " + line.strip()) is not None:
            return "IfBranch"
        elif re.search("\selse\s*{*", " " + line.strip()) is not None:
            return "ElseBranch"
        elif re.search("\w\w*\s\s*\w\w*\s*(\s*\S*\s*)\s*{*", line.strip()) is not None:
            return "FunctionStructDefinition"
        else:
            return "Statement"

    def process_annotation(self, annotation_line):
        """
        Processes an implicit or explicit (! and ~) debloating operation annotated at the specified line.

        This debloating module operates largely on a line by line basis. It does NOT support all types of source code
        authoring styles. Many code authoring styles are not supported and will cause errors in debloating. 

        Not Supported: Implicit annotations must be immediately preceding the construct to debloat.  There cannot
        be empty lines, comments, or block comments between the annotation and the construct.

        Not Supported: This processor assumes that all single statement debloating operations can remove the line
        wholesale. Multi-line statements will not be completely debloated.

        Not Supported: This processor assumes all execution branch statements have the entire condition expressed on
        the same line as the keyword.

        Not Supported: This processor expects all branches to be enclosed in braces, single statement blocks will cause
        errors.

        :param int annotation_line: Line where annotation to be processed is located.
        :return: None
        """
        # Check the annotation line for explicit cues ! and ~
        last_char = self.lines[annotation_line].strip()[-1]
        if last_char == "!":
            self.lines = []
            self.lines.append("///File Debloated.\n")
            self.lines.append("\n")
        elif last_char == "~":
            segment_end = None
            search_line = annotation_line + 1
            replacement_code = []

            # Check for replacement code following the segment debloat annotation.  If found, remove and store for later
            if self.lines[search_line].find("///^") > -1:
                self.lines.pop(search_line)

                while self.lines[search_line].find("///^") < 0:
                    replacement_code.append(self.lines.pop(search_line).replace("///", ""))

                self.lines.pop(search_line)

            while search_line < len(self.lines):
                if self.lines[search_line].find("///~") > -1:
                    segment_end = search_line
                    break
                else:
                    search_line += 1

            if segment_end is None:
                logging.error("No termination annotation found for segment annotation on line " + str(annotation_line) +
                              ".  Marking location and skipping this annotation.")
                self.lines.insert(annotation_line+1, "/// Segment NOT removed due to lack of termination annotation.\n")
            else:
                while segment_end != annotation_line:
                    self.lines.pop(segment_end)
                    segment_end -= 1
                self.lines[annotation_line] = "/// Segment Debloated.\n"
                self.lines.insert(annotation_line + 1, "\n")

                # Insert replacement code if it exists
                if len(replacement_code) > 0:
                    insert_point = 2
                    self.lines.insert(annotation_line + insert_point, "/// Code Inserted:\n")
                    insert_point += 1

                    for replacement_line in replacement_code:
                        self.lines.insert(annotation_line + insert_point, replacement_line)
                        insert_point += 1

                    self.lines.insert(annotation_line + insert_point, "\n")

        # If not explicit, look at next line to determine the implicit cue
        else:
            construct_line = annotation_line + 1
            construct = CResourceDebloater.get_construct(self.lines[construct_line])

            # Process implicit annotation based on construct identified
            if construct == "FunctionStructDefinition" or construct == "ElseBranch":
                # Function definitions, struct definitions, else branches are simple block removals.
                search_line = construct_line
                open_brace_counted = False
                brace_count = 0
                block_end = None

                while search_line < len(self.lines):
                    brace_count += self.lines[search_line].count("{")

                    if open_brace_counted is False and brace_count > 0:
                        open_brace_counted = True

                    brace_count -= self.lines[search_line].count("}")

                    if open_brace_counted is True and brace_count == 0:
                        block_end = search_line
                        break
                    else:
                        search_line += 1

                if block_end is None:
                    logging.error("Error finding end of code block annotated on line " + str(annotation_line) +
                                  ".  Marking location and skipping this annotation.")
                    self.lines.insert(annotation_line + 1,
                                      "/// Block NOT removed due to lack of termination brace.\n")
                else:
                    while block_end != annotation_line:
                        self.lines.pop(block_end)
                        block_end -= 1
                    self.lines[annotation_line] = "/// Code Block Debloated.\n"
                    self.lines.insert(annotation_line + 1, " \n")

            elif construct == "IfBranch" or construct == "ElseIfBranch":
                # Removing an If or and Else If branch can result in inadvertent execution of an else block if they are
                # removed entirely. To debloat these constructs, the condition check should remain in the source code
                # to ensure sound operation of the debloated code. Ultimately, the condition check will more than likely
                # be eliminated by the compiler, so modifying the conditions in source is unnecessarily dangerous.

                # Function definitions, struct definitions, else branches are simple block removals.
                search_line = construct_line
                open_brace_counted = False
                brace_count = 0
                block_end = None
                open_brace_line = None

                while search_line < len(self.lines):
                    brace_count += self.lines[search_line].count("{")

                    if open_brace_counted is False and brace_count > 0:
                        open_brace_counted = True
                        open_brace_line = search_line

                    brace_count -= self.lines[search_line].count("}")

                    if open_brace_counted is True and brace_count == 0:
                        block_end = search_line
                        break
                    else:
                        search_line += 1

                if block_end is None:
                    logging.error("Error finding end of code block annotated on line " + str(annotation_line) +
                                  ".  Marking location and skipping this annotation.")
                    self.lines.insert(annotation_line + 1,
                                      "/// Block NOT removed due to lack of termination brace.\n")
                else:
                    # Remove the code on line after open curly brace, and before the closing curly brace.
                    # Need this in case the braces aren't on their own line.
                    # Remove lines in bedtween the open and close curly brace.
                    block_end -= 1
                    open_brace_line += 1
                    while block_end != open_brace_line:
                        self.lines.pop(block_end)
                        block_end -= 1
                    self.lines[annotation_line] = "/// If / Else If Code Block Debloated.\n"

            elif construct == "Case":
                # Removing a case statement requires checking for fall through logic:
                # If the previous case has a break, the case be removed.
                # If the previous case doesn't have a break, then only the case label can be removed.

                # Search backwards from the annotation, see if a break or a case is found first.
                search_line = annotation_line - 1
                previous_break = None

                while search_line >= 0:
                    if re.search("\sbreak\s*;", " " + self.lines[search_line].strip()) is not None or \
                       re.search("\sswitch\s*(\s*\S*\s*)\s*{*", " " + self.lines[search_line].strip()) is not None:
                        previous_break = True
                        break
                    elif re.search("case\s\s*\w\w*\s*:\w*", self.lines[search_line].strip()) is not None:
                        previous_break = False
                        break
                    else:
                        search_line -= 1

                # Log an error and skip if switch statement behavior cannot be determined
                if previous_break is None:
                    logging.error("Error finding previous case or switch for case on line " + str(annotation_line) +
                                  ".  Marking location and skipping this annotation.")
                    self.lines.insert(annotation_line + 1,
                                      "/// Case NOT removed due to lack of switch or previous case.\n")

                # If previous case has fall through logic, only the case label can be deleted.
                elif previous_break is False:
                    self.lines[annotation_line] = "/// Case Label Debloated.\n"
                    self.lines[construct_line] = "\n"

                # If the previous case does not have fall through logic, then search for next break, case, or default
                elif previous_break is True:
                    case_end = None
                    search_line = construct_line + 1
                    brace_count = self.lines[construct_line].count("{")

                    while search_line < len(self.lines):
                        brace_count += self.lines[search_line].count("{")
                        brace_count -= self.lines[search_line].count("}")

                        if re.search("case\s\s*\w\w*\s*:\w*", self.lines[search_line].strip()) is not None or \
                           re.search("default\s\s*\w\w*\s*:\w*", self.lines[search_line].strip()) is not None or \
                           brace_count < 0:
                            case_end = search_line - 1

                            # Check that the line before the next case (or default) isn't a debloating annotation.
                            if self.lines[case_end].find(self.annotation_sequence) > -1:
                                case_end -= 1
                            break
                        elif re.search("\sbreak\s*;", " " + self.lines[search_line].strip()) is not None:
                            case_end = search_line
                            break
                        else:
                            search_line += 1

                    if case_end is None:
                        logging.error("No end of switch block found for case annotation on line " + str(annotation_line)
                                      + ".  Marking location and skipping this annotation.")
                        self.lines.insert(annotation_line + 1,
                                          "/// Case block NOT removed due to failure to identify end of block.\n")
                    else:
                        while case_end != annotation_line:
                            self.lines.pop(case_end)
                            case_end -= 1
                        self.lines[annotation_line] = "/// Case Block Debloated.\n"
                        self.lines.insert(annotation_line + 1, " \n")

            elif construct == "Statement":
                self.lines[annotation_line] = "/// Statement Debloated.\n"
                self.lines[construct_line] = "\n"
            else:
                # Log error and exit
                logging.error("Unexpected construct encountered when processing implicit annotation.  Exiting.")
                sys.exit("Unexpected construct encountered when processing implicit annotation.  Exiting.")

    def debloat(self):
        """
        Iterates through the file and debloats the selected features subject to dependency constraints
        :return: None
        """
        logging.info("Beginning debloating pass on " + self.location)

        # Search the source code for debloater annotations, and process them.
        current_line = 0

        while current_line < len(self.lines):
            if self.lines[current_line].find(self.annotation_sequence) > -1:
                logging.info("Annotation found on line " + str(current_line))

                feature_set = CResourceDebloater.get_features(self.lines[current_line])

                if self.target_features.issuperset(feature_set):
                    logging.info("Processing annotation found on line " + str(current_line))
                    self.process_annotation(current_line)
            current_line += 1
