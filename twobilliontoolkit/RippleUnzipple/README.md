# Ripple Unzipple

## Project Description

The Ripple Unzipple project is a Python script designed to recursively unzip all compressed folders in a given directory. It supports both .zip and .7z file formats and provides a straightforward solution for efficiently extracting compressed data. The script is particularly useful for scenarios where nested compressed folders need to be extracted.

## Table of Contents

- [Project Description](#project-description)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Installation

The RippleUnzipple module of the twobilliontoolkit package is included in the installation of the package itself. Currently there is no easy way of downloading just one tool from the package because the tools depend on other tools within the package, but if you wish to use this tool, follow the installation process documented [in the package README](../../README.md)

You should then be set up to use the tool!

## Usage

To use Ripple Unzipple, run the script from the command line with the following syntax:
```
python /path/to/ripple_unzipple.py /path/to/input /path/to/output [log_path]
```
- input_path: Path to the input directory or compressed file.
- output_path: Path to the output directory where the uncompressed data will be stored.
- log_path (optional): Path to the log file. If provided, detailed logs will be saved to this file.

Example from root of project:
```
python ./twobilliontoolkit/RippleUnzipple/ripple_unzipple.py /Testing/Data/TestFolder.zip /Testing/OutputFolder /Testing/OutputLog.txt
```

You also have the option of calling this function from a module import with the following syntax:
```
from twobilliontoolkit.RippleUnzipple.ripple_unzipple import ripple_unzip

def main():
    ripple_unzip(input_path, output_path, log_path)
```
**Note**: One thing that you should keep in mind is that the output path folder name will overwrite the initial input path folder or file name in the final result. So if you wish to preserve that root object's name you can name your output path folder the same, or put the original input object in another folder and call the folder instead.

## Configuration

You may run into an issue with your machines MAX_PATH_LENGTH being reached when trying to extract an extensive path with long directory names. On windows, to make sure this does not happen (Requires Users to have either Full Control or Special Permissions, if not available, contact an admin):

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

## Contributing

This project might not be maintained.

If you would like to contribute to Ripple Unzipple, follow these guidelines:

1. Submit bug reports or feature requests via the GitHub issue tracker.
2. Fork the repository, make your changes, and submit a pull request.

## License

This project is licensed under the MIT License. [Click here to view the license file](../LICENSE) and review the terms and conditions of the MIT License.

## Contact

If you have any questions, feedback, or suggestions, you can reach out here:

- Anthony Rodway
- Email: anthony.rodway@nrcan-rncan.gc.ca

If I am not reachable, then please contact Andrea Nesdoly for any questions you may have. You may reach her at andrea.nesdoly@nrcan-rncan.gc.ca

Feel free to provide your input to help improve Ripple Unzipple!

