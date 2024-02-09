# Record Reviser

## Project Description

This tool focuses on updating the records produced by the spatial transformer tool in either the data tracker or the database, the raw data gdb and the exported attachment folders as necessary. It can be used as a standalone script to change the records at any time. If working with the 2BT data, the user has the option to update the project number, which will do some background processes, creating a new duplicated record so the original record remains unchanged, but will updated any fields in the duplicated record. If you updated any of the boolean fields, it will directly change the original record and not make a duplicate. 

If no changes are given in the command-line, a GUI popup will open and allow the user to change any records as they see fit. Any changes in the table will be changed to red to indicate they were changed, and the user can click the reset button to changed these values back to when the application started or when it was last saved. The save button will submit the changes to the system and start the background processes.


## Table of Contents

- [Project Description](#project-description)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Contributing](#contributing)
- [License](#license)

## Installation

The RecordReviser module of the twobilliontoolkit package is included in the installation of the package itself. Currently there is no easy way of downloading just one tool from the package because the tools depend on other tools within the package, but if you wish to use this tool, follow the installation process documented [in the package README](../../README.md)

You should then be set up to use the tool!

## Usage

**Note**: This will need to be run in an ArcGIS Pro environment because it uses its library called Arcpy. If you do not know how to do this, please contact someone who for help before continuing because the tool would not work. Or if you are able to use the arcpy library on your machine without any restrictions and issues that may also work but has not been tested.

To use RecordReviser, run the script from the command line with the following syntax:
```
arcpy_environment_python_path /path/to/record_reviser.py [-h] --gdb /path/to/geodatabase --load [datatracker/database] --save [datatracker/database] --data_tracker /path/to/data_tracker.xlsx --log /path/to/logfile.txt --changes "{project_spatial_id: {field: newvalue, field2: newvalue2...}, project_spatial_id: {field: newfield}...}"
```
- [-h, --help] (optional): List all of the available commands and a description for help.
- --gdb gdbpath: The path to the GeoDatabase which holds the project layers for what will be updated 
- --load {datatracker,database}: Specify wheather the tool loads the data from an exisiting datatracker or a database connection. 
- --save {datatracker,database}: Specify wheather the tool saves the data to a specified datatracker or a database connection. 
- [--data_tracker_path data_tracker_path] (conditional): Path to where the Datatracker sheet is located. This is only needed if one of the 'load' or 'save' arguments is spacified as *datatracker*
- [--changes "{project_spaital_id: {field: newvalue, field2:newvalue2...}, project_spatial_id: {field: newfield}...}"] (optional): The dictionary of changes that you want to update the data with.

Example from root of project:
```
python ./RecordReviser/record_reviser.py --load database --save database --gdb .\twobilliontoolkit\SpatialTransformer\OutputGDB.gdb --data_tracker .\twobilliontoolkit\SpatialTransformer\OutputDataTracker.xlsx
```

You also have the option of calling this function from a module import with the following syntax:
```
from PyQt5.QtWidgets import QApplication
from twobilliontoolkit.RecordReviser.record_reviser import DataTableApp, update_records
from twobilliontoolkit.SpatialTransformer.Datatracker import Datatracker

def some_func():
    gdb = 'path/to/gdb'
    data = Datatracker(...)

    # Open the record reviser
    app = QApplication([])
    window = DataTableApp(data, gdb)
    app.exec_()  
```
**Note**: Using the DataTableApp and PyQT5, a GUI will be opened (as seen below) with the data contained in the Datatracker class.

![Alt text](image.png)

## Configuration

If you are going to be working with a database, one of the first things that you must do when trying to use this package is to fill in the information to establish a connection. This is needed for a couple of tools . Navigate to [/twobilliontoolkit/SpatialTransformer/database.ini](/twobilliontoolkit/SpatialTransformer/database.ini) and fill out the postgresql section

```
[postgresql]
host = 
port = 
database = 
user = 
password = 
```
This will allow you to connect to a database that you have set up, however you may need to make changes to the code or to the database to make sure everything works properly.

## Contributing

This project might not be maintained or up to date.

If you would like to contribute to RecordReviser, follow these guidelines:

1. Submit bug reports or feature requests via the GitHub issue tracker.
2. Fork the repository, make your changes, and submit a pull request.

## License

This project is licensed under the MIT License. [Click here to view the license file](LICENSE) and review the terms and conditions of the MIT License.

## Contact

If you have any questions, feedback, or suggestions, you can reach out here:

- Anthony Rodway
- Email: anthony.rodway@nrcan-rncan.gc.ca

If I am not reachable, then please contact Andrea Nesdoly for any questions you may have. You may reach her at andrea.nesdoly@nrcan-rncan.gc.ca

Feel free to provide your input to help improve RecordReviser!