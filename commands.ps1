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
$ArcPro_PYENV = "C:\Users\$username\AppData\Local\Programs\ArcGIS\Pro\bin\Python\Scripts\proenv.bat"
$ArcPro_original = "C:\Users\$username\AppData\Local\Programs\ArcGIS\Pro\bin\Python\envs\arcgispro-py3"
$ArcPro_clone = "C:\Users\$username\AppData\Local\ESRI\conda\envs\arcgispro-py3-clone"
$python_exe = "$ArcPro_clone\python.exe"
$toolkit_dir = "..."
$input_path = "..."
$output_path = "..."
$master_data = "..."
$load = "database"
$save = "database"
$gdb_name = "Output"
$gdb = "${gdb_name}.gdb"
$gdb_path = "...\${gdb}"
$datatracker = "OutputDatatracker.xlsx"
$datatracker_path = "...\${datatracker}"
$local_dir_path = "C:\LocalTwoBillionToolkit"
$transfer_files = @("${gdb}", "${gdb_name}_Attachments", "${gdb_name}_Log_${datestamp}_ERROR.txt", "${gdb_name}_Log_${datestamp}_WARNING.txt")

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
    Write-Host "9. Exit"
}

# Main loop
do {
    Show-Menu
    $choice = Read-Host "Enter your choice"

    switch ($choice) {
        "1" {
            Write-Host "Cloning the ArcGIS Pro environement..."
            Write-Host $ArcPro_PYENV 
            & $ArcPro_PYENV 
            Write-Host conda create --clone $ArcPro_original -p $ArcPro_clone --insecure
            Write-Host
            conda create --clone $ArcPro_original -p $ArcPro_clone --insecure
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
            Write-Host $python_exe "$toolkit_dir\twobilliontoolkit\SpatialTransformer\spatial_transformer.py" --load $load --save $save --input_path "$input_path" --output_path "$output_path" --gdb_path "$gdb_path" --datatracker "$datatracker" --master "$master_data" --suppress
            Write-Host
            & $python_exe "$toolkit_dir\twobilliontoolkit\SpatialTransformer\spatial_transformer.py" --load $load --save $save --input_path "$input_path" --output_path "$output_path" --gdb_path "$gdb_path" --datatracker "$datatracker" --master "$master_data" --suppress
            Write-Host
            Write-Host "The SpatialTransformer has completed its processing!"
            Pause
        }
        "4" {
            Write-Host "Resuming Spatial Transformer from failure..."
            Write-Host $python_exe "$toolkit_dir\twobilliontoolkit\SpatialTransformer\spatial_transformer.py" --load $load --save $save --input_path "$input_path" --output_path "$output_path" --gdb_path "$gdb_path" --datatracker "$datatracker" --master "$master_data" --suppress --resume
            Write-Host
            & $python_exe "$toolkit_dir\twobilliontoolkit\SpatialTransformer\spatial_transformer.py" --load $load --save $save --input_path "$input_path" --output_path "$output_path" --gdb_path "$gdb_path" --datatracker "$datatracker" --master "$master_data" --suppress --resume
            Write-Host
            Write-Host "The SpatialTransformer has completed its processing!"
            Pause
        }
        "5" {
            Write-Host "Running Ripple Unzipple Independently..."
            Write-Host $python_exe "$toolkit_dir\twobilliontoolkit\RippleUnzipple\ripple_unzipple.py" --input "$input_path" --output "$output_path"
            Write-Host
            & $python_exe "$toolkit_dir\twobilliontoolkit\RippleUnzipple\ripple_unzipple.py" --input "$input_path" --output "$output_path"
            Write-Host
            Write-Host "Ripple Unzipple has completed its processing!"
            Pause
        }
        "6" {
            Write-Host "Running Geo Attachment Seeker Independently..."
            Write-Host $python_exe "$toolkit_dir\twobilliontoolkit\GeoAttachmentSeeker\geo_attachment_seeker.py" "$gdb_path" $output_path
            Write-Host
            & $python_exe "$toolkit_dir\twobilliontoolkit\GeoAttachmentSeeker\geo_attachment_seeker.py" "$gdb_path" $output_path
            Write-Host
            Write-Host "Geo Attachment Seeker has completed its processing!"
            Pause
        }
        "7" {
            Write-Host "Running Network Transfer Independently..."
            Write-Host $python_exe "$toolkit_dir\twobilliontoolkit\SpatialTransformer\network_transfer.py" "$local_dir_path" "$output_path" --files $transfer_files
            Write-Host
            & $python_exe "$toolkit_dir\twobilliontoolkit\SpatialTransformer\network_transfer.py" "$local_dir_path" "$output_path" --files $transfer_files
            Write-Host
            Write-Host "Network Transfer has completed its processing!"
            Pause
        }
        "8" {
            Write-Host "Running Record Reviser Independently..."
            Write-Host $python_exe "$toolkit_dir\twobilliontoolkit\RecordReviser\record_reviser.py" --gdb "$gdb_path" --load $load --save $save --datatracker "$datatracker_path"
            Write-Host
            & $python_exe "$toolkit_dir\twobilliontoolkit\RecordReviser\record_reviser.py" --gdb "$gdb_path" --load $load --save $save --datatracker "$datatracker_path"
            Write-Host
            Write-Host "Record Reviser has completed its processing!"
            Pause
        }
        "9" {
            break
        }
        default {
            Write-Host "Invalid choice. Please try again."
            Pause
        }
    }
} while ($choice -ne "9")