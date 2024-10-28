# GeoAttachmentSeeker

## Project Description

This tool is designed to identify and process attachment tables within specified GeoDatabases, extracting attachment files and organizing them based on project IDs.

## Table of Contents

- [Project Description](#project-description)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Installation

The GeoAttachmentSeeker module of the twobilliontoolkit package is included in the installation of the package itself. Currently there is no easy way of downloading just one tool from the package because the tools depend on other tools within the package, but if you wish to use this tool, follow the installation process documented [in the package README](../../README.md)

You should then be set up to use the tool!

## Usage

**Note**: This will need to be run in an ArcGIS Pro environment because it uses its library called Arcpy. If you do not know how to do this, please contact someone for help before continuing because the tool will not work. Or if you are able to use the arcpy library on your machine outside of the arcgis enironment that may also work but has not been tested.

To use GeoAttachmentSeeker, run the script from the command line with the following syntax:
```
arcpy_environment_python_path /path/to/geo_attachment_seeker.py [-h] /path/to/geodatabase.gdb /path/to/output_path
```
- [-h, --help] (optional): List all of the available commands and a description for help.
- gdb_path: Path to the input Geodatabase that will be searched through.
- output_path: Path to the output directory where the project folder will be placed containing any attachments extracted.

Example from root of project:
```
python ./twobilliontoolkit/GeoAttachmentSeeker/geo_attachment_seeker.py ./Testing/Data/TestGDB1.gdb ./OutputFolder
```

You also have the option of calling this function from a module import with the following syntax:
```
from twobilliontoolkit.GeoAttachmentSeeker.geo_attachment_seeker import find_attachments, process_attachment

def main():
    find_attachments(gdb_path, output_path)
```

## Configuration

No additional configuration is required for GeoAttachmentSeeker. However, ensure that you have the necessary permissions to read from the GeoDatabase and write to the specified output folder.

## Contributing

This project might not be maintained.

If you would like to contribute to GeoAttachmentSeeker, follow these guidelines:

1. Submit bug reports or feature requests via the GitHub issue tracker.
2. Fork the repository, make your changes, and submit a pull request.

## License

This project is licensed under the MIT License. [Click here to view the license file](../LICENSE) and review the terms and conditions of the MIT License.

## Contact

If you have any questions, feedback, or suggestions, you can reach out here:

- Anthony Rodway
- Email: anthony.rodway@nrcan-rncan.gc.ca

If I am not reachable, then please contact Andrea Nesdoly for any questions you may have. You may reach her at andrea.nesdoly@nrcan-rncan.gc.ca

Feel free to provide your input to help improve GeoAttachmentSeeker!
