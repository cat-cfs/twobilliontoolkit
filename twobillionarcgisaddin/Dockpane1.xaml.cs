using ArcGIS.Core.CIM;
using ArcGIS.Core.Data;
using ArcGIS.Core.Data.UtilityNetwork.Trace;
using ArcGIS.Core.Geometry;
using ArcGIS.Desktop.Core;
using ArcGIS.Desktop.Core.Geoprocessing;
using ArcGIS.Desktop.Framework.Dialogs;
using ArcGIS.Desktop.Framework.Threading.Tasks;
using ArcGIS.Desktop.Internal.Mapping;
using ArcGIS.Desktop.Internal.Mapping.CommonControls;
using ArcGIS.Desktop.Mapping;
using ArcGIS.Desktop.Mapping.Events;
using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.ComponentModel;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Security.Policy;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Input;
using System.Windows.Markup;
using System.Windows.Threading;
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

        //
        private bool SiteMapper_IsBatch = false;

        //
        private List<DataEntry> dataEntries = null;

        //
        private DataLayerOptionsPopup _dataLayerOptionsPopup = null;

        //
        public class DataLayer : INotifyPropertyChanged
        {
            private string _table;
            private string _name;
            private esriGeometryType _geomType;
            private string _objectIDColumn;
            private string? _year;
            private string? _projectNum;
            private bool _disabled;

            public string Table
            {
                get { return _table; }
                set
                {
                    if (_table != value)
                    {
                        _table = value;
                        OnPropertyChanged(nameof(Table));
                    }
                }
            }

            public string Name
            {
                get { return _name; }
                set
                {
                    if (_name != value)
                    {
                        _name = value;
                        OnPropertyChanged(nameof(Name));
                    }
                }
            }

            public esriGeometryType GeomType
            {
                get { return _geomType; }
                set
                {
                    if (_geomType != value)
                    {
                        _geomType = value;
                        OnPropertyChanged(nameof(GeomType));
                    }
                }
            }

            public string ObjectIDColumn
            {
                get { return _objectIDColumn; }
                set
                {
                    if (_objectIDColumn != value)
                    {
                        _objectIDColumn = value;
                        OnPropertyChanged(nameof(ObjectIDColumn));
                    }
                }
            }

            public string? Year
            {
                get { return _year; }
                set
                {
                    if (_year != value)
                    {
                        _year = value;
                        OnPropertyChanged(nameof(Year));
                    }
                }
            }

            public string? ProjectNum
            {
                get { return _projectNum; }
                set
                {
                    if (_projectNum != value)
                    {
                        _projectNum = value;
                        OnPropertyChanged(nameof(ProjectNum));
                    }
                }
            }

            public bool Disabled
            {
                get { return _disabled; }
                set
                {
                    if (_disabled != value)
                    {
                        _disabled = value;
                        OnPropertyChanged(nameof(Disabled));
                    }
                }
            }

            public event PropertyChangedEventHandler PropertyChanged;

            protected void OnPropertyChanged(string propertyName)
            {
                PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
            }
        }

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

            this.ArcPythonToolboxPath.Text = "";
            this.ArcConnectionFilePath.Text = "";
            this.DatabaseSchema.Text = "";

            AddStaticDataLayers();
        }

        private ObservableCollection<DataLayer> dataLayersToAdd = new ObservableCollection<DataLayer>();

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
            if (sender == this.ArcPythonToolboxButton)
            {
                openFileDialog.Filter = "Python Toolbox Files|*.pyt";
            }
            else if (sender == this.ArcConnectionFileButton)
            {
                openFileDialog.Filter = "Database Connection Files|*.sde";
            }

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
                this.Import2BTData.Visibility = Visibility.Collapsed;
                this.BatchSiteMapperSection.Visibility = Visibility.Collapsed;
                SiteMapper_IsBatch = false;
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

        // Method to handle the click event of the Import2BTData button
        private void Import2BTDataButtonClicked(object sender, RoutedEventArgs e)
        {
            // Toggle visibility of UI elements
            if (this.ButtonToolist.Visibility == Visibility.Visible)
            {
                this.ButtonToolist.Visibility = Visibility.Collapsed;
                this.Import2BTData.Visibility = Visibility.Visible;
            }

            try
            {
                // Disable the button (spam prevention)
                this.Import2BTDataButton.IsEnabled = false;

                this.DataLayers.ItemsSource = dataLayersToAdd;
            }
            catch (Exception ex)
            {
                // Handle any exceptions that occur during tool execution
                ArcGIS.Desktop.Framework.Dialogs.MessageBox.Show($"Error: {ex.Message}", "Error");
            }

            this.Import2BTDataButton.IsEnabled = true;
        }

        // Method to handle the click event of the Import Data Options button
        private void ImportDataOptionsButtonClicked(object sender, RoutedEventArgs e)
        {
            try
            {
                // Disable the button (spam prevention)
                this.ImportDataOptionsButton.IsEnabled = false;

                // Get the selected item from the ListBox
                DataLayer selectedDataLayer = (DataLayer)DataLayers.SelectedItem;
                if (selectedDataLayer == null)
                {
                    // Show an error message if no item is selected
                    ArcGIS.Desktop.Framework.Dialogs.MessageBox.Show("Please select a data layer to edit.", "Error");
                    return;
                }

                // Pass the selected item to the DataLayerOptionsPopup
                if (_dataLayerOptionsPopup == null || !_dataLayerOptionsPopup.IsVisible)
                {
                    _dataLayerOptionsPopup = new DataLayerOptionsPopup(selectedDataLayer);
                    _dataLayerOptionsPopup.Title = $"{selectedDataLayer.Table} Options";
                    _dataLayerOptionsPopup.Show();
                }

            }
            catch (Exception ex)
            {
                // Handle any exceptions that occur during tool execution
                ArcGIS.Desktop.Framework.Dialogs.MessageBox.Show($"Error: {ex.Message}", "Error");
            }

            this.ImportDataOptionsButton.IsEnabled = true;
        }

        // Method to handle the click event of the Import Data Toggle button
        private void ImportDataToggleButtonClicked(object sender, RoutedEventArgs e)
        {
            try
            {
                // Disable the button (spam prevention)
                this.ImportDataToggleButton.IsEnabled = false;


                // Cast the selected item to the DataLayer type
                DataLayer selectedDataLayer = this.DataLayers.SelectedItem as DataLayer;

                // Check if the casting was successful
                if (selectedDataLayer != null)
                {
                    selectedDataLayer.Disabled = !selectedDataLayer.Disabled; // Toggle the disabled state
                }

            }
            catch (Exception ex)
            {
                // Handle any exceptions that occur during tool execution
                ArcGIS.Desktop.Framework.Dialogs.MessageBox.Show($"Error: {ex.Message}", "Error");
            }

            this.ImportDataToggleButton.IsEnabled = true;
        }

        // Method to handle the click event of the Send Data button
        private async void ImportDataButtonClicked(object sender, RoutedEventArgs e)
        {
            try
            {
                // Disable the button (spam prevention)
                this.ImportDataButton.IsEnabled = false;

                // Store the active map and connection file path in variables
                Map map = MapView.Active.Map;
                Uri uri = new Uri(this.ArcConnectionFilePath.Text);

                // loop through each entry in the dictionary
                foreach (DataLayer entry in dataLayersToAdd)
                {
                    if (entry.Disabled)
                    {
                        continue;
                    }

                    // Build the database query based on parameters
                    string databaseSchema = $"bt_testcase1.{this.DatabaseSchema.Text}";
                    string dataset = $"{databaseSchema}.{entry.Table}";
                    var sqlQueryBuilder = new StringBuilder($@"SELECT si.*, sii.site_name, sii.project_number, sii.year FROM {dataset} si INNER JOIN {databaseSchema}.site_id sii ON si.site_id = sii.site_id"
                    );

                    List<string> conditions = new List<string>();

                    if (!string.IsNullOrEmpty(entry.Year))
                    {
                        conditions.Add($"year = '{int.Parse(entry.Year)}'");
                    }
                    if (!string.IsNullOrEmpty(entry.ProjectNum))
                    {
                        conditions.Add($"project_number = '{entry.ProjectNum}'");
                    }

                    if (conditions.Count > 0)
                    {
                        sqlQueryBuilder.Append(" WHERE " + string.Join(" AND ", conditions));
                    } 

                    string sqlQuery = sqlQueryBuilder.ToString();

                    await QueuedTask.Run(() =>
                    {
                        Geodatabase geodatabase = new Geodatabase(new DatabaseConnectionFile(uri));
                        CIMSqlQueryDataConnection sqlDataConnection = new CIMSqlQueryDataConnection()
                        {
                            WorkspaceConnectionString = geodatabase.GetConnectionString(),
                            GeometryType = entry.GeomType,
                            OIDFields = entry.ObjectIDColumn,
                            Srid = "102001",
                            SqlQuery = sqlQuery,
                            Dataset = dataset
                        };

                        var layerParameters = new LayerCreationParams(sqlDataConnection)
                        {
                            Name = entry.Name
                        };

                        FeatureLayer featureLayer = LayerFactory.Instance.CreateLayer<FeatureLayer>(layerParameters, map);
                    });
                }
            }
            catch (Exception ex)
            {
                // Handle any exceptions that occur during tool execution
                ArcGIS.Desktop.Framework.Dialogs.MessageBox.Show($"Error: {ex.Message}", "Error");
            }

            this.ImportDataButton.IsEnabled = true;
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
                    SiteMapper_IsBatch = true;
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
                if (mapView == null)
                {
                    ArcGIS.Desktop.Framework.Dialogs.MessageBox.Show("No active map view found.");
                    this.SendDataButton.IsEnabled = true;
                    return;
                }

                bool foundGeometryOrCanceled = await SiteMapperCheckGeometryExistInDB(mapView);
                if (foundGeometryOrCanceled)
                {
                    ArcGIS.Desktop.Framework.Dialogs.MessageBox.Show("Canceled");
                    this.SendDataButton.IsEnabled = true;
                    return;
                }

                /*if (SiteMapper_IsBatch)
                {
                    SiteMapperSendDataBatch(mapView);
                }
                else
                {
                    SiteMapperSendData(mapView);
                }*/


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
                if (mapView == null)
                {
                    ArcGIS.Desktop.Framework.Dialogs.MessageBox.Show("No active map view found.");
                    return;
                }

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
            catch (Exception ex)
            {
                // Handle any exceptions that occur during tool execution
                ArcGIS.Desktop.Framework.Dialogs.MessageBox.Show($"Error: {ex.Message}", "Error");
            }
        }

        // Method to handle the change event of the filters
        private void SiteMapperClearButtonClicked(object sender, RoutedEventArgs e)
        {
            try
            {
                if (sender == this.SiteMapperProjectNumberClearButton)
                {
                    this.ProjectNumber_Dropdown.SelectedItem = "";
                }
                else if (sender == this.SiteMapperSiteIDClearButton)
                {
                    this.SiteID_Dropdown.SelectedItem = "";
                }
            }
            catch (Exception ex)
            {
                // Show an error message if an exception occurs
                ArcGIS.Desktop.Framework.Dialogs.MessageBox.Show($"Error: {ex.Message}", "Error");
            }
        }

        // Method to handle the change event of the filters
        private void SiteMapperProjectNumberFilterChanged(object sender, SelectionChangedEventArgs e)
        {
            try
            { 
                this.SiteID_Dropdown.SelectedIndex = 0;
                Dictionary<string, string> filter = GetSiteMapperFilter();

                // Create a DataContainer instance to process the JSON string
                dataContainer = new DataContainer(siteMapperToolOutput);

                // 
                PopulateFilters(dataContainer, true);

                if (this.ProjectNumber_Dropdown.SelectedItem == null || this.ProjectNumber_Dropdown.SelectedItem.ToString() == "")
                {
                    this.Secondary_Filter.Visibility = Visibility.Collapsed;
                    this.SendDataButton.IsEnabled = false;
                }
                else
                {
                    this.Secondary_Filter.Visibility = Visibility.Visible;
                }

            if (SiteMapper_IsBatch)
            {
                this.Secondary_Filter.Visibility = Visibility.Collapsed; 
            }

                // Refresh the list of data entries for other functionalities
                dataEntries = dataContainer.GetDataEntriesByProjectNumber(this.ProjectNumber_Dropdown.SelectedItem.ToString());

                // Filter map layers based on the selected project number
                SelectMapLayers(filter["ProjectNumber"]);

                // Repopulate the data grid with the filtered data
                SiteMapperDataGridView dockpane2 = SiteMapperDataGridView.MySiteMapperDataGridView;
                dockpane2.PopulateDataGrid(dataContainer, filter);
            }
            catch (Exception ex)
            {
                // Show an error message if an exception occurs
                ArcGIS.Desktop.Framework.Dialogs.MessageBox.Show($"Error: {ex.Message}", "Error");
            }
        }

        // Method to handle the change event of the filters
        private void SiteMapperSiteIDFilterChanged(object sender, SelectionChangedEventArgs e)
        {
            try
            {
                if (_noise)
                {
                    _noise = false;
                }

                Dictionary<string, string> filter = GetSiteMapperFilter();

                if (this.SiteID_Dropdown.SelectedItem == null || this.SiteID_Dropdown.SelectedItem.ToString() == "")
                {
                    this.SendDataButton.IsEnabled = false;
                }
                else
                {
                    this.SendDataButton.IsEnabled = true;
                }

                // Repopulate the data grid with the filtered data
                SiteMapperDataGridView dockpane2 = SiteMapperDataGridView.MySiteMapperDataGridView;
                dockpane2.PopulateDataGrid(dataContainer, filter);
            }
            catch (Exception ex)
            {
                // Show an error message if an exception occurs
                ArcGIS.Desktop.Framework.Dialogs.MessageBox.Show($"Error: {ex.Message}", "Error");
            }
        }

        // Method to handle the change event of the filters
        private void SiteMapperMatchFilterChanged(object sender, SelectionChangedEventArgs e)
        {
            if (this.MatchField_Dropdown.SelectedItem == null || this.MatchField_Dropdown.SelectedItem.ToString() == "" || this.ProjectNumber_Dropdown.SelectedItem == null || this.ProjectNumber_Dropdown.SelectedItem.ToString() == "")
            {
                this.SendDataButton.IsEnabled = false;
                this.MatchButton.IsEnabled = false;
            }
            else
            {
                this.SendDataButton.IsEnabled = true;
                this.MatchButton.IsEnabled = true;
            }
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

                // Query the rows of the table and print out a specific column
                string columnName = (string)this.MatchField_Dropdown.SelectedItem;

                Table table = null;
                await QueuedTask.Run(() =>
                {
                    // Access the table associated with the feature layer
                    table = featureLayer.GetTable();
                    if (table == null)
                    {
                        ArcGIS.Desktop.Framework.Dialogs.MessageBox.Show("No attribute table found for the selected feature layer.");
                        this.MatchButton.IsEnabled = true;
                        return;
                    }

                    using (RowCursor rowCursor = table.Search())
                    {
                        while (rowCursor.MoveNext())
                        {
                            using (Row row = rowCursor.Current)
                            {
                                MatchSiteToEntry(row, columnName);
                            }
                        }
                    }

                    // Get the TableView for the table
                    var tablePane = TableView.Active;
                    if (tablePane == null)
                        return;

                    // refresh
                    if (tablePane.CanRefresh)
                        tablePane.Refresh();
                });

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
        private async void BatchSiteMapperRefreshButtonClicked(object sender, RoutedEventArgs e)
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

        // Method to handle the click event of the SiteMapper button
        private async void BatchSiteMapperCleanButtonClicked(object sender, RoutedEventArgs e)
        {
            this.BatchSiteMapperCleanButton.IsEnabled = false;

            try
            {
                // Access the current map in ArcGIS Pro
                MapView mapView = MapView.Active;
                if (mapView == null)
                {
                    throw new Exception("No active map view found.");
                }

                // Get the first selected feature layer from the active map view
                FeatureLayer featureLayer = mapView.GetSelectedLayers().OfType<FeatureLayer>().FirstOrDefault();
                if (featureLayer == null)
                {
                    throw new Exception("Please select a feature layer in the Drawing Order and try again.");
                }

                Table table = null;
                await QueuedTask.Run(() =>
                {
                    // Access the table associated with the feature layer
                    table = featureLayer.GetTable();
                    if (table == null)
                    {
                        throw new Exception("No attribute table found for the selected feature layer.");
                    }

                    var selection = featureLayer.GetSelection();
                    var selectedOids = selection.GetObjectIDs();
                    if (selectedOids == null || selectedOids.Count == 0)
                    {
                        throw new Exception("No features selected.");
                    }

                    // Iterate through the selected rows and update the "bt_site_id" field
                    QueryFilter queryFilter = new QueryFilter()
                    {
                        ObjectIDs = selectedOids
                    };

                    using (RowCursor rowCursor = table.Search(queryFilter))
                    {
                        while (rowCursor.MoveNext())
                        {
                            using (Row row = rowCursor.Current)
                            {
                                row["bt_site_id"] = null;
                                row.Store();
                            }
                        }
                    }

                    // Get the TableView for the table
                    var tablePane = TableView.Active;
                    if (tablePane == null)
                        return;

                    // refresh
                    if (tablePane.CanRefresh)
                        tablePane.Refresh();
                });

                // Re-enable the Cleanup button after processing
                this.BatchSiteMapperCleanButton.IsEnabled = true;

            }
            catch (Exception ex)
            {
                // Show an error message if an exception occurs
                ArcGIS.Desktop.Framework.Dialogs.MessageBox.Show($"Error: {ex.Message}", "Error");

                // Re-enable the Cleanup button in case of an error
                this.BatchSiteMapperCleanButton.IsEnabled = true;
            }
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

        //
        private async void SiteMapperSendData(MapView mapView)
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

        //
        private async void SiteMapperSendDataBatch(MapView mapView)
        {
            // Get the first selected feature layer from the active map view
            FeatureLayer featureLayer = mapView.GetSelectedLayers().OfType<FeatureLayer>().FirstOrDefault();
            if (featureLayer == null)
            {
                ArcGIS.Desktop.Framework.Dialogs.MessageBox.Show("Please select a feature layer in the Drawing Order and try again.");
                this.MatchButton.IsEnabled = true;
                return;
            }

            if ((bool)this.OverwriteToggle.IsChecked)
            {
                await ExecuteBatchUpdateDataToolAsync(featureLayer);
            }
            else
            {
                await ExecuteBatchInsertDataToolAsync(featureLayer);
            }
        }

        //
        private async Task<bool> SiteMapperCheckGeometryExistInDB(MapView mapView)
        {
            // Get the first selected feature layer from the active map view
            FeatureLayer featureLayer = mapView.GetSelectedLayers().OfType<FeatureLayer>().FirstOrDefault();
            if (featureLayer == null)
            {
                ArcGIS.Desktop.Framework.Dialogs.MessageBox.Show("Please select a feature layer in the Drawing Order and try again.");
                return false;
            }

            bool foundGeometry = await ExecuteCheckGeometryExistsToolAsync(featureLayer);
            return foundGeometry;
        }

        //
        private async void MatchSiteToEntry(Row row, string columnName)
        {
            string value = (string)row[columnName];

            foreach (DataEntry entry in dataEntries)
            {
                // Split the site name into significant parts for matching
                string[] parts = entry.SiteName.Split(new[] { ' ', ':', '#', '-', '_' }, StringSplitOptions.RemoveEmptyEntries);

                // Escape special characters in each part for regex matching
                string[] escapedParts = parts.Select(Regex.Escape).ToArray();

                // 
                bool matched = ContainsMostParts(value, escapedParts);
                if (matched)
                {
                    await QueuedTask.Run(() =>
                    {
                        try
                        {
                            // Update the row with the matched SiteID
                            row["bt_site_id"] = entry.SiteID;

                            // Store the changes to the table
                            row.Store();
                        }
                        catch (Exception ex)
                        {
                            // Handle any exceptions that occur during the row update
                            ArcGIS.Desktop.Framework.Dialogs.MessageBox.Show($"Error updating row: {ex.Message}", "Error");
                        }
                    });
                }
            }
                        
        }

        // Custom function to check if most parts of the site name are present in the input
        bool ContainsMostParts(string input, string[] parts)
        {
            int matchCount = parts.Count(part => Regex.IsMatch(input, $@"\b{part}\b", RegexOptions.IgnoreCase));
            return matchCount >= (parts.Length * 0.75); // Adjust threshold as needed
        }

        // 
        void AddStaticDataLayers()
        {
            // Add static layers to the ObservableCollection
            dataLayersToAdd.Clear(); // Clear the ObservableCollection first
            dataLayersToAdd.Add(new DataLayer()
            {
                Table = "site_points",
                Name = "2BT Site Points",
                GeomType = esriGeometryType.esriGeometryPoint,
                ObjectIDColumn = "id",
                Year = null,
                ProjectNum = null,
                Disabled = false
            });

            dataLayersToAdd.Add(new DataLayer()
            {
                Table = "site_buffered_points",
                Name = "2BT Site Buffered Points",
                GeomType = esriGeometryType.esriGeometryPolygon,
                ObjectIDColumn = "id",
                Year = null,
                ProjectNum = null,
                Disabled = false
            });

            dataLayersToAdd.Add(new DataLayer()
            {
                Table = "valid_geometry",
                Name = "2BT Site Polygons",
                GeomType = esriGeometryType.esriGeometryPolygon,
                ObjectIDColumn = "id",
                Year = null,
                ProjectNum = null,
                Disabled = false
            });
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
        private async Task<bool> ExecuteBatchInsertDataToolAsync(FeatureLayer featureLayer)
        {
            try
            {
                // Set the parameters
                string toolboxPath = this.ArcPythonToolboxPath.Text + "\\BatchInsertDataTool";
                string connectionFile = this.ArcConnectionFilePath.Text;
                string tableName = this.DatabaseSchema.Text + ".site_geometry";

                // Execute the Python tool and get the result
                var parameters = Geoprocessing.MakeValueArray(connectionFile, tableName, featureLayer);
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

        // Method to execute the Update Data tool asynchronously
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

        // Method to execute the  Batch Update Data tool asynchronously
        private async Task<bool> ExecuteBatchUpdateDataToolAsync(FeatureLayer featureLayer)
        {
            try
            {
                // Set the parameters
                string toolboxPath = this.ArcPythonToolboxPath.Text + "\\BatchUpdateDataTool";
                string connectionFile = this.ArcConnectionFilePath.Text;
                string tableName = this.DatabaseSchema.Text + ".site_geometry";

                // Execute the Python tool and get the result
                var parameters = Geoprocessing.MakeValueArray(connectionFile, tableName, featureLayer);
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

        // Method to execute the Check Geomtry Exists tool asynchronously, returns false if no issues arise
        private async Task<bool> ExecuteCheckGeometryExistsToolAsync(FeatureLayer featureLayer)
        {
            try
            {
                // Set the parameters
                string toolboxPath = this.ArcPythonToolboxPath.Text + "\\CheckGeometryExists";
                string connectionFile = this.ArcConnectionFilePath.Text;
                string tableName = this.DatabaseSchema.Text + ".site_geometry";

                // Execute the Python tool and get the result
                var parameters = Geoprocessing.MakeValueArray(connectionFile, tableName, featureLayer);
                var returnValue = await Geoprocessing.ExecuteToolAsync(toolboxPath, parameters);

                if (returnValue.IsFailed)
                {
                    throw new Exception("The CheckGeometryExists Python tool failed");
                }

                // A return value of "1" indicates no duplicates were found
                if (returnValue.ReturnValue == "1")
                {
                    return false;
                }

                // Split by semicolon to get individual lists
                string[] lists = returnValue.ReturnValue.Split(';');

                // Initialize variables to store parsed values
                string numberOfOccurrences = "";
                List<string> allIds = new List<string>();
                List<string> allSiteIds = new List<string>();

                // Ensure there are enough lists to proceed safely
                foreach (string listStr in lists)
                {
                    // Process each list (assuming it contains the data you need)
                    string trimmedListStr = listStr.Trim('[', ']');
                    string[] parts = trimmedListStr.Split(',');

                    // Extract values assuming a specific order (adjust as needed)
                    if (parts.Length >= 3)
                    {
                        numberOfOccurrences = parts[0].Trim();

                        // Collect IDs and SiteIDs
                        string ids = parts[1].Trim();
                        string siteIds = parts[2].Trim();

                        // Add to the lists (if more than one)
                        allIds.Add(ids);
                        allSiteIds.Add(siteIds);
                    }
                }

                // Join multiple IDs and SiteIDs with commas
                string joinedIds = string.Join(", ", allIds);
                string joinedSiteIds = string.Join(", ", allSiteIds);

                // Construct the message
                string message = $"{numberOfOccurrences} Duplicate geometries have been found in the database for the geometry selected:\n" +
                                 $"     ID's: {joinedIds}\n" +
                                 $"     SiteID's: {joinedSiteIds}\n\n" +
                                 "Press OK if you still wish to commit the geometry to the database or Cancel to abort";


                // Displaying a message box with OK/Cancel buttons
                MessageBoxResult buttonResult = ArcGIS.Desktop.Framework.Dialogs.MessageBox.Show(
                    message, "Warning", MessageBoxButton.OKCancel);

                // Checking the result of the message box
                if (buttonResult == MessageBoxResult.OK) // OK button was clicked
                {
                    return false;
                }
            }
            catch (Exception ex)
            {
                // Handle any exceptions that occur during tool execution
                ArcGIS.Desktop.Framework.Dialogs.MessageBox.Show($"Error: {ex.Message}", "Error");
            }

            return true;
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
        // ******************************************************
        // Old Functions that can be pieced out or used later
        // ******************************************************
        #region Old Functions

        /*// Method to handle the click event of the Match Button
        private async void OLDMatchButtonClicked(object sender, RoutedEventArgs e)
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
        }*/

        #endregion
    }
}
