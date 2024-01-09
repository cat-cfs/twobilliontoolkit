# Spatial Transformer

## Project Description

This project aims to develop tools for the spatial data processing workflow for 2BT. The workflow involves gathering and preparing raw spatial data from various sources, including CSV tables and spatial files, and converting them into feature classes within a Geodatabase (GDB). The primary goal is to create efficient, reusable Python scripts and tools that can handle different data formats and integrate seamlessly with the existing 2BT data infrastructure.

## Table of Contents

- [Project Description](#project-description)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Contributing](#contributing)
- [License](#license)

## Installation

To install and set up Spatial Transformer, follow these steps:

1. Clone the repository to your local machine.
2. Ensure that you have Python >=3.10 installed. Download from [here](https://www.python.org/downloads/release/python-3100/) if not.
3. Install the required dependencies using the following command:

```
pip install -r /path/to/requirements.txt
```

You should then be set up to use the tool!

## Usage

**Note**: This will need to be run in an ArcGIS Pro environment because it uses its library called Arcpy. If you do not know how to do this, please contact someone who for help before continuing because the tool would not work. Or if you are able to use the arcpy library on your machine without any restrictions and issues that may also work but has not been tested.

To use the Spatial Transformer, run the script from the command line with the following syntax:

```
arcpy_environment_python_path /path/to/spatial_transformer.py [-h] [--log_path LOG_PATH] [--debug] --load {datatracker,database} --save {datatracker,database} unzipper_input_path unzipper_output_path gdb_path data_tracker_path
```
- [-h, --help] (optional): List all of the available commands and a description for help.
- [--log_path log_path] (optional): Path to the log file. If provided, detailed logs will be saved to this file. 
- --load {datatracker,database}: Specify wheather the tool loads the data from an exisiting datatracker or a database connection. 
- --save {datatracker,database}: Specify wheather the tool saves the data to a specified datatracker or a database connection. 
- unzipper_input_path: Path to the input directory or compressed file.
- unzipper_output_path: Path to the output directory where the uncompressed data will be stored.
- gdb_path: Path to where the resulting GeoDatabase will be stored, it can be an existing GeoDatabase, else it will create the GeoDatabase itself.
- data_tracker_path: Path to where the resulting Data Tracker Excell sheet will be stored, it can be an existing datasheet, else it will create it when it is complete.

Example from root of project:
```
python ./spatial_transformer/spatial_transformer.py ./Testing/Data/TestFolder.zip ./Testing/OutputFolder ./Testing/OutputGDB.gdb ./Testing/OutputDataSheet.xlsx --log_path ./Testing/OutputLog.txt --load datatracker --save datatracker
```

You also have the option of calling this function from a module import with the following syntax (you may need to use relative or absolute paths depending on your environment and where you are calling from):
```
from spatial_transformer.common import *
from spatial_transformer.spatial_transformer import StartupParameters
from spatial_transformer.ProcessorModule import Processor
from spatial_transformer.DataTrackerModule import DataTracker

def main():
    input_path = './Testing/Data/TestFolder.zip'
    output_path = './Testing/OutputFolder'
    gdb_path = './Testing/OutputGDB.gdb'
    datatracker_path = './Testing/OutputDataSheet.xlsx'
    log_path = './Testing/OutputLog.txt'
    load_from = 'database'
    save_to = 'database'
    
    startparams = StartupParameters(input_path, output_path, gdb_path,
      datatracker_path, log_path, load_from, save_to)
    processor = Processor(self.startparams)
    datatracker = DataTracker(self.startparams.datatracker)
```
**Note**: if you dont wish to save to a log, you can omit that and it will just print its messages to the standard out stream.

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

Feel free to provide your input to help improve Ripple Unzipple!
