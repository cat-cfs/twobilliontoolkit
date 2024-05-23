using ArcGIS.Core.Data;
using ArcGIS.Core.Geometry;
using ArcGIS.Desktop.Core.Geoprocessing;
using ArcGIS.Desktop.Framework.Dialogs;
using ArcGIS.Desktop.Framework.Threading.Tasks;
using ArcGIS.Desktop.Internal.Mapping.CommonControls;
using ArcGIS.Desktop.Mapping;
using ArcGIS.Desktop.Mapping.Events;
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Linq;
using System.Text.RegularExpressions;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Input;
using System.Windows.Markup;
using static ArcGIS.Desktop.Editing.Templates.EditingGroupTemplate;


namespace twobillionarcgisaddin
{
    /// <summary>
    /// Interaction logic for TwoBillionTreesToolLogisticsView.xaml
    /// </summary>
    public partial class TwoBillionTreesToolLogisticsView : UserControl
    {
        #region Global Variables
        // ******************************************************
        // Global Variables
        // ******************************************************

        // Store the output of the SiteMapper tool
        public string siteMapperToolOutput { get; private set; }

        // Access to the data container object of the SiteMapper tool
        public DataContainer dataContainer { get; private set; }

        // Global variable flag to bypass double triggering events
        private bool _noise = false;

        #endregion
        // ******************************************************
        // Constructor
        // ******************************************************
        #region Constructor

        private static TwoBillionTreesToolLogisticsView _this = null;
        static public TwoBillionTreesToolLogisticsView MyTwoBillionTreesToolLogisticsView => _this;
        public TwoBillionTreesToolLogisticsView()
        {
            InitializeComponent();

            _this = this;

            // TODO: Remove default values
            this.ArcPythonToolboxPath.Text = "";
            this.ArcConnectionFilePath.Text = "";
            this.DatabaseSchema.Text = "";
        }

        #endregion
        // ******************************************************
        // Event Functions (Button Clicks, Toggles, ...)
        // ******************************************************
        #region Event Functions

        // Method to handle the click event of the Establish Connection button
        private async void EstablishButtonClicked(object sender, RoutedEventArgs e)
        {
            try
            {
                // Disable the button (spam prevention)
                this.EstablishConnectionButton.IsEnabled = false;

                ShowHiddenCat();

                bool success = await ExecuteEstablishConnectionAsync();
                if (!success)
                {
                    this.EstablishConnectionButton.IsEnabled = true;
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
                this.BatchSiteMapperSection.Visibility = Visibility.Collapsed;
            }
        }

        private void FeatureSelectionChanged(MapSelectionChangedEventArgs args)
        {
            MapView mapView = MapView.Active;
            if (mapView != null)
            {
                FeatureLayer featureLayer = mapView.GetSelectedLayers().OfType<FeatureLayer>().FirstOrDefault();
                if (featureLayer != null) 
                { 
                    SelectedFeaturesNumber.Content = featureLayer.SelectionCount.ToString();
                }       
                
            }
        }

        // Method to handle the click event of the SiteMapper button
        private async void SiteMapperButtonClicked(object sender, RoutedEventArgs e)
        {
            MapSelectionChangedEvent.Subscribe(FeatureSelectionChanged);

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

                if (sender == this.BatchSiteMapperButton)
                {
                    this.BatchSiteMapperSection.Visibility = Visibility.Visible;
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

                // Hide the status message
                this.SiteMapper_SuccessStatus.Visibility = Visibility.Collapsed;
                this.SiteMapper_ErrorStatus.Visibility = Visibility.Collapsed;

                // Access the current map in ArcGIS Pro
                MapView mapView = MapView.Active;
                if (mapView != null)
                {
                    SelectionSet selectedFeatures = null;
                    FeatureLayer featureLayer = null;
                    GeometryType geometryType = GeometryType.Unknown;
                    await QueuedTask.Run(() =>
                    {
                        // Get the currently selected features in the map
                        selectedFeatures = mapView.Map.GetSelection();

                        // Check if any features are selected in any layer
                        if (selectedFeatures.Count == 0)
                        {
                            ArcGIS.Desktop.Framework.Dialogs.MessageBox.Show("No features on the map are selected, please select a feature you want to process and try again!");
                            this.SendDataButton.IsEnabled = true;
                            this.SiteMapper_ErrorStatus.Visibility = Visibility.Visible;
                            return;
                        }

                        // Get the first layer and its corresponding selected feature OIDs
                        var selectionSet = selectedFeatures.ToDictionary().First();
                        featureLayer = selectionSet.Key as FeatureLayer;

                        // Check if the feature layer is not null
                        if (featureLayer != null)
                        {
                            // Access the feature class of the feature layer
                            FeatureClass featureClass = featureLayer.GetFeatureClass();

                            // Get the geometry type of the feature class
                            geometryType = featureClass.GetDefinition().GetShapeType();
                        }
                    });

                    // Check if the selected layer is a polygon or not
                    if (geometryType != GeometryType.Polygon)
                    {
                        ArcGIS.Desktop.Framework.Dialogs.MessageBox.Show("You currently have a " + geometryType.ToString() + " geometry selected. The tool does not currently accept anything other than Polygons.");

                        // Disable the button (spam prevention)
                        this.SendDataButton.IsEnabled = true;
                    }
                    else
                    {
                        // Get the selected Site ID from the logistics dropdown
                        string selectedSiteID = this.SiteID_Dropdown.SelectedItem.ToString();

                        if ((bool)this.OverwriteToggle.IsChecked)
                        {
                            await ExecuteUpdateDataToolAsync(selectedSiteID, featureLayer);
                        }
                        else
                        {
                            await ExecuteInsertDataToolAsync(selectedSiteID, featureLayer);
                        }
                    }                
                }
            }
            catch (Exception ex)
            {
                // Handle any exceptions that occur during tool execution
                ArcGIS.Desktop.Framework.Dialogs.MessageBox.Show($"Error: {ex.Message}", "Error");
            }

            this.SendDataButton.IsEnabled = true;
        }

        // Method to handle the click event of the Finish Project button
        private async void CompleteProjectButtonClicked(object sender, RoutedEventArgs e)
        {
            try
            {
                // Access the current map in ArcGIS Pro
                MapView mapView = MapView.Active;
                if (mapView != null)
                {
                    string selectedLayer = null;
                    await QueuedTask.Run(() =>
                    {
                        // Get the currently selected features in the map
                        var selectedFeatures = mapView.GetSelectedLayers();
                        if (selectedFeatures.Count == 0)
                        {
                            ArcGIS.Desktop.Framework.Dialogs.MessageBox.Show("Please select a project on the left and try again.");
                            return;
                        }
                        else if (selectedFeatures.Count > 1) 
                        {
                            ArcGIS.Desktop.Framework.Dialogs.MessageBox.Show("Please select only one project on the left and try again.");
                            return;
                        }

                        selectedLayer = selectedFeatures[0].Name;
                    });

                    if (selectedLayer != null)
                    {
                        await ExecuteCompleteProjectToolAsync(selectedLayer);
                    }
                }
            }
            catch (Exception ex)
            {
                // Handle any exceptions that occur during tool execution
                ArcGIS.Desktop.Framework.Dialogs.MessageBox.Show($"Error: {ex.Message}", "Error");
            }
        }

        // Method to handle the change event of the filters
        private void SiteMapperProjectNumberFilterChanged(object sender, SelectionChangedEventArgs e)
        {
            this.SiteID_Dropdown.SelectedIndex = 0;
            Dictionary<string, string> filter = GetSiteMapperFilter();

            // Create a DataContainer instance to process the JSON string
            dataContainer = new DataContainer(siteMapperToolOutput);

            // 
            PopulateFilters(dataContainer, true);

            if (string.IsNullOrEmpty(this.ProjectNumber_Dropdown.SelectedItem as string))
            {
                this.Secondary_Filter.Visibility = Visibility.Collapsed;
            }
            else
            {
                this.Secondary_Filter.Visibility = Visibility.Visible;
            }
                       
            // Filter map layers based on the selected project number
            SelectMapLayers(filter["ProjectNumber"]);
                
            // Repopulate the data grid with the filtered data
            SiteMapperDataGridView dockpane2 = SiteMapperDataGridView.MySiteMapperDataGridView;
            dockpane2.PopulateDataGrid(dataContainer, filter);   
        }

        // Method to handle the change event of the filters
        private void SiteMapperSiteIDFilterChanged(object sender, SelectionChangedEventArgs e)
        {
            if (_noise)
            {
                _noise = false;
            }

            Dictionary<string, string> filter = GetSiteMapperFilter();

            if (this.SiteID_Dropdown.SelectedItem == null || this.SiteID_Dropdown.SelectedItem.ToString() == "")
            {
                this.SendDataButton.IsEnabled = false;
                this.MatchButton.IsEnabled = false;
            }
            else
            {
                this.SendDataButton.IsEnabled = true;
                this.MatchButton.IsEnabled = true;
            }

            // Repopulate the data grid with the filtered data
            SiteMapperDataGridView dockpane2 = SiteMapperDataGridView.MySiteMapperDataGridView;
            dockpane2.PopulateDataGrid(dataContainer, filter);
        }

        private async void ShowHiddenCat()
        {
            this.HiddenCat.Visibility = Visibility.Visible;
            await Task.Delay(500); // 500 milliseconds = .5 seconds
            this.HiddenCat.Visibility = Visibility.Hidden;
        }

        // Method to handle the click event of the Match Button
        private async void MatchButtonClicked(object sender, RoutedEventArgs e)
        {
            // Disable the Match button to prevent multiple clicks while processing
            this.MatchButton.IsEnabled = false;

            try
            {
                // Access the current map in ArcGIS Pro
                MapView mapView = MapView.Active;
                if (mapView == null)
                {
                    ArcGIS.Desktop.Framework.Dialogs.MessageBox.Show("No active map view found.");
                    this.MatchButton.IsEnabled = true;
                    return;
                }

                // Get the first selected feature layer from the active map view
                FeatureLayer featureLayer = mapView.GetSelectedLayers().OfType<FeatureLayer>().FirstOrDefault();
                if (featureLayer == null)
                {
                    ArcGIS.Desktop.Framework.Dialogs.MessageBox.Show("Please select a feature layer in the Drawing Order and try again.");
                    this.MatchButton.IsEnabled = true;
                    return;
                }

                // Retrieve the site name from the selected site ID in the dropdown
                DataEntry entry = dataContainer.GetDataEntryBySiteID(this.SiteID_Dropdown.SelectedItem.ToString());
                string siteName = entry.SiteName;
                string siteNameFormatted = $"%{siteName.Replace(" ", "%")}%";
                string matchField = this.MatchField_Dropdown.SelectedItem.ToString();

                bool isStringField = true;
                await QueuedTask.Run(() =>
                {
                    // Check the data type of the match field
                    Field matchFieldType = featureLayer.GetTable().GetDefinition().GetFields().FirstOrDefault(f => f.Name == matchField);
                    isStringField = matchFieldType.FieldType == FieldType.String;
                });


                // Asynchronously retrieve all unique values from the specified field in the feature layer
                List<string> columnValues = await QueuedTask.Run(() =>
                {
                    List<string> values = new List<string>();
                    using (Table table = featureLayer.GetTable())
                    using (RowCursor cursor = table.Search(null, false))
                    {
                        while (cursor.MoveNext())
                        {
                            using (Row row = cursor.Current)
                            {
                                // Retrieve the value from the specified match field
                                object value = row[matchField];
                                if (value != DBNull.Value && value != null && !values.Contains(value))
                                {
                                    values.Add(value.ToString());
                                }
                            }
                        }
                    }
                    return values;
                });

                // Split the site name into significant parts for matching
                string[] parts = siteName.Split(new[] { ' ', ':', '#', '-', '_' }, StringSplitOptions.RemoveEmptyEntries);

                // Escape special characters in each part for regex matching
                string[] escapedParts = parts.Select(Regex.Escape).ToArray();

                // Custom function to check if most parts of the site name are present in the input
                bool ContainsMostParts(string input, string[] parts)
                {
                    int matchCount = parts.Count(part => Regex.IsMatch(input, $@"\b{part}\b", RegexOptions.IgnoreCase));
                    return matchCount >= (parts.Length * 0.75); // Adjust threshold as needed
                }

                // Find all strings in columnValues that match most parts of the site name
                List<string> matchingStrings = columnValues.FindAll(str => ContainsMostParts(str, escapedParts));

                // Build the SQL query to select features matching the identified strings
                string query = "";
                if (isStringField)
                {
                    query = string.Join(" OR ", matchingStrings.Select(match => $"{matchField} LIKE '%{match}%'"));
                }
                else
                {
                    // Handle non-string fields differently, here we assume exact matches for simplicity
                    query = string.Join(" OR ", matchingStrings.Select(match => $"{matchField} = {match}"));
                }

                // Initialize the message for the number of matching features found
                string matchesFound = "0 features were found";

                // Asynchronously execute the query and count the matching features
                await QueuedTask.Run(() =>
                {
                    // Clear previous selections on the map
                    mapView.Map.ClearSelection();

                    // If no matches were found, return early
                    if (query == "")
                    {
                        return;
                    }

                    // Create a query filter with the built query
                    QueryFilter queryFilter = new QueryFilter()
                    {
                        WhereClause = query
                    };

                    // Select features matching the query filter
                    featureLayer.Select(queryFilter);

                    // Count the number of matching features
                    using (RowCursor rowCursor = featureLayer.Search(queryFilter))
                    {
                        int i = 0;
                        while (rowCursor.MoveNext()) i++;
                        matchesFound = $"{i} features were found";
                    }
                });

                // Update the label with the number of matched features
                this.MatchedFeaturesLabel.Content = matchesFound;

                // Re-enable the Match button after processing
                this.MatchButton.IsEnabled = true;
                
            }
            catch (Exception ex)
            {
                // Show an error message if an exception occurs
                ArcGIS.Desktop.Framework.Dialogs.MessageBox.Show($"Error: {ex.Message}", "Error");

                // Re-enable the Match button in case of an error
                this.MatchButton.IsEnabled = true;
            }
        }

        // Method to handle the click event of the SiteMapper button
        private async void RefreshButtonClicked(object sender, RoutedEventArgs e)
        {
            this.BatchSiteMapperRefreshButton.Content = "Working...";
            this.BatchSiteMapperRefreshButton.IsEnabled = false;

            MapView mapView = MapView.Active;
            // Getting the first selected feature layer
            FeatureLayer featureLayer = mapView.GetSelectedLayers().OfType<FeatureLayer>().FirstOrDefault();
            if (featureLayer == null)
            {
                ArcGIS.Desktop.Framework.Dialogs.MessageBox.Show("Please select a feature layer in the Drawing Order and try again.");
                this.MatchButton.IsEnabled = false;
                this.BatchSiteMapperRefreshButton.Content = "Refresh";
                this.BatchSiteMapperRefreshButton.IsEnabled = true;
                return;
            }

            List<FieldDescription> fieldDescriptions = null;
            await QueuedTask.Run(() =>
            {
                // Retrieving field descriptions
                fieldDescriptions = featureLayer.GetFieldDescriptions();
                if (fieldDescriptions.Count == 0)
                {
                    ArcGIS.Desktop.Framework.Dialogs.MessageBox.Show("The selected layer has no fields.");
                }
                return;
            });
            this.MatchField_Dropdown.Items.Clear();
            foreach (var item in fieldDescriptions)
            {
                this.MatchField_Dropdown.Items.Add(item.Name);
            }

            this.BatchSiteMapperRefreshButton.Content = "Refresh";
            this.BatchSiteMapperRefreshButton.IsEnabled = true;
        }

        #endregion
        // ******************************************************
        // Various Helper Functions
        // ******************************************************
        #region Various Helper Functions

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
                filterProjNumberList.Sort(StringComparer.OrdinalIgnoreCase);
                this.ProjectNumber_Dropdown.ItemsSource = filterProjNumberList;
            }

            filterSiteIDList.Sort(StringComparer.OrdinalIgnoreCase);
            _noise = true;
            this.SiteID_Dropdown.ItemsSource = filterSiteIDList;
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

        #endregion
        // ******************************************************
        // Asyncronous Database Functions
        // ******************************************************
        #region Asyncronous Database Functions

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
        private async Task<bool> ExecuteInsertDataToolAsync(string siteID, FeatureLayer featureLayer)
        {
            try
            {
                // Set the parameters
                string toolboxPath = this.ArcPythonToolboxPath.Text + "\\InsertDataTool";
                string connectionFile = this.ArcConnectionFilePath.Text;
                string tableName = this.DatabaseSchema.Text + ".site_geometry";

                // Execute the Python tool and get the result
                var parameters = Geoprocessing.MakeValueArray(connectionFile, tableName, siteID, featureLayer);
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

        // Method to execute the Insert Data tool asynchronously
        private async Task<bool> ExecuteUpdateDataToolAsync(string siteID, FeatureLayer featureLayer)
        {
            try
            {
                // Set the parameters
                string toolboxPath = this.ArcPythonToolboxPath.Text + "\\UpdateDataTool";
                string connectionFile = this.ArcConnectionFilePath.Text;
                string tableName = this.DatabaseSchema.Text + ".site_geometry";

                // Execute the Python tool and get the result
                var parameters = Geoprocessing.MakeValueArray(connectionFile, tableName, siteID, featureLayer);
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

        // Method to execute the Insert Data tool asynchronously
        private async Task<bool> ExecuteCompleteProjectToolAsync(string projectSpatialID)
        {
            try
            {
                // Set the parameters
                string toolboxPath = this.ArcPythonToolboxPath.Text + "\\CompleteProjectTool";
                string connectionFile = this.ArcConnectionFilePath.Text;
                string tableName = this.DatabaseSchema.Text + ".raw_data_tracker";

                // Execute the Python tool and get the result
                var parameters = Geoprocessing.MakeValueArray(connectionFile, tableName, projectSpatialID);
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

        #endregion
    }
}
