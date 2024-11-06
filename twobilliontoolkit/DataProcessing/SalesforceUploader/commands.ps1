# _____________________________________________________________
# Author: Anthony Rodway (anthony.rodway@nrcan-rncan.gc.ca) with help from Andrea Nesdoly (andrea.nesdoly@nrcan-rncan.gc.ca)
# Date Created: July 10, 2024 
# Last Updated: July 10, 2024

# A script for easily running the data processing tools in the twobilliontoolkit.     
# _____________________________________________________________

# Get current date in YYYY-MM-DD format
$datestamp = Get-Date -Format "yyyy-MM-dd"

# Get current user username
$username = $env:USERNAME

# Define Variables
$toolkit_dir = "..."

$debug_mode = $false  # or $debug_mode = 0
$script_location = $MyInvocation.MyCommand.Path

# Define menu function
function Show-Menu {
    # Clear-Host
    Write-Host "Choose an option:"
    Write-Host "1. Install/Update twobilliontoolkit package"
    Write-Host "2. Run the Buffer Builder"
    Write-Host "3. Exit"
}

# Main loop
do {
    Show-Menu
    $choice = Read-Host "Enter your choice"

    switch ($choice) {
        "1" {
            Write-Host "Installing or Updating the twobilliontoolkit package..."
            Write-Host python -m pip install $toolkit_dir
            Write-Host
            & python -m pip install $toolkit_dir
            Write-Host
            Write-Host "The twobilliontoolkit has completed installing or updating!"
            Pause
        }
        "2" {
            Write-Host "Running Salesforce Uploader..."

            Write-Host
            Write-Host "The Salesforce Uploader has completed its processing!"
            Pause
        }
        "3" {
            break
        }
        default {
            Write-Host "Invalid choice. Please try again."
            Pause
        }
    }
} while ($choice -ne "3")