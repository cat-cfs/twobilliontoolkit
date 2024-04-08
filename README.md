# twobilliontoolkit

## Project Description

This repo stands as a singular place for all the tools that will be developed for the processing of 2 Billion Trees data and information. It is a collection of tools, so each one has its own respective READMEs:
- [GeoAttachmentSeeker README](twobilliontoolkit/GeoAttachmentSeeker/README.md)
- [RecordReviser README](twobilliontoolkit/RecordReviser/README.md)
- [RippleUnzipple README](twobilliontoolkit/RippleUnzipple/README.md)
- [SpatialTransformer README](twobilliontoolkit/SpatialTransformer/README.md)

## Table of Contents

- [Project Description](#project-description)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Contributing](#contributing)
- [License](#license)

## Installation

To install and set up the twobilliontoolkit package, follow these steps:
1. First Ensure that you have Python >=3.9 installed. Download from [here](https://www.python.org/downloads/release/python-3100/) if not.
2. If you plan to just use the package through imports

    i. You can install the package directly using the following command:

    ```
    pip install git+https://github.com/cat-cfs/twobilliontoolkit.git
    ```

3. If you plan to develop on top of this or make any changes, you can
    
    i. Clone the repository to your local machine using the following command:

    ```
    git clone https://github.com/cat-cfs/twobilliontoolkit.git
    ```

    ii. Then you can run the setup file and install the package onto your environment with:

    ```
    pip install /path/to/root/folder
    ```
        
    If you already in the root folder you can also run
    ```
    pip install .
    ```
    In both cases, it will find the setup.py file and take care of the rest.

You should then be set up to use the tools in the package!

## Usage

You are free to use any of the tools in the way you see fit, the tools should hopefully be general enough for different applications, but they also may need some tweaking. Refer to the other READMEs that are tool specific to see their specific usage sections.
- [GeoAttachmentSearth Usage](twobilliontoolkit/GeoAttachmentSeeker/README.md#usage)
- [RecordReviser Usage](twobilliontoolkit/RecordReviser/README.md#usage)
- [RippleUnzipple Usage](twobilliontoolkit/RippleUnzipple/README.md#usage)
- [SpatialTransformer Usage](twobilliontoolkit/SpatialTransformer/README.md#usage)


## Configuration

This section I will I will compile some of the configuration of all the other tools in a single place.

One of te first things that you must do when trying to use this package to insert or extract data from a database, is to fill in the information to establish a connection. This is needed for the Spatial Transformer tool. Navigate to [/twobilliontoolkit/SpatialTransformer/database.ini](/twobilliontoolkit/SpatialTransformer/database.ini) and fill out the postgresql section

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
This will allow you to connect to a database that you have set up, however you may need to make changes to the code or to the database to make sure everything works properly.

An issue that was found when using the RippleUnzipple tool in this package: You may run into an issue with your machines MAX_PATH_LENGTH being reached when trying to extract an extensive path with long directory names. On windows, to make sure this does not happen (Requires Users to have either Full Control or Special Permissions, if not available, contact an admin):

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

**Note**: There is a annoying use case where the RippleUnzipple tool will crash unexpectedly if one of the project folders within the root folder is named the same as the root folder (ie. root_folder/root_folder). It would be very easy to remidy this by just changing the compressed folder or the outputted unzipped folders name.

## Contributing

This project might not be maintained or up to date.

If you would like to contribute to twobilliontoolkit, follow these guidelines:

1. Submit bug reports or feature requests via the GitHub issue tracker.
2. Fork the repository, make your changes, and submit a pull request.

## License

This project is licensed under the MIT License. [Click here to view the license file](LICENSE) and review the terms and conditions of the MIT License.

## Contact

If you have any questions, feedback, or suggestions, you can reach out here:

- Anthony Rodway
- Email: anthony.rodway@nrcan-rncan.gc.ca

If I am not reachable, then please contact Andrea Nesdoly for any questions you may have. You may reach her at andrea.nesdoly@nrcan-rncan.gc.ca

Feel free to provide your input to help improve the twobilliontoolkit!
