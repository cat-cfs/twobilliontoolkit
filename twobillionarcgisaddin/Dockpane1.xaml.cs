using ArcGIS.Core.Data;
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
        private string g_SiteMaperToolOutput;
        public string GetSiteMaperToolOutput()
        {
            return g_SiteMaperToolOutput;
        }

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

        private DataContainer dataContainer;

        private async void ToggleEstablishButton(object sender, RoutedEventArgs e)
        {
            // Call the async method
            bool success = await ExecuteEstablishConnectionAsync();

            if (!success)
            {
                return;
            }

            if (this.UserForm.Visibility == Visibility.Visible)
            {
                this.UserForm.Visibility = Visibility.Collapsed;
                this.ButtonToolist.Visibility = Visibility.Visible;
            }
        }

        private async void ToggleSiteMapperButton(object sender, RoutedEventArgs e)
        {
            try
            {
                this.SiteMapperButton.IsEnabled = false;

                TwoBillionTreesDockpaneViewModel2.Show();

                if (String.IsNullOrEmpty(g_SiteMaperToolOutput))
                {
                    // Call the async method
                    bool success = await ExecuteRetrieveDataToolAsync();

                    if (!success)
                    {
                        return;
                    }

                }

                if (this.ButtonToolist.Visibility == Visibility.Visible)
                {
                    this.ButtonToolist.Visibility = Visibility.Collapsed;
                    this.SiteMapper.Visibility = Visibility.Visible;
                }

                this.SiteMapperButton.IsEnabled = true;
            }
            catch (Exception ex)
            {
                // Handle any exceptions that occur during tool execution
                ArcGIS.Desktop.Framework.Dialogs.MessageBox.Show($"Error: {ex.Message}", "Error");
                this.SiteMapperButton.IsEnabled = true;
            }
        }

        private void ToggleBackButton(object sender, RoutedEventArgs e)
        {
            if (this.BackButton.Visibility == Visibility.Visible)
            {
                this.ButtonToolist.Visibility = Visibility.Visible;
                this.SiteMapper.Visibility = Visibility.Collapsed;
            }
        }

        private async void ToggleSendButton(object sender, RoutedEventArgs e)
        {
            this.SendData.IsEnabled = false;
            this.SiteMapper_SuccessStatus.Visibility = Visibility.Collapsed;
            this.SiteMapper_ErrorStatus.Visibility = Visibility.Collapsed;

            // Access the current map in ArcGIS Pro
            MapView mapView = MapView.Active;

            if (mapView != null)
            {
                string selectedGeometry = null;
                await QueuedTask.Run(() =>
                {
                    // get the currently selected features in the map
                    var selectedFeatures = mapView.Map.GetSelection();

                    // get the first layer and its corresponding selected feature OIDs
                    var selectionSet = selectedFeatures.ToDictionary();

                    if (selectionSet.Count == 0)
                    {
                        ArcGIS.Desktop.Framework.Dialogs.MessageBox.Show("No features on the map are selected, please select a feature you want to process and try again!");
                        /*return;*/
                    }

                    // create an instance of the inspector class
                    var inspector = new ArcGIS.Desktop.Editing.Attributes.Inspector();

                    // load the selected features into the inspector using a list of object IDs
                    inspector.Load(selectionSet.Keys.First(), selectionSet.Values.First());

                    // Assuming the inspector.Shape represents the geometry of the selected feature
                    selectedGeometry = inspector.Shape.ToJson();
                });
                   
                await ExecuteInsertDataToolAsync($"{SiteID_Dropdown.SelectedItem}, {selectedGeometry}");
            }
        }


        private void BrowseButtonToolboxClick(object sender, RoutedEventArgs e)
        {
            Microsoft.Win32.OpenFileDialog openFileDialog = new Microsoft.Win32.OpenFileDialog();

            // Set filter for file extension and default file extension
            openFileDialog.Filter = "All files (*.*)|*.*";

            // Display OpenFileDialog by calling ShowDialog method
            bool? result = openFileDialog.ShowDialog();

            // Get the selected file name and display in the TextBox
            if (result == true)
            {
                this.ArcPythonToolboxPath.Text = openFileDialog.FileName;
            }
        }

        private void BrowseButtonConnFileClick(object sender, RoutedEventArgs e)
        {
            Microsoft.Win32.OpenFileDialog openFileDialog = new Microsoft.Win32.OpenFileDialog();

            // Set filter for file extension and default file extension
            openFileDialog.Filter = "All files (*.*)|*.*";

            // Display OpenFileDialog by calling ShowDialog method
            bool? result = openFileDialog.ShowDialog();

            // Get the selected file name and display in the TextBox
            if (result == true)
            {
                this.ArcConnectionFilePath.Text = openFileDialog.FileName;
            }
        }

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

        private void PopulateFilters(DataContainer container, bool updateSecondaryFilter = false)
        {
            string selectedItem = (string)ProjectNumber_Dropdown.SelectedItem;

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

        private void FilterChanged(object sender, SelectionChangedEventArgs e)
        {
            if (sender == this.ProjectNumber_Dropdown)
            {
                // Create a DataContainer instance to process the JSON string
                dataContainer = new DataContainer(g_SiteMaperToolOutput);

                //
                PopulateFilters(dataContainer, true);

                if (ProjectNumber_Dropdown.SelectedItem == "")
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

        private async Task<bool> ExecuteEstablishConnectionAsync()
        {
            this.EstablishConnection.IsEnabled = false;
            try
            {
                // Set the path to the Python toolbox
                string toolboxPath = this.ArcPythonToolboxPath.Text + "\\EstablishConnectionTool";

                // Set the path to the connection file
                string connectionFile = this.ArcConnectionFilePath.Text;

                // Set the table name
                string tableName = this.DatabaseSchema.Text + ".site_mapping";

                // Execute the Python tool and get the result
                var parameters = Geoprocessing.MakeValueArray(connectionFile, tableName);
                var returnValue = await Geoprocessing.ExecuteToolAsync(toolboxPath, parameters);

                if (returnValue.IsFailed)
                {
                    this.EstablishConnection.IsEnabled = true;
                    return false;
                }

                return true;
            }
            catch (Exception ex)
            {
                // Handle any exceptions that occur during tool execution
                ArcGIS.Desktop.Framework.Dialogs.MessageBox.Show($"Error: {ex.Message}", "Error");
                this.EstablishConnection.IsEnabled = true;
                return false;
            }
        }

        private async Task<bool> ExecuteRetrieveDataToolAsync()
        {
            try
            {
                // Set the path to the Python toolbox
                string toolboxPath = this.ArcPythonToolboxPath.Text + "\\ReadDataTool";

                // Set the path to the connection file
                string connectionFile = this.ArcConnectionFilePath.Text;

                // Set the table name
                string tableName = this.DatabaseSchema.Text + ".site_mapping";

                // Execute the Python tool and get the result
                var parameters = Geoprocessing.MakeValueArray(connectionFile, tableName);
                var toolOuput = await Geoprocessing.ExecuteToolAsync(toolboxPath, parameters);
                g_SiteMaperToolOutput = toolOuput.ReturnValue;

                // Check if the tool ran correctly by checking the output
                if (String.IsNullOrEmpty(g_SiteMaperToolOutput))
                {
                    return false;
                }

                // Create a DataContainer instance to process the JSON string
                dataContainer = new DataContainer(g_SiteMaperToolOutput);

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

        private async Task<bool> ExecuteInsertDataToolAsync(string insertData)
        {
            try
            {
                // Set the path to the Python toolbox
                string toolboxPath = this.ArcPythonToolboxPath.Text + "\\UpdateDataTool";

                // Set the path to the connection file
                string connectionFile = this.ArcConnectionFilePath.Text;

                // Set the table name
                string tableName = this.DatabaseSchema.Text + ".site_geometry";

                // Execute the Python tool and get the result
                var parameters = Geoprocessing.MakeValueArray(connectionFile, tableName, insertData);
                var returnValue = await Geoprocessing.ExecuteToolAsync(toolboxPath, parameters);

                if (returnValue.IsFailed)
                {
                    this.SendData.IsEnabled = true;
                    this.SiteMapper_SuccessStatus.Visibility = Visibility.Collapsed;
                    this.SiteMapper_ErrorStatus.Visibility = Visibility.Visible;
                    return false;
                }

                this.SendData.IsEnabled = true;
                this.SiteMapper_ErrorStatus.Visibility = Visibility.Collapsed;
                this.SiteMapper_SuccessStatus.Visibility = Visibility.Visible;

                return true;
            }
            catch (Exception ex)
            {
                // Handle any exceptions that occur during tool execution
                ArcGIS.Desktop.Framework.Dialogs.MessageBox.Show($"Error: {ex.Message}", "Error");
                this.SendData.IsEnabled = true;
                this.SiteMapper_SuccessStatus.Visibility = Visibility.Collapsed;
                this.SiteMapper_ErrorStatus.Visibility = Visibility.Visible;
                return false;
            }
        }

        public DataContainer GetDataContainer()
        {
            return dataContainer;
        }
    }
}
