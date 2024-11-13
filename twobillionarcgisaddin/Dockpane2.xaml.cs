using ArcGIS.Desktop.Framework.Threading.Tasks;
using ArcGIS.Desktop.Mapping;
using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Media;


namespace twobillionarcgisaddin
{
    /// <summary>
    /// Interaction logic for SiteMapperDataGridView.xaml
    /// </summary>
    public partial class SiteMapperDataGridView : UserControl
    {
        private static SiteMapperDataGridView _this = null;
        static public SiteMapperDataGridView MySiteMapperDataGridView => _this;
        public SiteMapperDataGridView()
        {
            InitializeComponent();

            _this = this;
        }

        // Declare ObservableCollection<DataEntry>
        public ObservableCollection<DataEntry> ProjectItems { get; set; } = new ObservableCollection<DataEntry>();

        public void ClearDataGrid()
        {
            this.ProjectItems.Clear(); // Clears the ObservableCollection and updates the UI
        }

        // Add this function to populate the DataGrid with the dictionary
        public void PopulateDataGrid(DataContainer container, Dictionary<string, string> filter = null, string siteNameFitler = null)
        {
            // Clear existing rows in the DataGrid
            this.ProjectItems.Clear();

            // Iterate through the dictionary and add rows to the DataGrid
            foreach (var entry in container.Data)
            {
                if  ( filter == null || (
                    (string.IsNullOrEmpty(filter["ProjectNumber"]) || filter["ProjectNumber"] == entry.ProjectNumber) &&
                    (string.IsNullOrEmpty(filter["SiteID"]) || filter["SiteID"] == entry.SiteID) &&
                    (string.IsNullOrEmpty(filter["Year"]) || entry.SiteID.StartsWith(filter["Year"][filter["Year"].Length - 1])
                    )))
                {
                    if (string.IsNullOrEmpty(siteNameFitler) || entry.SiteName.ToLower().StartsWith(siteNameFitler.ToLower()))
                    {
                        // Add the object to the DataGrid
                        this.ProjectItems.Add(entry);
                    }
                }
            }

            SiteMapperDataGrid.ItemsSource = ProjectItems;
        }

        private void SiteNameFilterTextBox_TextChanged(object sender, TextChangedEventArgs e)
        {
            TwoBillionTreesToolLogisticsView dockpane1 = TwoBillionTreesToolLogisticsView.MyTwoBillionTreesToolLogisticsView;
            PopulateDataGrid(dockpane1.dataContainer, dockpane1.GetSiteMapperFilter(), this.SiteNameFilterTextBox.Text);
        }

        private void ZoomToSelectedButton(object sender, RoutedEventArgs e)
        {
            // Access the current map in ArcGIS Pro
            MapView mapView = MapView.Active;

            if (mapView != null)
            {
                QueuedTask.Run(() =>
                {
                    mapView.ZoomToSelected();
                });
            }
        }
    }
}
