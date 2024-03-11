using ArcGIS.Desktop.Core.Geoprocessing;
using ArcGIS.Desktop.Framework.Threading.Tasks;
using ArcGIS.Desktop.Mapping;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.RegularExpressions;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;


namespace twobillionarcgisaddin
{
    /// <summary>
    /// Interaction logic for TwoBillionTreesToolLogisticsView.xaml
    /// </summary>
    public partial class TwoBillionTreesToolLogisticsView : UserControl
    {
        // ******************************************************
        // Global Variables
        // ******************************************************

        // Store the output of the SiteMapper tool
        public string siteMapperToolOutput { get; private set; }

        // Access to the data container object of the SiteMapper tool
        public DataContainer dataContainer { get; private set; }


        // ******************************************************
        // Constructor
        // ******************************************************

        private static TwoBillionTreesToolLogisticsView _this = null;
        static public TwoBillionTreesToolLogisticsView MyTwoBillionTreesToolLogisticsView => _this;
        public TwoBillionTreesToolLogisticsView()
        {
            InitializeComponent();

            _this = this;

            // TODO: Remove default values
            this.ArcPythonToolboxPath.Text = @"\\vic-fas1\projects_a\2BT\02_Tools\twobilliontoolkit\twobillionarcgistoolboxes\twobillionarcgistoolboxes.pyt";
            this.ArcConnectionFilePath.Text = @"\\vic-fas1\projects_a\2BT\02_Tools\EsriAddIns\database_connection.sde";
            this.DatabaseSchema.Text = "bt_spatial_test";
        }

        // ******************************************************
        // Event Functions (Button Clicks, Toggles, ...)
        // ******************************************************

        // Method to handle the click event of the Establish Connection button
        private async void EstablishButtonClicked(object sender, RoutedEventArgs e)
        {
            try
            {
                // Disable the button (spam prevention)
                this.EstablishConnectionButton.IsEnabled = false;

                bool success = await ExecuteEstablishConnectionAsync();
                if (!success)
                {
                    return;
                }

                // Toggle visibility of UI elements
                if (this.UserForm.Visibility == Visibility.Visible)
                {
                    this.UserForm.Visibility = Visibility.Collapsed;
                    this.ButtonToolist.Visibility = Visibility.Visible;
                }
            }
            catch (Exception ex)
            {
                // Handle any exceptions that occur during tool execution
                ArcGIS.Desktop.Framework.Dialogs.MessageBox.Show($"Error: {ex.Message}", "Error");
            }

            this.EstablishConnectionButton.IsEnabled = true;
        }

        // Method to handle the click event of the Browse button
        private void BrowseButtonClicked(object sender, RoutedEventArgs e)
        {
            Microsoft.Win32.OpenFileDialog openFileDialog = new Microsoft.Win32.OpenFileDialog();

            // Set filter for file extension and default file extension
            openFileDialog.Filter = "All files (*.*)|*.*";

            // Display OpenFileDialog by calling ShowDialog method
            bool? result = openFileDialog.ShowDialog();

            // Get the selected file name and display in the TextBox
            if (result == true)
            {
                if (sender == this.ArcPythonToolboxButton)
                {
                    this.ArcPythonToolboxPath.Text = openFileDialog.FileName;
                }
                else if (sender == this.ArcConnectionFileButton)
                {
                    this.ArcConnectionFilePath.Text = openFileDialog.FileName;
                }
            }
        }

        // Method to handle the click event of the Back button
        private void BackButtonClicked(object sender, RoutedEventArgs e)
        {
            if (this.BackButton.Visibility == Visibility.Visible)
            {
                this.ButtonToolist.Visibility = Visibility.Visible;
                this.SiteMapper.Visibility = Visibility.Collapsed;
            }
        }

        // Method to handle the click event of the SiteMapper button
        private async void SiteMapperButtonClicked(object sender, RoutedEventArgs e)
        {
            try
            {
                // Disable the button (spam prevention)
                this.SiteMapperButton.IsEnabled = false;

                TwoBillionTreesDockpaneViewModel2.Show();

                // If the global has not already been populated
                if (string.IsNullOrEmpty(siteMapperToolOutput))
                {
                    bool success = await ExecuteRetrieveDataToolAsync();
                    if (!success)
                    {
                        return;
                    }
                }

                // Toggle visibility of UI elements
                if (this.ButtonToolist.Visibility == Visibility.Visible)
                {
                    this.ButtonToolist.Visibility = Visibility.Collapsed;
                    this.SiteMapper.Visibility = Visibility.Visible;
                }
            }
            catch (Exception ex)
            {
                // Handle any exceptions that occur during tool execution
                ArcGIS.Desktop.Framework.Dialogs.MessageBox.Show($"Error: {ex.Message}", "Error");
            }

            this.SiteMapperButton.IsEnabled = true;
        }

        // Method to handle the click event of overwrite toggle
        private void OverwriteSwitchToggled(object sender, RoutedEventArgs e)
        {
            // Swap the tooltip of the switch
            if ((bool)this.OverwriteToggle.IsChecked)
            {
                this.OverwriteToggle.ToolTip = "Toggle Off";
            } 
            else
            {
                this.OverwriteToggle.ToolTip = "Toggle On";
            }
        }

        // Method to handle the click event of the Send Data button
        private async void SendButtonClicked(object sender, RoutedEventArgs e)
        {
            try
            {
                // Disable the button (spam prevention)
                this.SendDataButton.IsEnabled = false;

                //
                this.SiteMapper_SuccessStatus.Visibility = Visibility.Collapsed;
                this.SiteMapper_ErrorStatus.Visibility = Visibility.Collapsed;

                // Access the current map in ArcGIS Pro
                MapView mapView = MapView.Active;
                if (mapView != null)
                {
                    string selectedGeometry = null;
                    await QueuedTask.Run(() =>
                    {
                        // Get the currently selected features in the map
                        var selectedFeatures = mapView.Map.GetSelection();

                        // Get the first layer and its corresponding selected feature OIDs
                        var selectionSet = selectedFeatures.ToDictionary();
                        if (selectionSet.Count == 0)
                        {
                            ArcGIS.Desktop.Framework.Dialogs.MessageBox.Show("No features on the map are selected, please select a feature you want to process and try again!");
                            this.SendDataButton.IsEnabled = true;
                            return;
                        }

                        // Create an instance of the inspector class
                        var inspector = new ArcGIS.Desktop.Editing.Attributes.Inspector();

                        // Load the selected features into the inspector using a list of object IDs
                        inspector.Load(selectionSet.Keys.First(), selectionSet.Values.First());

                        // Assuming the inspector.Shape represents the geometry of the selected feature
                        selectedGeometry = inspector.Shape.ToJson();
                    });
                   
                    await ExecuteInsertDataToolAsync($"{SiteID_Dropdown.SelectedItem}, {selectedGeometry}");
                }
            }
            catch (Exception ex)
            {
                // Handle any exceptions that occur during tool execution
                ArcGIS.Desktop.Framework.Dialogs.MessageBox.Show($"Error: {ex.Message}", "Error");
            }

            this.SendDataButton.IsEnabled = true;
        }

        // Method to handle the change event of the filters
        private void SiteMapperFilterChanged(object sender, SelectionChangedEventArgs e)
        {
            if (sender == this.ProjectNumber_Dropdown)
            {
                // Create a DataContainer instance to process the JSON string
                dataContainer = new DataContainer(siteMapperToolOutput);

                //
                PopulateFilters(dataContainer, true);

                if (string.IsNullOrEmpty(this.ProjectNumber_Dropdown.SelectedItem as string))
                {
                    this.SiteID_Dropdown.SelectedItem = "";
                    this.Secondary_Filter.Visibility = Visibility.Collapsed;
                }
                else
                {
                    this.Secondary_Filter.Visibility = Visibility.Visible;
                }
            }

            Dictionary<string, string> filter = GetSiteMapperFilter();

            // Repopulate the data grid with the filtered data
            SiteMapperDataGridView dockpane2 = SiteMapperDataGridView.MySiteMapperDataGridView;
            dockpane2.PopulateDataGrid(dataContainer, filter);

            // Filter map layers based on the selected project number
            SelectMapLayers(filter["ProjectNumber"]);
        }

        // ******************************************************
        // Various Helper Functions
        // ******************************************************

        // Method to get the selected filter values for the SiteMapper tool
        public Dictionary<string, string> GetSiteMapperFilter()
        {
            // Get the selected dropdown project number
            string projectNumberSelected = this.ProjectNumber_Dropdown.SelectedItem as string;
            string siteIdSelected = this.SiteID_Dropdown.SelectedItem as string;

            return new Dictionary<string, string>
            {
                { "ProjectNumber", projectNumberSelected },
                { "SiteID", siteIdSelected },
            };
        }

        // Method to populate filters for the SiteMapper tool
        private void PopulateFilters(DataContainer container, bool updateSecondaryFilter = false)
        {
            string selectedItem = (string)this.ProjectNumber_Dropdown.SelectedItem;

            // Initialize filter lists with an empty string as the default value
            List<string> filterProjNumberList = new List<string>() { "" };
            List<string> filterSiteIDList = new List<string>() { "" };

            foreach (DataEntry dataEntry in container.Data)
            {
                bool isMatchingProject = string.IsNullOrEmpty(selectedItem) || selectedItem == dataEntry.ProjectNumber;

                if (updateSecondaryFilter)
                {
                    if (!isMatchingProject)
                    {
                        continue;
                    }
                }
                else
                {
                    if (!filterProjNumberList.Contains(dataEntry.ProjectNumber))
                    {
                        filterProjNumberList.Add(dataEntry.ProjectNumber);
                    }
                }

                // Common for both primary and secondary filters
                if (!filterSiteIDList.Contains(dataEntry.SiteID))
                {
                    filterSiteIDList.Add(dataEntry.SiteID);
                }
            }

            // Set ItemSource based on the filter type
            if (!updateSecondaryFilter)
            {
                ProjectNumber_Dropdown.ItemsSource = filterProjNumberList;
            }

            SiteID_Dropdown.ItemsSource = filterSiteIDList;
        }

        // Method to select map layers based on the selected project number
        private void SelectMapLayers(string projectNumber)
        {
            // Access the current map in ArcGIS Pro
            MapView mapView = MapView.Active;

            if (mapView != null)
            {
                // Remove spaces, dashes, and underscores
                string projectNumberNormalized = Regex.Replace(projectNumber, @"[-_ ]", "");
                QueuedTask.Run(() =>
                {
                    // Iterate through each layer in the map
                    foreach (Layer layer in mapView.Map.Layers)
                    {
                        // Remove spaces, dashes, and underscores
                        string layerNormalized = Regex.Replace(layer.Name, @"[-_ ]", "");

                        if (layer is FeatureLayer featureLayer)
                        {
                            // Check if the layer has the necessary attribute for filtering
                            if (Regex.IsMatch(layerNormalized, projectNumberNormalized) && projectNumber != "")
                            {
                                featureLayer.Select();
                            }
                            else
                            {
                                featureLayer.ClearSelection();
                            };
                        }
                    }

                });
            }
        }

        // ******************************************************
        // Asyncronous Database Functions
        // ******************************************************

        // Method to execute the Establish Connection tool asynchronously
        private async Task<bool> ExecuteEstablishConnectionAsync()
        {
            try
            {
                // Set the parameters
                string toolboxPath = this.ArcPythonToolboxPath.Text + "\\EstablishConnectionTool";
                string connectionFile = this.ArcConnectionFilePath.Text;
                string tableName = this.DatabaseSchema.Text + ".site_mapping";

                // Execute the Python tool and get the result
                var parameters = Geoprocessing.MakeValueArray(connectionFile, tableName);
                var returnValue = await Geoprocessing.ExecuteToolAsync(toolboxPath, parameters);

                if (!returnValue.IsFailed)
                {
                    return true;
                }
            }
            catch (Exception ex)
            {
                // Handle any exceptions that occur during tool execution
                ArcGIS.Desktop.Framework.Dialogs.MessageBox.Show($"Error: {ex.Message}", "Error");
            }

            return false;
        }

        // Method to execute the Retrieve Data tool asynchronously
        private async Task<bool> ExecuteRetrieveDataToolAsync()
        {
            try
            {
                // Set the parameters
                string toolboxPath = this.ArcPythonToolboxPath.Text + "\\ReadDataTool";
                string connectionFile = this.ArcConnectionFilePath.Text;
                string tableName = this.DatabaseSchema.Text + ".site_mapping";

                // Execute the Python tool and get the result
                var parameters = Geoprocessing.MakeValueArray(connectionFile, tableName);
                var toolOuput = await Geoprocessing.ExecuteToolAsync(toolboxPath, parameters);
                siteMapperToolOutput = toolOuput.ReturnValue;

                // Check if the tool ran correctly by checking the output
                if (string.IsNullOrEmpty(siteMapperToolOutput))
                {
                    return false;
                }

                // Create a DataContainer instance to process the JSON string
                dataContainer = new DataContainer(siteMapperToolOutput);

                //
                PopulateFilters(dataContainer);

                // Populate the data grid with the output data
                SiteMapperDataGridView dockpane2 = SiteMapperDataGridView.MySiteMapperDataGridView;
                dockpane2.PopulateDataGrid(dataContainer);

                return true;
            }
            catch (Exception ex)
            {
                // Handle any exceptions that occur during tool execution
                ArcGIS.Desktop.Framework.Dialogs.MessageBox.Show($"Error: {ex.Message}", "Error");
                return false;
            }
        }

        // Method to execute the Insert Data tool asynchronously
        private async Task<bool> ExecuteInsertDataToolAsync(string insertData)
        {
            try
            {
                // Set the parameters
                string toolboxPath = this.ArcPythonToolboxPath.Text + "\\UpdateDataTool";
                string connectionFile = this.ArcConnectionFilePath.Text;
                string tableName = this.DatabaseSchema.Text + ".site_geometry";

                // Execute the Python tool and get the result
                var parameters = Geoprocessing.MakeValueArray(connectionFile, tableName, insertData);
                var returnValue = await Geoprocessing.ExecuteToolAsync(toolboxPath, parameters);

                if (!returnValue.IsFailed)
                {
                    this.SiteMapper_ErrorStatus.Visibility = Visibility.Collapsed;
                    this.SiteMapper_SuccessStatus.Visibility = Visibility.Visible;
                    return true;
                }                
            }
            catch (Exception ex)
            {
                // Handle any exceptions that occur during tool execution
                ArcGIS.Desktop.Framework.Dialogs.MessageBox.Show($"Error: {ex.Message}", "Error");
            }

            this.SiteMapper_SuccessStatus.Visibility = Visibility.Collapsed;
            this.SiteMapper_ErrorStatus.Visibility = Visibility.Visible;
            return false;
        }

    }
}
