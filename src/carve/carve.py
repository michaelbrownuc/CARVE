#!/usr/bin/env python3
"""
CARVE Debloater CLI
This script's primary purpose is to read in the specified debloating configuration and target folder containing the
target library source code, and apply the appropriate transformations to the source code.

This debloater is extensible to any language that supports in-source commenting. However, at current time it only supports 
debloating C/C++ style source files with implicit mappings. Explicit mappings can be used with the C resource debloater to 
debloat any kind of source code.
"""

# Standard Library Imports
import argparse
import logging
import shutil
import sys
from pathlib import Path

# Third Party Imports
import yaml

# Local Imports
from carve.utility import *
from carve.resource_debloater.CResourceDebloater import CResourceDebloater
from carve.resource_debloater.PythonResourceDebloater import PythonResourceDebloater

def main() -> None:
    # Parse command line options
    log_opts = {"DEBUG": logging.DEBUG, "INFO": logging.INFO, "WARNING": logging.WARNING, "ERROR": logging.ERROR,
                "CRITICAL": logging.CRITICAL}

    parser = argparse.ArgumentParser()
    parser.add_argument("debloat_config", help="File containing debloating configuration.", type=str)
    parser.add_argument("-ll", "--log_level", help="Verbosity of logging.", type=str, default='INFO',
                        choices=log_opts.keys())

    args = parser.parse_args()

    # Create a timestamped results folder and pre-populate it with a copy of the campaign file
    try:
        directory_name = create_output_directory("results/debloat_results_")
    except OSError as oserr:
        print("An OS Error occurred during creation of results directory: " + oserr.strerror)
        sys.exit("Results cannot be logged, aborting operation...")

    # Initialize the logger
    log_level = log_opts.get(args.log_level)
    logging.basicConfig(filename=directory_name + "/debloating_log.txt", level=log_level)

    # Copy the debloating configuration used to the results directory for posterity
    shutil.copy2(args.debloat_config, directory_name)

    # Parse Configuration File
    try:
        config = yaml.safe_load(open(args.debloat_config, "r"))
    except yaml.YAMLError as err:
        logging.error("An error occurred when parsing the debloat config file: {err}".format(err=err))
        sys.exit("Debloating configuration cannot be parsed, aborting operation...")

    # Iterate through the specified libraries and debloat them according to the configuration file
    libraries = config.get("Libraries")
    for library in libraries:
        logging.info("Starting debloating operation on library: " + library.get("name"))

        # Create total list of features to debloat (expand categories to leaf features)
        logging.info("Identifying features to debloat.")

        debloatable_features = library.get("debloatable_features")
        features_to_debloat = library.get("debloat")

        if features_to_debloat is None:
            logging.error("No features selected to debloat. Terminating.")
            sys.exit("No features selected to debloat. Terminating.")

        target_features = set(features_to_debloat)

        for feature in features_to_debloat:
            search_results = search_hierarchy(feature, debloatable_features)

            if len(search_results) == 0:
                logging.error("Feature to debloat: " + feature + " was not found in the hierarchy of debloatable "
                            "features.")
                sys.exit("Specified feature to debloat not specified in feature hierarchy.  Please ensure the configuration"
                        + " is correct.")

            target_features = set(search_results).union(target_features)

        # Pull relevant configuration entries
        locations = library.get("locations")
        extensions = library.get("extensions")
        language = library.get("language")

        # Currently only supports C/C++ - If new debloating modules are created the opts dict below must be updated.
        language_opts = {"C": CResourceDebloater, "Python": PythonResourceDebloater}
        language_type = language_opts.get(language)

        if language_type is None:
            logging.error("Specified language:" + language + " is not supported.")
            sys.exit("Specified language:" + language + " is not supported. Exiting...")

        # Iterate through library source code locations
        for location in locations:
            for dirpath, dirnames, filenames in os.walk(location):
                # Iterate through files in the location
                for filename in filenames:
                    file = Path(dirpath) / filename
                    if get_extension(file.name) in extensions:
                        logging.info(f"Processing file: {file}")
                        # Process the file
                        resource_debloater = language_type(file, target_features)
                        resource_debloater.read_from_disk()
                        resource_debloater.debloat()
                        resource_debloater.write_to_disk()
