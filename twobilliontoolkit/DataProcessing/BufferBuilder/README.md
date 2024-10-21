# Buffer Builder

## Project Description

This tool is for processing spatial data, creating buffer zones around given points, and integrating the results with a PostgreSQL/PostGIS database. This script supports spatial analysis tasks related to carbon accounting and land management.

## Table of Contents

- [Project Description](#project-description)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Contributing](#contributing)
- [License](#license)

## Installation

The DataProcessing module of the twobilliontoolkit package is included in the installation of the package itself. Currently there is no easy way of downloading just one tool from the package because the tools depend on other tools within the package, but if you wish to use this tool, follow the installation process documented [in the package README](../../../README.md)

You should then be set up to use the tool!

## Usage

To use BufferBuilder, run the script from the command line with the following syntax:
```
python path/to/buffer_builder.py --datasheet <datasheet_path> --ini <database_ini_path> --log <log_file_path> [--ps_script <script_path>] [--debug]
```
- `[-h, --help]` (optional): List all of the available commands and a description for help.
- `--datasheet` (required): Path to the spatial data sheet (must be .csv or .xlsx).
- `--ini` (required): Path to the database initialization file.
- `--log` (required): Path to the output log file.
- `--ps_script` (optional): Path to a PowerShell script for additional commands.
- `--debug` (optional): Flag to enable debug mode.

Example from the root of the project:
```
python ./twobilliontoolkit/DataProcessing/BufferBuilder/buffer_builder.py --datasheet ./test_spatial_file.xlsx --ini ./twobilliontoolkit/SpatialTransformer/config.ini --log ./twobilliontoolkit/DataProcessing/BufferBuilder/log.txt
```

A preloaded commands powershell script is ready for you to use [here](./commands.ps1) you will just need to change out some variables labelled as "..." and then run the script by 
```
./commands.ps1
```
and following the walkthrough

You also have the option of calling this tool from a module import with the following syntax:
```
from twobilliontoolkit.DataProcessing.BufferBuilder.buffer_builder import buffer_builder

def main():
    data_sheet = 'path/to/spatial_data.xlsx'
    database_ini = 'path/to/config.ini'
    log_path = 'path/to/log.txt'
    
    # Call the handler function
    buffer_builder(data_sheet= data_sheet, database_ini = db_config, log_path = log_path)
```

## Configuration

If you are going to be working with a database, one of the first things that you must do when trying to use this package is to fill in the information to establish a connection. This is needed for a couple of tools. Navigate to [/twobilliontoolkit/SpatialTransformer/database.ini](/twobilliontoolkit/SpatialTransformer/database.ini) and fill out the postgresql section

```
[postgresql]
host = 
port = 
database = 
schema = 
table = 
user = 
password = 
```
This will allow you to connect to a PostGreSQL database that you have set up, however you may need to make changes to the code or to the database to make sure everything works properly.

## Contributing

This project might not be maintained or up to date.

If you would like to contribute to DataDuster, follow these guidelines:

1. Submit bug reports or feature requests via the GitHub issue tracker.
2. Fork the repository, make your changes, and submit a pull request.

## License

This project is licensed under the MIT License. [Click here to view the license file](../../../LICENSE) and review the terms and conditions of the MIT License.

## Contact

If you have any questions, feedback, or suggestions, you can reach out here:

- Anthony Rodway
- Email: anthony.rodway@nrcan-rncan.gc.ca

If I am not reachable, then please contact Andrea Nesdoly for any questions you may have. You may reach her at andrea.nesdoly@nrcan-rncan.gc.ca

Feel free to provide your input to help improve Buffer Builder!