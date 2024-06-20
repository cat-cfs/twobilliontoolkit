# _____________________________________________________________
# Author: Anthony Rodway (anthony.rodway@nrcan-rncan.gc.ca) with help from Andrea Nesdoly (andrea.nesdoly@nrcan-rncan.gc.ca)
# Date Created: June 20, 2024 
# Last Updated: June 20, 2024

# A script for easily running the data processing tools in the twobilliontoolkit.     

# _____________________________________________________________

# Get current date in YYYY-MM-DD format
$datestamp = Get-Date -Format "yyyy-MM-dd"

# Get current user username
$username = $env:USERNAME

# Define Variables
$toolkit_dir = "..."
$master_datasheet = "..." 
$database_init = "..." 
$debug_mode = $true  # or $debug_mode = 0
$script_location = $MyInvocation.MyCommand.Path

# Define menu function
function Show-Menu {
    # Clear-Host
    Write-Host "Choose an option:"
    Write-Host "1. Run the Buffer Builder"
    Write-Host "2. Exit"
}

# Main loop
do {
    Show-Menu
    $choice = Read-Host "Enter your choice"

    switch ($choice) {
        "1" {
            Write-Host "Running Buffer Builder..."
            if ($debug_mode) 
            {
                Write-Host python "$toolkit_dir\twobilliontoolkit\BufferBuilder\buffer_builder.py" --datasheet $master_datasheet --init $database_init --debug
                Write-Host
                & python "$toolkit_dir\twobilliontoolkit\BufferBuilder\buffer_builder.py" --datasheet $master_datasheet --init $database_init --debug
            }
            else 
            {
                Write-Host python "$toolkit_dir\twobilliontoolkit\BufferBuilder\buffer_builder.py" --datasheet $master_datasheet --init $database_init
                Write-Host
                & python "$toolkit_dir\twobilliontoolkit\BufferBuilder\buffer_builder.py" --datasheet $master_datasheet --init $database_init
            }
            Write-Host
            Write-Host "The Buffer Builder has completed its processing!"
            Pause
        }
        "2" {
            break
        }
        default {
            Write-Host "Invalid choice. Please try again."
            Pause
        }
    }
} while ($choice -ne "2")