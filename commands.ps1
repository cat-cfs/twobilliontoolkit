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
$toolkit_dir = ""
$input_path = ""
$output_path = ""
$master_data = ""
$gdb_name = "Output"
$gdb = "${gdb_name}.gdb"
$datatracker_name = "OutputDatatracker.xlsx"
$local_dir_path = "C:\LocalTwoBillionToolkit\Output"
$transfer_files = @("${gdb}", "${gdb_name}_Attachments", "${gdb_name}_Log_${datestamp}_ERROR.txt", "${gdb_name}_Log_${datestamp}_WARNING.txt")

# Define menu function
function Show-Menu {
    Clear-Host
    Write-Host "Choose an option:"
    Write-Host "1. Clone the ArcGIS Pro environement"
    Write-Host "2. Install/Update twobilliontoolkit package"
    Write-Host "3. Run Spatial Transformer"
    Write-Host "4. Resume Spatial Transformer from failure"
    Write-Host "5. Run Ripple Unzipple Independently"
    Write-Host "6. Run Network Transfer Independently"
    Write-Host "7. Exit"
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
            conda create --clone $ArcPro_original -p $ArcPro_clone --insecure
            Write-Host "The ArcGIS Pro environement has succefully been cloned!"
            Pause
        }
        "2" {
            Write-Host "Installing or Updating the twobilliontoolkit package..."
            Write-Host $python_exe -m pip install .
            & $python_exe -m pip install .
            Write-Host "The twobilliontoolkit has completed installing or updating!"
            Pause
        }
        "3" {
            Write-Host "Running Spatial Transformer..."
            Write-Host $python_exe "$toolkit_dir\SpatialTransformer\spatial_transformer.py" --load database --save database --input_path "$input_path" --output_network_path "$output_path" --gdb "$gdb" --datatracker "$datatracker_name" --master "$master_data" --suppress
            & $python_exe "$toolkit_dir\SpatialTransformer\spatial_transformer.py" --load database --save database --input_path "$input_path" --output_network_path "$output_path" --gdb "$gdb" --datatracker "$datatracker_name" --master "$master_data" --suppress
            Write-Host "The SpatialTransformer has completed its processing!"
            Pause
        }
        "4" {
            Write-Host "Resuming Spatial Transformer from failure..."
            Write-Host $python_exe "$toolkit_dir\SpatialTransformer\spatial_transformer.py" --load database --save database --input_path "$input_path" --output_network_path "$output_path" --gdb "$gdb" --datatracker "$datatracker_name" --master "$master_data" --suppress --resume
            & $python_exe "$toolkit_dir\SpatialTransformer\spatial_transformer.py" --load database --save database --input_path "$input_path" --output_network_path "$output_path" --gdb "$gdb" --datatracker "$datatracker_name" --master "$master_data" --suppress --resume
            Write-Host "The SpatialTransformer has completed its processing!"
            Pause
        }
        "5" {
            Write-Host "Running Ripple Unzipple Independently..."
            Write-Host $python_exe "$toolkit_dir\RippleUnzipple\ripple_unzipple.py" --input "$input_path" --output "$local_dir_path"
            & $python_exe "$toolkit_dir\RippleUnzipple\ripple_unzipple.py" --input "$input_path" --output "$local_dir_path"
            Write-Host "RippleUnzipple has completed its processing!"
            Pause
        }
        "6" {
            Write-Host "Running Network Transfer Independently..."
            Write-Host $python_exe "$toolkit_dir\SpatialTransformer\network_transfer.py" "$local_dir_path" "$output_path" --files $transfer_files
            & $python_exe "$toolkit_dir\SpatialTransformer\network_transfer.py" "$local_dir_path" "$output_path" --files $transfer_files
            Write-Host "Network Transfer has completed its processing!"
            Pause
        }
        "7" {
            break
        }
        default {
            Write-Host "Invalid choice. Please try again."
            Pause
        }
    }
} while ($choice -ne "7")