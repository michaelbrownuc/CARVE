# CARVE
CARVE is a source code based software debloating tool. It can be used to remove code associated with unwanted features in software and optionally replace them with code that handles attempts to invoke removed features. CARVE provides separation between to different tasks in software debloating: identifying code associated with features removing code associated with features.

If you use this tool in your research, please cite the following paper:

**Brown, Michael D., and Santosh Pande. "CARVE: Practical Security-Focused Software Debloating Using Simple Feature Set Mappings". In 3rd ACM Workshop on Forming an Ecosystem Around Software Transformation (FEAST '19). 2019.**[\[pdf\]](https://dl.acm.org/doi/abs/10.1145/3338502.3359764)

## Description
CARVE is a source code based software debloater that operates similarly to a compiler's preprocessor. Software features must be mapped to the source code associated with them prior to removal with CARVE. To make this easy, CARVE supports both language agnostic **explicit** feature mappings and language specific **implicit** feature mappings. Implicit feature mappings intelligently determine the code to be removed based on the source code construct marked by the feature mapping. Currently, CARVE supports the following implicit feature mappings for C/C++ source code:

 1. If / Else If / Else conditional branching constructs
 2. Function definitions
 3. Cases within switch statements
 4. Single statements
 
CARVE takes as input a configuration file specifying the following pieces of information:

 1. Locations of source code files
 2. Source code language
 3. File extensions of files to process for debloating
 4. Names of software features that can be debloated (expressed as a hierarchy to simplify feature mapping)
 5. Names of the features (or feature groups) to debloat

CARVE produces as output a timestamped results folder containing:

 1. A copy of the debloating configuration file.
 2. A log file containing output generated during the debloating process.
 3. A folder containing the debloated source code, which can be then compiled to produce a debloated binary.

## Dependencies
CARVE is dependent upon the following third party packages / libraries:

 1. PyYAML - file format for config file.  `pip install pyyaml`

## Mapping Features to Source Code
TODO

## Debloating Source Code
CARVE has the following optional inputs:

 1. Log Level (--log_level): Adjust the verbosity of log information produced by CARVE.

CARVE has 1 required input:

 1. Configuration File: Filepath to the config file.

Example invocations:
```
python3 CARVE.py --log_level [level] [path to config file]

python3 CARVE.PY /sample/debloat-config.yaml
```
