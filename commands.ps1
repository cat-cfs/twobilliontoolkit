# _____________________________________________________________
# Author: Anthony Rodway (anthony.rodway@nrcan-rncan.gc.ca) with help from Andrea Nesdoly (andrea.nesdoly@nrcan-rncan.gc.ca)
# Date Created: April 9, 2024 
# Last Updated: April 9, 2024

# A script for easily running the tools in the twobilliontoolkit.     

# **
# Ensure ArcPro is installed: contact andrea.nesdoly@nrcan-rncan.gc.ca for installation instructions
# **
# _____________________________________________________________

# Get current date in YYYY-MM-DD format
$datestamp = Get-Date -Format "yyyy-MM-dd"

# Get current user username
$username = $env:USERNAME

# Define Variables
$ArcPro_original = "C:\Users\$username\AppData\Local\Programs\ArcGIS\Pro\bin\Python\envs\arcgispro-py3"
$ArcPro_clone = "C:\Users\$username\AppData\Local\ESRI\conda\envs\arcgispro-py3-clone"
$python_exe = "$ArcPro_clone\python.exe"
$toolkit_dir = "..."
$input_path = "..."
$output_path = "..."
$master_data = "..."
$database_config = "..."
$load = "database"
$save = "database"
$log_path = "..." # Not for spatial transformer, for running individual tools seperately 
$gdb_output = "..."
$gdb_name = "Output"
$gdb = "${gdb_name}.gdb"
$gdb_path = "${gdb_output}\${gdb}"
$datatracker = "OutputDatatracker.xlsx"
$datatracker_path = "${gdb_output}\${datatracker}"
$local_dir_path = "C:\LocalTwoBillionToolkit"
$transfer_files = @("${gdb}", "${gdb_name}_Attachments", "${gdb_name}_Log_${datestamp}_ERROR.txt", "${gdb_name}_Log_${datestamp}_WARNING.txt")
$year = "..."
$debug_mode = $false  # or $debug_mode = 0
$skip_unzip = $true
$suppress = $true
$script_location = $MyInvocation.MyCommand.Path


# Define menu function
function Show-Menu {
    # Clear-Host
    Write-Host "Choose an option:"
    Write-Host "1. Clone the ArcGIS Pro environement"
    Write-Host "2. Install/Update twobilliontoolkit package"
    Write-Host "3. Run Spatial Transformer"
    Write-Host "4. Resume Spatial Transformer from failure"
    Write-Host "5. Run Ripple Unzipple Independently"
    Write-Host "6. Run Attachment Seeker Independently"
    Write-Host "7. Run Network Transfer Independently"
    Write-Host "8. Run Record Reviser Independently"
    Write-Host "9. Remove contents from the temporary local directory"
    Write-Host "10. Exit"
}

# Main loop
do {
    Show-Menu
    $choice = Read-Host "Enter your choice"

    switch ($choice) {
        "1" {
            Write-Host "Cloning the ArcGIS Pro environement..."
            Write-Host conda config --set ssl_verify false
            Write-Host
            conda config --set ssl_verify false
            Write-Host
            Write-Host conda create --clone $ArcPro_original -p $ArcPro_clone
            Write-Host
            conda create --clone $ArcPro_original -p $ArcPro_clone
            Write-Host conda activate $ArcPro_clone
            Write-Host
            conda activate $ArcPro_clone
            Write-Host
            Write-Host conda config --set ssl_verify true
            Write-Host
            conda config --set ssl_verify true
            Write-Host
            Write-Host "The ArcGIS Pro environement has succefully been cloned!"
            Pause
        }
        "2" {
            Write-Host "Installing or Updating the twobilliontoolkit package..."
            Write-Host $python_exe -m pip install $toolkit_dir
            Write-Host
            & $python_exe -m pip install $toolkit_dir
            Write-Host
            Write-Host "The twobilliontoolkit has completed installing or updating!"
            Pause
        }
        "3" {
            Write-Host "Running Spatial Transformer..."
            # if ($debug_mode) 
            # {
            #     Write-Host $python_exe "$toolkit_dir\twobilliontoolkit\SpatialTransformer\spatial_transformer.py" --load $load --save $save --input_path "$input_path" --output_path "$output_path" --gdb_path "$gdb_path" --datatracker "$datatracker" --master "$master_data" --ini "$database_config" --suppress --debug --ps_script "$script_location" --year "$year"
            #     Write-Host
            #     & $python_exe "$toolkit_dir\twobilliontoolkit\SpatialTransformer\spatial_transformer.py" --load $load --save $save --input_path "$input_path" --output_path "$output_path" --gdb_path "$gdb_path" --datatracker "$datatracker" --master "$master_data" --ini "$database_config" --suppress --debug --ps_script "$script_location" --year "$year"
            
            # }
            # else 
            # {
            #     Write-Host $python_exe "$toolkit_dir\twobilliontoolkit\SpatialTransformer\spatial_transformer.py" --load $load --save $save --input_path "$input_path" --output_path "$output_path" --gdb_path "$gdb_path" --datatracker "$datatracker_path" --master "$master_data" --ini "$database_config" --suppress --ps_script "$script_location" --year "$year"
            #     Write-Host
            #     & $python_exe "$toolkit_dir\twobilliontoolkit\SpatialTransformer\spatial_transformer.py" --load $load --save $save --input_path "$input_path" --output_path "$output_path" --gdb_path "$gdb_path" --datatracker "$datatracker_path" --master "$master_data" --ini "$database_config" --suppress --ps_script "$script_location" --year "$year"
            # }
            
            # Construct the base command arguments
            $args = @(
                "--load", $load
                "--save", $save
                "--input_path", "$input_path"
                "--output_path", "$output_path"
                "--gdb_path", "$gdb_path"
                "--datatracker", "$datatracker"
                "--master", "$master_data"
                "--ini", "$database_config"
                "--ps_script", "$script_location"
                "--year", "$year"
            )

            # Conditionally add flags
            if ($skip_unzip) { $args += "--skip_unzip" }
            if ($debug)      { $args += "--debug" }
            if ($suppress)   { $args += "--suppress" }

            # Print out the command
            Write-Host $python_exe "$toolkit_dir\twobilliontoolkit\SpatialTransformer\spatial_transformer.py" @args
            Write-Host
            
            # Execute the command
            & $python_exe "$toolkit_dir\twobilliontoolkit\SpatialTransformer\spatial_transformer.py" @args

            Write-Host
            Write-Host "The SpatialTransformer has completed its processing!"
            Pause
        }
        "4" {
            Write-Host "Resuming Spatial Transformer from failure..."
            if ($debug_mode)
            {
                Write-Host $python_exe "$toolkit_dir\twobilliontoolkit\SpatialTransformer\spatial_transformer.py" --load $load --save $save --input_path "$input_path" --output_path "$output_path" --gdb_path "$gdb_path" --datatracker "$datatracker" --master "$master_data" --ini "$database_config" --suppress --debug --resume --ps_script "$script_location" --year "$year"
                Write-Host
                & $python_exe "$toolkit_dir\twobilliontoolkit\SpatialTransformer\spatial_transformer.py" --load $load --save $save --input_path "$input_path" --output_path "$output_path" --gdb_path "$gdb_path" --datatracker "$datatracker" --master "$master_data" --ini "$database_config" --suppress --debug --resume --ps_script "$script_location" --year "$year"
            }
            else
            {
                Write-Host $python_exe "$toolkit_dir\twobilliontoolkit\SpatialTransformer\spatial_transformer.py" --load $load --save $save --input_path "$input_path" --output_path "$output_path" --gdb_path "$gdb_path" --datatracker "$datatracker" --master "$master_data" --ini "$database_config" --suppress --resume --ps_script "$script_location" --year "$year"
                Write-Host
                & $python_exe "$toolkit_dir\twobilliontoolkit\SpatialTransformer\spatial_transformer.py" --load $load --save $save --input_path "$input_path" --output_path "$output_path" --gdb_path "$gdb_path" --datatracker "$datatracker" --master "$master_data" --ini "$database_config" --suppress --resume --ps_script "$script_location" --year "$year"
            }
            Write-Host
            Write-Host "The SpatialTransformer has completed its processing!"
            Pause
        }
        "5" {
            Write-Host "Running Ripple Unzipple Independently..."
            Write-Host $python_exe "$toolkit_dir\twobilliontoolkit\RippleUnzipple\ripple_unzipple.py" --input "$input_path" --output "$output_path" --log "$log_path" --ps_script "$script_location"
            Write-Host
            & $python_exe "$toolkit_dir\twobilliontoolkit\RippleUnzipple\ripple_unzipple.py" --input "$input_path" --output "$output_path" --log "$log_path" --ps_script "$script_location"
            Write-Host
            Write-Host "Ripple Unzipple has completed its processing!"
            Pause
        }
        "6" {
            Write-Host "Running Geo Attachment Seeker Independently..."
            Write-Host $python_exe "$toolkit_dir\twobilliontoolkit\GeoAttachmentSeeker\geo_attachment_seeker.py" --gdb "$gdb_path" --output "$gdb_path" --log "$log_path" --ps_script "$script_location"
            Write-Host
            & $python_exe "$toolkit_dir\twobilliontoolkit\GeoAttachmentSeeker\geo_attachment_seeker.py" --gdb "$gdb_path" --output "$gdb_path" --log "$log_path" --ps_script "$script_location"
            Write-Host
            Write-Host "Geo Attachment Seeker has completed its processing!"
            Pause
        }
        "7" {
            Write-Host "Running Network Transfer Independently..."
            Write-Host $python_exe "$toolkit_dir\twobilliontoolkit\NetworkTransfer\network_transfer.py" --source "$local_dir_path" --destination "$gdb_output" --log "$log_path" --ps_script "$script_location" --files $transfer_files
            Write-Host
            & $python_exe "$toolkit_dir\twobilliontoolkit\NetworkTransfer\network_transfer.py" --source "$local_dir_path" --destination "$gdb_output" --log "$log_path" --ps_script "$script_location" --files $transfer_files
            Write-Host
            Write-Host "Network Transfer has completed its processing!"
            Pause
        }
        "8" {
            Write-Host "Running Record Reviser Independently..."
            Write-Host $python_exe "$toolkit_dir\twobilliontoolkit\RecordReviser\record_reviser.py" --gdb "$gdb_path" --load $load --save $save --datatracker "$datatracker_path" --ini "$database_config" --log "$log_path" --ps_script "$script_location"
            Write-Host
            & $python_exe "$toolkit_dir\twobilliontoolkit\RecordReviser\record_reviser.py" --gdb "$gdb_path" --load $load --save $save --datatracker "$datatracker_path" --ini "$database_config" --log "$log_path" --ps_script "$script_location"
            Write-Host
            Write-Host "Record Reviser has completed its processing!"
            Pause
        }
        "9" {
            Write-Host "Removing contents from local directory..."
            & Get-ChildItem -Path $local_dir_path | Remove-Item -Force -Recurse
            Write-Host "Local directory has been cleared!"
            Pause
        }
        "10" {
            break
        }
        default {
            Write-Host "Invalid choice. Please try again."
            Pause
        }
    }
} while ($choice -ne "10")