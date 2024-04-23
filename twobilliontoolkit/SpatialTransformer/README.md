# Spatial Transformer

## Project Description

The SpatailTransformer tool is the main processing of the 2BT Data pipeline. 

The SpatialTransformer tool is a crucial component of the 2BT Data pipeline, it facilitates tasks such as geodatabase creation, file validation, and cross-referencing project numbers against a master data sheet. This tool serves as a vital utility for managing spatial data effectively within organizations, particularly for tasks related to geospatial data processing and analysis.

## Table of Contents

- [Project Description](#project-description)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Contributing](#contributing)
- [License](#license)

## Installation

The spatial transformer module of the twobilliontoolkit package is included in the installation of the package itself. Currently there is no easy way of downloading just one tool from the package because the tools depend on other tools within the package, but if you wish to use this tool, follow the installation process documented [in the package README](../../README.md)

You should then be set up to use the tool!

## Usage

**Note**: This will need to be run in an ArcGIS Pro environment because it uses its library called Arcpy. If you do not know how to do this, please contact someone for help before continuing because the tool will not work. Or if you are able to use the arcpy library on your machine outside of the arcgis enironment that may also work but has not been tested.

To use the Spatial Transformer, run the script from the command line with the following syntax:
```
arcpy_environment_python_path /path/to/spatial_transformer.py [-h] --input_path input_path --output_path output_path --gdb_path gdb_path --master master_data_path --load {datatracker,database} --save {datatracker,database} [--datatracker datatracker_path] [--attachments attachments_path] [--debug] [--suppress] [--resume]
```
- [-h, --help] (optional): List all of the available commands and a description for help.
- --input_path input_path : Path to the input directory or compressed file.
- --output_path output_path: Path for output of Ripple unzipple. If not provided.
- --gdb_path gdb_path: The GeoDatabase path where it will be saved. It will be either created or merged into an exisiting GeoDatabase if it already exists.
- --master master_data_path: Path to where the aspatial master datasheet is located.
- --load {datatracker,database}: Specify wheather the tool loads the data from an exisiting datatracker or a database connection. 
- --save {datatracker,database}: Specify wheather the tool saves the data to a specified datatracker or a database connection. 
- [--datatracker datatracker] (conditional): Name of the resulting Data Tracker Excell sheet to be stored, it can be an existing datasheet, else it will create it when it is complete.
- [--attachments attachments] (optional): The name of the attachments folder extracted from the geodatabase.
- [--debug] (optional): include to enable debugging mode, giving some more information.
- [--suppress] (optional): omits Warning logs from the command line, they are still added to their relivant log file though.
- [--resume] (optional): include to continue where the code left off from if there was a fatal crash, this may be a bit buggy and need some manual intervention afterwards.

**Note**: If an attachments name is not provided, it will take the same name provided for the geodatabase and append _Attachments. (ie. If --gdb testing223.gdb, then the attachments folder will be named testing223_Attachments). It will also be adjacent to the geodatabase in the output.

**Note**: Multiple logs are automatically created with the name of your gdb, a date (YYYY-MM-DD) and what type of log was passed (WARNING, ERROR). They will also be adjacent to the output.

Example from root of project:
```
python ./twobilliontoolkit/SpatialTransformer/spatial_transformer.py --input_path ./Testing/Data/TestFolder.zip --output_path ./Testing/OutputFolder --gdb_path ./Testing/OutputGDB.gdb --datatracker OutputDataSheet.xlsx --load datatracker --save datatracker --master ./MasterDatasheet --attachments ./Testing/Attachments --suppress
```

You also have the option of calling this function from a module import with the following syntax (you may need to use relative or absolute paths depending on your environment and where you are calling from):
```
from twobilliontoolkit.SpatialTransformer.common import *
from twobilliontoolkit.Logger.logger import log, Colors
from twobilliontoolkit.SpatialTransformer.Parameters import Parameters
from twobilliontoolkit.SpatialTransformer.Processor import Processor
from twobilliontoolkit.SpatialTransformer.spatial_transformer import spatial_transformer

# Example input parameters
input_path = "/path/to/input/data"
output_path = "/path/to/output/data"
load_from = "database"
save_to = "datatracker"
gdb_path ="./Testing/geodatabase.gdb"
datatracker = "datatracker.xlsx"
attachments = "attachmentsfolder"
master_data_path = "/path/to/master_data.xlsx"
debug = True
resume = False
suppress = True

# Call the spatial_transformer function
spatial_transformer(
    input_path, output_path, load_from, save_to, gdb_path, datatracker, attachments, master_data_path, debug, resume, suppress
)
```

## Configuration

An issue that was found when using a tool that this project is dependant on: You may run into an issue with your machines MAX_PATH_LENGTH being reached when trying to extract an extensive path with long directory names. On windows, to make sure this does not happen (Requires Users to have either Full Control or Special Permissions, if not available, contact an admin):

1. Press the windows start key and type *Registry Editor* and choose the best match.
2. Navigate to the following location
*HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\FileSystem*.
3. Select the variable named **LongPathsEnabled**.
    
    **Note**: If the registry key does not exist, you can add it by performing the following:
    
    1. Right-click in an empty space below the other key
    2. Select *New*.
    3. Choose *DWORD (32-bit) Value*.
    4. Right-click the newly added key and choose *Rename*.
    5. Rename the key to **LongPathsEnabled** and press *Enter*.

4. Double-click the **LongPathsEnabled** entry to open the key.
5. In the *Value* data field, enter a value of **1** and press OK.

Now, longer paths should be enabled on your machine, and no issues should arise. For more information, please follow this [link](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/The-Windows-10-default-path-length-limitation-MAX-PATH-is-256-characters.html#:~:text=By%20default%2C%20Windows%20uses%20a,Files%2C%20Paths%2C%20and%20Namespaces.).

**Note**: There is a annoying use case where the tool will crash unexpectedly when one of the project folders within the root folder is named the same as the root folder (ie. root_folder/root_folder). It would be very easy to remidy this by just changing the compressed folder or the outputted unzipped folders name.

## Contributing

This project might not be maintained.

If you would like to contribute to Spatial Transformer, follow these guidelines:

1. Submit bug reports or feature requests via the GitHub issue tracker.
2. Fork the repository, make your changes, and submit a pull request.

## License

This project is licensed under the MIT License. [Click here to view the license file](../LICENSE) and review the terms and conditions of the MIT License.

## Contact

If you have any questions, feedback, or suggestions, you can reach out here:

- Anthony Rodway
- Email: anthony.rodway@nrcan-rncan.gc.ca

If I am not reachable, then please contact Andrea Nesdoly for any questions you may have. You may reach her at andrea.nesdoly@nrcan-rncan.gc.ca

Feel free to provide your input to help improve Spatial Transformer!
