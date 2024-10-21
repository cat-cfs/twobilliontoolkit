# Network Transfer

## Project Description

The NetworkTransfer tool transfers files from a source directory to a destination, primarily focusing on transferring files from local computers to a network drive. This is especially useful for processing the Two Billion Trees Toolkit. The tool can handle complete directories, specific files, and merge geodatabases.


## Table of Contents

- [Project Description](#project-description)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Installation

The NetworkTransfer module of the twobilliontoolkit package is included in the installation of the package itself. Currently there is no easy way of downloading just one tool from the package because the tools depend on other tools within the package, but if you wish to use this tool, follow the installation process documented [in the package README](../../README.md)

You should then be set up to use the tool!

## Usage

**Note**: This will need to be run in an ArcGIS Pro environment because it uses its library called Arcpy. If you do not know how to do this, please contact someone for help before continuing because the tool will not work. Or if you are able to use the arcpy library on your machine outside of the arcgis enironment that may also work but has not been tested.

To use NetworkTransfer, run the script from the command line with the following syntax:
```
arcpy_environment_python_path path/to/network_transfer.py local_path source_path network_path destination_path [--files [...list of files...]]

- [-h, --help] (optional): List all of the available commands and a description for help.
- local_path source_path: Path to the source directory where the files will be moved from.
- network_path destination_path: Path to the destination directory where the files will be moved to.
- [--files [...list of files...]] (optional): List of specific files to transfer. If left blank it will transfer all files.

Example from root of project:
```
python ./twobilliontoolkit/NetworkTransfer/network_transfer.py ./source ./destination --files file1.txt file2.gdb

```

You also have the option of calling this tool from a module import with the following syntax:
```
from twobilliontoolkit.Logger.logger import log, Colors
from twobilliontoolkit.NetworkTransfer.network_transfer import transfer

def main():
    local_path = './source'
    network_path = './destination'
    log_path = './log.txt'
    files = ['file1.txt', 'file2.gdb']

    success = transfer(local_path, network_path, files, log_path)
    if success:
        print("Transfer completed successfully.")
    else:
        print("Transfer failed.")

```

## Configuration

No specific configuration is needed for the NetworkTransfer tool. Ensure you have the necessary permissions to read from the source and write to the destination directories.

## Contributing

This project might not be maintained or up to date.

If you would like to contribute to NetworkTransfer, follow these guidelines:

1. Submit bug reports or feature requests via the GitHub issue tracker.
2. Fork the repository, make your changes, and submit a pull request.

## License

This project is licensed under the MIT License. [Click here to view the license file](../../LICENSE) and review the terms and conditions of the MIT License.

## Contact

If you have any questions, feedback, or suggestions, you can reach out here:

- Anthony Rodway
- Email: anthony.rodway@nrcan-rncan.gc.ca

If I am not reachable, then please contact Andrea Nesdoly for any questions you may have. You may reach her at andrea.nesdoly@nrcan-rncan.gc.ca

Feel free to provide your input to help improve NetworkTransfer!