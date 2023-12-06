# CARVE
CARVE is a source code based software debloating tool. It can be used to remove code associated with unwanted features in software and optionally replace them with code that handles attempts to invoke removed features. CARVE provides separation between two different tasks in software debloating:
 1. identifying code associated with features
 2. removing code associated with features.

If you use this tool in your research, please cite the following paper:

**Brown, Michael D., and Santosh Pande. "CARVE: Practical Security-Focused Software Debloating Using Simple Feature Set Mappings". In 3rd ACM Workshop on Forming an Ecosystem Around Software Transformation (FEAST '19). 2019.**[\[pdf\]](https://dl.acm.org/doi/abs/10.1145/3338502.3359764)

## Description
CARVE is a source code based software debloater that operates similarly to a compiler's preprocessor. Software features must be mapped to the source code associated with them prior to removal with CARVE. To make this easy, CARVE supports both language agnostic **explicit** feature mappings and language specific **implicit** feature mappings. Implicit feature mappings intelligently determine the code to be removed based on the source code construct marked by the feature mapping. CARVE supports C/C++ and Python.

Currently, CARVE supports the following implicit feature mappings for C/C++ source code:

 1. If / Else If / Else conditional branching constructs
 2. Function definitions
 3. Cases within switch statements
 4. Single statements

And for Python, CARVE supports implicit mappings of:
 1. If / Else conditional branching constructs
 2. Function definitions
 3. Single statements
 4. Class Definitions
 
CARVE takes as input a configuration file specifying the following pieces of information:

 1. Locations of source code files
 2. Source code language
 3. File extensions of files to process for debloating
 4. Names of software features that can be debloated (expressed as a hierarchy to simplify feature mapping)
 5. Names of the features (or feature groups) to debloat

CARVE debloats the source code in-place and produces as output a timestamped results folder containing:

 1. A copy of the debloating configuration file.
 2. A log file containing output generated during the debloating process.

## Installation
Run `pip install .` to install CARVE and dependencies. (We recommend installing in a virtual environment.)

## Mapping Features to Source Code
The following subsections describe the types of feature mappings CARVE currently supports. Additional information on these mappings can be found in the research paper linked above.  Additionally, a fully mapped version of [libmodbus](https://libmodbus.org/) v3.1.4 is provided in the `sample` subdirectory.

### Feature Mapping Anatomy: Tag and Feature(s)
Feature mappings are differentiated from typical comments by a user-definable tag. Tags are language specific, and must be considered legal comments. The tag used by CARVE's C/C++ debloating module is `///` (and `###` for Python). Immediately following the tag, one or more features (or feature groups) associated with the tagged code must be listed, each enclosed in a set of square braces `[ ]`. For example, the feature mapping `///[Feature_X][Feature_Y]` identifies the code following the tag as associated with Features X and Y. If both X and Y are selected for debloating, the tagged code will be removed by CARVE.

### Full File Mapping
To map all of the code in a file to features or feature groups, the `!` marker can be appended to a feature mapping. When CARVE processes this mapping, it produces an empty file rather than deleting the file outright to avoid breaking build processes. For example, the feature mapping `///[FeatureGroup_A]!` placed anywhere within the file will debloat all code in the file if Feature Group A is selected for debloating.

### Segment Mapping with Optional Replacement
Segment explicit mappings are indicated by the `~` marker being appended to the feature mapping. When CARVE processes this mapping, it will remove code between the mapping and the next occurring termination marker, indicated by the tag and the `~` marker (`///~`). Replacement code segments can also be specified between the two replacement tags (`///^`) for segment explicit mappings. For example, the debloating with replacement mapping:

```
///[Feature_Y]~
///^
///return 0;
///^
int ret = i + a;
int temp = b - j;
return ret * temp;
///~
```
instructs CARVE to remove the three lines of code between the mapping and the termination tag, and replace it with the single line of code `return 0;`.

### Implicit Feature Mappings
Implicit mappings instruct the debloater to analyze the code following the mapping to determine its structure, and by extension what code should be removed. Implicit mappings obviate the need to handle predictable control-flow implications associated with certain types of code constructs by using explicit mappings with replacement code. Feature mappings that do not have an operator appended to them are considered implicit mappings by CARVE.

### Limitations
It is important to note that CARVE operates largely on a line-by-line basis on source code. Though wide leeway in syntax is provided by most programming languages, CARVE does not support all coding styles for implicit feature mappings. A (probably incomplete) list of unsupported C/C++ programming styles can be found in the C/C++ debloating module. It is recommended that incompatible styles be adjusted when annotating the source code with feature mappings. The Python debloater is more style-tolerant for implicit mappings.


## Debloating Source Code
CARVE has the following optional inputs:

 1. Log Level (--log_level): Adjust the verbosity of log information produced by CARVE.

CARVE has 1 required input:

 1. Configuration File: Filepath to the config file.

Example invocations:
```
python3 -m carve --log_level [level] [path to config file]

python3 -m carve sample/debloat-config.yaml
```

## Testing
CARVE has tests in `test/`. Install CARVE in developer mode `pip install -e ".[dev]"` and run `pytest test`.
