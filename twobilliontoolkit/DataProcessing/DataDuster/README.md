# Data Duster

## Project Description

This tool is used for cleaning and updating duplicate geometries in a database. It does so by updating each field in the site_geometry table which will trigger a database function to re-evaluate if each polygon has a exact duplicate or not.

## Table of Contents

- [Project Description](#project-description)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Additional Information](#additional-information)
- [Contributing](#contributing)
- [License](#license)

## Installation

The DataProcessing module of the twobilliontoolkit package is included in the installation of the package itself. Currently there is no easy way of downloading just one tool from the package because the tools depend on other tools within the package, but if you wish to use this tool, follow the installation process documented [in the package README](../../../README.md)

You should then be set up to use the tool!

## Usage

To use DataDuster, run the script from the command line with the following syntax:
```
python path/to/data_duster.py --ini path/to/db_config.ini --log path/to/log.txt
```
- `[-h, --help]` (optional): List all of the available commands and a description for help.
- `--ini` (required): Path to the database initialization file.
- `--log` (required): Path to the output log file.
- `--ps_script` (optional): Path to a PowerShell script for additional commands.
- `--debug` (optional): Flag to enable debug mode.

Example from the root of the project:
```
python ./twobilliontoolkit/DataProcessing/DataDuster/data_duster.py --ini ./twobilliontoolkit/SpatialTransformer/config.ini --log ./twobilliontoolkit/DataProcessing/DataDuster/log.txt
```

A preloaded commands powershell script is ready for you to use [here](./commands.ps1) you will just need to change out some variables labelled as "..." and then run the script by 
```
./commands.ps1
```
and following the walkthrough

You also have the option of calling this tool from a module import with the following syntax:
```
from twobilliontoolkit.DataProcessing.DataDuster.data_duster import data_duster

def main():
    db_config = 'path/to/config.ini'
    log_path = 'path/to/log.txt'
    
    # Call the handler function
    data_duster(db_config=db_config, log_path=log_path)
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

## Additional Information

This tool script will most likely be doing multiple things in the future, and among the functionality there is a function called update_database_duplicate_geometries() which updates the rows to re-evaluate the duplicate geometries that are logged in the site_geometry table.

I will briefly explain how those are calculated in the first place and show the trigger and function combination that allows this to be possible.

The field in site_geometry is populated when there is an update or insert on the table with the following trigger. The schema will be replace with a placeholder {schema} to avoid confusion if you were to copy and paste the code.

```
CREATE TRIGGER update_duplicate_geometry_ids_trigger 
BEFORE INSERT OR UDPATE 
ON {schema}.site_geometry 
FOR EACH ROW EXECUTE FUNCTION {schema}.update_duplicate_geometry_ids()
```

This trigger will call the function called update_duplicate_geometry_ids()

```
CREATE OR REPLACE FUNCTION bt.update_duplicate_geometry_ids()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
	BEGIN
	    -- Fetching the list of duplicate ids for the current NEW.geom
	    SELECT string_agg(CAST(id AS TEXT), ', ') INTO NEW.duplicate_geometry_ids
	    FROM (
	        SELECT 
	            id, 
	            geom, 
	            COUNT(*) OVER(PARTITION BY geom) AS num_occurrences
	        FROM ONLY bt.site_geometry 
	        WHERE dropped = false
	    ) AS duplicates
	    WHERE geom = NEW.geom AND id != NEW.id;
	    
	    RETURN NEW;
	END;
$function$;
```

It is designed to update the duplicate_geometry_ids field for a new or updated geometry entry (NEW.geom) in the bt.site_geometry table. Specifically, it identifies other entries in the table that share the same geometry but have a different id. These duplicate IDs are then aggregated and stored as a comma-separated string in the NEW.duplicate_geometry_ids field.


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

Feel free to provide your input to help improve Data Duster!