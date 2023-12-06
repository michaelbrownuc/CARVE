"""
C Resource Debloater
"""

# Standard Library Imports
import logging
import re
import sys

# Third Party Imports

# Local Imports
from carve.resource_debloater.ResourceDebloater import ResourceDebloater


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
    # Regex patterns for identifying constructs
    # They search a trimmed string and are ordered by precedence in get_construct
    # They err on the side of permissiveness, leaving it to the developer to write valid C.
    CASE_CONSTRUCT_PAT = r"case\s+\w+\s*:"
    ELSE_IF_CONSTRUCT_PAT = r"\selse\s+if\s*\("
    IF_CONSTRUCT_PAT = r"\sif\s*\("
    ELSE_CONSTRUCT_PAT = r"\selse($|\s*\{)"
    FUNC_CONSTRUCT_PAT = r"\w+\s+\w+\s*\(.*\)"
    STRUCT_CONSTRUCT_PAT = r"(^|\s+)struct\s+\w+"

    # Other regex patterns
    BREAK_PAT = r"\sbreak\s*;"
    SWITCH_PAT = r"\sswitch\s*\(.*\)"
    DEFAULT_PAT = r"default\s*:"

    def __init__(self, location, target_features):
        """
        CResourceDebloater constructor
        :param str location: Filepath of the file on disk to debloat.
        :param set target_features: List of features to be debloated from the file.
        """
        super(CResourceDebloater, self).__init__(location, target_features)
        
        # If you desire to use a different mapping sequence, it can be adjusted here.
        self.annotation_sequence = self.C_ANNOTATION_SEQUENCE

    @staticmethod
    def get_construct(line):
        """
        Returns a string detailing the construct found at the line number.  Currently supports identifying the following
        constructs:
            Function definitions
            Switch cases
            Execution branches (if, else if, else)
            Struct definitions
            Individual statements

        :param str line: line of code immediately following an annotation
        :return:
        """
        
        if re.search(CResourceDebloater.CASE_CONSTRUCT_PAT, line.strip()) is not None:
            return "Case"
        elif re.search(CResourceDebloater.ELSE_IF_CONSTRUCT_PAT, " " + line.strip()) is not None:
            return "ElseIfBranch"
        elif re.search(CResourceDebloater.IF_CONSTRUCT_PAT, " " + line.strip()) is not None:
            return "IfBranch"
        elif re.search(CResourceDebloater.ELSE_CONSTRUCT_PAT, " " + line.strip()) is not None:
            return "ElseBranch"
        elif re.search(CResourceDebloater.FUNC_CONSTRUCT_PAT, line.strip()) is not None:
            return "FunctionDefinition"
        elif re.search(CResourceDebloater.STRUCT_CONSTRUCT_PAT, line.strip()) is not None:
            return "StructDefinition"
        else:
            return "Statement"

    def process_annotation(self, annotation_line: int) -> None:
        """
        Processes an implicit or explicit (! and ~) debloating operation annotated at the specified line.

        This debloating module operates largely on a line by line basis. It does NOT support all types of source code
        authoring styles. Many code authoring styles are not supported and will cause errors in debloating. Specifically,
        the implicit module is style-sensitive. See the documentation of process_implicit_annotation for more.

        :param int annotation_line: Line where annotation to be processed is located.
        :return: None
        """
        # Check the annotation line for explicit cues ! and ~
        last_char = self.lines[annotation_line].strip()[-1]
        is_explicit_annotation = last_char in {"~", "!"}
        if is_explicit_annotation:
            self.process_explicit_annotation(annotation_line)
        else:
            self.process_implicit_annotation(annotation_line)


    def process_implicit_annotation(self, annotation_line: int) -> None:
            """Processes an implicit annotation

            The C implicit annotation processor expects a particular style. This is a list of what is not supported,
            although it is not exhaustive:

            Not Supported: Implicit annotations must be immediately preceding the construct to debloat. There cannot
            be empty lines, comments, or block comments between the annotation and the construct.

            Not Supported: This processor assumes that all single-statement debloating operations can remove the line
            wholesale. Multi-line statements will not be completely debloated.

            Not Supported: This processor expects all branches to be enclosed in braces. Single-statement blocks will cause
            errors.

            Not Supported: This processor expects annotations which only debloat the body of a construct (`if`, `else if`)
            to have the construct and body statements on separate lines. This annotation is invalid:
            ```
            ///[Variant_A]
            if (condition == 1) { fprintf(stderr, "Condition is one.\\n"); }
            ```
            Not Supported: Implicit annotations which are inside the braces of the previous statement. This annotation is invalid:
            ```
            if (condition == 1) {
                fprintf(stderr, "Condition is one.\\n");
            ///[Variant_A]
            } else if (condition == 1) {
                fprintf(stderr, "Condition is two.\\n");
            }
            ```
            Not Supported: Struct typedefs cannot extend past the line of the last brace. This annotation is invalid:
            ```
            typedef struct _mystruct
            {
            int field_a;
            }
            mystruct;
            ```
            Not Supported: Braces on the same line as case branches that can be debloated. The specific error is if a brace is on the same line
            as a case label and only the label is debloated, then there will be a dangling brace. This annotation will generate invalid code:
            ```
            switch (switchval) {
                case 1:
                ///[Variant_A]
                case 2: {
                    fprintf(stderr, "case 2\\n");
                }
            }
            ```
            Not Supported: Annotated implicit lines that have non-ASCII identifiers.
            """
            # Look at next line to determine the implicit construct
            construct_line = annotation_line + 1
            construct = CResourceDebloater.get_construct(self.lines[construct_line])

            # Process implicit annotation based on construct identified
            if construct == "FunctionDefinition" or construct == "StructDefinition" or construct == "ElseBranch":
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
                                      f"{self.annotation_sequence} Block NOT removed due to lack of termination brace.\n")
                else:
                    while block_end != annotation_line:
                        self.lines.pop(block_end)
                        block_end -= 1
                    self.lines[annotation_line] = f"{self.annotation_sequence} Code Block Debloated.\n"
                    self.lines.insert(annotation_line + 1, "\n")

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
                                      f"{self.annotation_sequence} Block NOT removed due to lack of termination brace.\n")
                else:
                    # Remove the code on line after open curly brace, and before the closing curly brace.
                    # Need this in case the braces aren't on their own line.
                    # Remove lines in bedtween the open and close curly brace.
                    block_end -= 1
                    while block_end != open_brace_line:
                        self.lines.pop(block_end)
                        block_end -= 1
                    self.lines[annotation_line] = f"{self.annotation_sequence} If / Else If Code Block Debloated.\n"

            elif construct == "Case":
                # Removing a case statement requires checking for fall through logic:
                # If the previous case has a break, the case be removed.
                # If the previous case doesn't have a break, then only the case label can be removed.

                # Search backwards from the annotation, see if a break or a case is found first.
                search_line = annotation_line - 1
                previous_break = None

                while search_line >= 0:
                    if re.search(CResourceDebloater.BREAK_PAT, " " + self.lines[search_line].strip()) is not None or \
                       re.search(CResourceDebloater.SWITCH_PAT, " " + self.lines[search_line].strip()) is not None:
                        previous_break = True
                        break
                    elif re.search(CResourceDebloater.CASE_CONSTRUCT_PAT, self.lines[search_line].strip()) is not None:
                        previous_break = False
                        break
                    else:
                        search_line -= 1

                # Log an error and skip if switch statement behavior cannot be determined
                if previous_break is None:
                    logging.error("Error finding previous case or switch for case on line " + str(annotation_line) +
                                  ".  Marking location and skipping this annotation.")
                    self.lines.insert(annotation_line + 1,
                                      f"{self.annotation_sequence} Case NOT removed due to lack of switch or previous case.\n")

                # If previous case has fall through logic, only the case label can be deleted.
                elif previous_break is False:
                    self.lines[annotation_line] = f"{self.annotation_sequence} Case Label Debloated.\n"
                    self.lines[construct_line] = "\n"

                # If the previous case does not have fall through logic, then search for next break, case, or default
                elif previous_break is True:
                    case_end = None
                    search_line = construct_line + 1
                    brace_count = self.lines[construct_line].count("{")

                    while search_line < len(self.lines):
                        brace_count += self.lines[search_line].count("{")
                        brace_count -= self.lines[search_line].count("}")

                        if re.search(CResourceDebloater.CASE_CONSTRUCT_PAT, self.lines[search_line].strip()) is not None or \
                           re.search(CResourceDebloater.DEFAULT_PAT, self.lines[search_line].strip()) is not None or \
                           brace_count < 0:
                            case_end = search_line - 1

                            # Check that the line before the next case (or default) isn't a debloating annotation.
                            if self.lines[case_end].find(f"{self.annotation_sequence}[") > -1:
                                case_end -= 1
                            break
                        elif re.search(CResourceDebloater.BREAK_PAT, " " + self.lines[search_line].strip()) is not None:
                            case_end = search_line
                            break
                        else:
                            search_line += 1

                    if case_end is None:
                        logging.error("No end of switch block found for case annotation on line " + str(annotation_line)
                                      + ".  Marking location and skipping this annotation.")
                        self.lines.insert(annotation_line + 1,
                                          f"{self.annotation_sequence} Case block NOT removed due to failure to identify end of block.\n")
                    else:
                        while case_end != annotation_line:
                            self.lines.pop(case_end)
                            case_end -= 1
                        self.lines[annotation_line] = f"{self.annotation_sequence} Case Block Debloated.\n"
                        self.lines.insert(annotation_line + 1, "\n")

            elif construct == "Statement":
                self.lines[annotation_line] = f"{self.annotation_sequence} Statement Debloated.\n"
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
        logging.info(f"Beginning debloating pass on {self.location}")

        # Search the source code for debloater annotations, and process them.
        current_line = 0

        while current_line < len(self.lines):
            if self.lines[current_line].find(f"{self.annotation_sequence}[") > -1:
                logging.info("Annotation found on line " + str(current_line))

                feature_set = CResourceDebloater.get_features(self.lines[current_line])

                if self.target_features.issuperset(feature_set):
                    logging.info("Processing annotation found on line " + str(current_line))
                    self.process_annotation(current_line)
            current_line += 1
