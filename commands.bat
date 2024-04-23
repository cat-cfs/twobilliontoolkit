@echo off

rem _____________________________________________________________
rem Author: Anthony Rodway (anthony.rodway@nrcan-rncan.gc.ca) with help from Andrea Nesdoly (andrea.nesdoly@nrcan-rncan.gc.ca)
rem Date Created: April 7, 2024 
rem Last Updated: April 9, 2024

rem A script for easily running the tools in the twobilliontoolkit.     

rem **
rem Ensure ArcPro is installed: contact andrea.nesdoly@nrcan-rncan.gc.ca for installation instructions
rem **
rem _____________________________________________________________

setlocal

rem Get current date in YYYY-MM-DD format
for /f "tokens=1-3 delims=/ " %%a in ("%DATE%") do (
    set "month=%%a"
    set "day=%%b"
    set "year=%%c"
)
set "datestamp=%year%-%month%-%day%"
set "datestamp=%datestamp:~1,-1%"

rem Define Variables
set "ArcPro_PYENV=C:\Users\%USERNAME%\AppData\Local\Programs\ArcGIS\Pro\bin\Python\Scripts\proenv.bat"
set "ArcPro_original=C:\Users\%USERNAME%\AppData\Local\Programs\ArcGIS\Pro\bin\Python\envs\arcgispro-py3"
set "ArcPro_clone=C:\Users\%USERNAME%\AppData\Local\ESRI\conda\envs\arcgispro-py3-clone"
set "python_exe=C:\Users\%USERNAME%\AppData\Local\ESRI\conda\envs\arcgispro-py3-clone\python.exe"
set "toolkit_dir=..."
set "input_path=..."
set "output_path=..."
set "master_data=..."
set "load=database"
set "save=database"
set "gdb_name=Output"
set "gdb=%gdb_name%.gdb"
set "gdb_path=...\%gdb%"
set "datatracker=OutputDatatracker.xlsx"
set "datatracker_path=...\%datatracker%"
set "local_dir_path=C:\LocalTwoBillionToolkit\Output"
set transfer_files="%gdb%" "%gdb_name%_Attachments" "%gdb_name%_Log_%datestamp%_ERROR.txt" "%gdb_name%_Log_%datestamp%_WARNING.txt"

:menu
cls
echo Choose an option:
echo 1. Clone the ArcGIS Pro environement
echo 2. Install/Update twobilliontoolkit package
echo 3. Run Spatial Transformer
echo 4. Resume Spatial Transformer from failure
echo 5. Run Ripple Unzipple Independantly
echo 6. Run Attachment Seeker Independently
echo 7. Run Network Transfer Independantly
echo 8. Run Record Reviser Independently
echo 9. Exit
set /p choice=Enter your choice: 

if "%choice%"=="1" goto command1
if "%choice%"=="2" goto command2
if "%choice%"=="3" goto command3
if "%choice%"=="4" goto command4
if "%choice%"=="5" goto command5
if "%choice%"=="6" goto command6
if "%choice%"=="7" goto command7
if "%choice%"=="8" goto command8
if "%choice%"=="9" goto :eof

echo Invalid choice. Please try again.
pause
goto menu

:command1
echo Cloning the ArcGIS Pro environement...
echo "%ArcPro_PYENV%" && conda create --clone "%ArcPro_original%" -p "%ArcPro_clone%" --insecure
echo
rem
"%ArcPro_PYENV%" && conda create --clone "%ArcPro_original%" -p "%ArcPro_clone%" --insecure
echo
echo The ArcGIS Pro environement has succefully been cloned!
pause
goto menu

:command2
echo Installing or Updating the twobilliontoolkit package...
echo "%python_exe%" -m pip install .
echo
rem
"%python_exe%" -m pip install .
echo
echo The twobilliontoolkit has completed installing or updating!
pause
goto menu

:command3
echo Running Spatial Transformer...
echo "%python_exe%" "%toolkit_dir%\SpatialTransformer\spatial_transformer.py" --load %load% --save %save% --input_path "%input_path%" --output_path "%output_path%" --gdb_path "%gdb_path%" --datatracker "%datatracker%" --master "%master_data%" --suppress
echo
rem
"%python_exe%" "%toolkit_dir%\SpatialTransformer\spatial_transformer.py" --load %load% --save %save% --input_path "%input_path%" --output_path "%output_path%" --gdb_path "%gdb_path%" --datatracker "%datatracker%" --master "%master_data%" --suppress
echo
echo The SpatialTransformer has completed its processing!
pause
goto menu

:command4
echo Resuming Spatial Transformer from failure...
echo "%python_exe%" "%toolkit_dir%\SpatialTransformer\spatial_transformer.py" --load %load% --save %save% --input_path "%input_path%" --output_path "%output_path%" --gdb_path "%gdb_path%" --datatracker "%datatracker%" --master "%master_data%" --suppress --resume
echo
rem
"%python_exe%" "%toolkit_dir%\SpatialTransformer\spatial_transformer.py" --load %load% --save %save% --input_path "%input_path%" --output_path "%output_path%" --gdb_path "%gdb_path%" --datatracker "%datatracker%" --master "%master_data%" --suppress --resume
echo
echo The SpatialTransformer has completed its processing!
pause
goto menu

:command5
echo Running Ripple Unzipple Independantly...
echo "%python_exe%" "%toolkit_dir%\RippleUnzipple\ripple_unzipple.py" --input "%input_path%" --output "%local_dir_path%"
echo
rem
"%python_exe%" "%toolkit_dir%\RippleUnzipple\ripple_unzipple.py" --input "%input_path%" --output "%local_dir_path%"
echo
echo RippleUnzipple has completed its processing!
pause
goto menu

:command6
echo Running Geo Attachment Seeker Independently...
echo "%python_exe%" "%toolkit_dir%\GeoAttachmentSeeker\geo_attachment_seeker.py" "%gdb_path%" "%output_path%"
echo
rem
"%python_exe%" "%toolkit_dir%\GeoAttachmentSeeker\geo_attachment_seeker.py" "%gdb_path%" "%output_path%"
echo
echo Geo Attachment Seeker has completed its processing!
pause
goto menu

:command7
echo Running Network Transfer Independantly...
echo "%python_exe%" "%toolkit_dir%\SpatialTransformer/network_transfer.py" "%local_dir_path%" "%output_path%" --files %transfer_files%
echo
rem
"%python_exe%" "%toolkit_dir%\SpatialTransformer/network_transfer.py"  "%local_dir_path%" "%output_path%" --files %transfer_files%
echo
echo Network Transfer has completed its processing!
pause
goto menu

:command8
echo Running Record Reviser Independently...
echo "%python_exe%" "%toolkit_dir%\RecordReviser\record_reviser.py" --gdb "%gdb_path%" --load "%load%" --save "%save%" --datatracker "%datatracker_path%"
echo
rem
"%python_exe%" "%toolkit_dir%\RecordReviser\record_reviser.py" --gdb "%gdb_path%" --load "%load%" --save "%save%" --datatracker "%datatracker_path%"
echo
echo Record Reviser has completed its processing!
pause
goto menu
