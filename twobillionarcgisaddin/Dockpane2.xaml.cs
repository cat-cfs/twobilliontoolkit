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
                    (string.IsNullOrEmpty(filter["SiteID"]) || filter["SiteID"] == entry.SiteID)          
                    ))
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

        /*private object originalValue; // Store the original value globally

        private void CellBeginningEdit(object sender, DataGridBeginningEditEventArgs e)
        {
            // Store the original value when editing begins
            var selectedItem = SiteMapperDataGrid.SelectedItem;
            var propertyName = SiteMapperDataGrid.CurrentColumn.SortMemberPath;
            originalValue = selectedItem.GetType().GetProperty(propertyName).GetValue(selectedItem, null);
        }

        private void CellEditEnding(object sender, DataGridCellEditEndingEventArgs e)
        {
            if (e.EditAction == DataGridEditAction.Commit)
            {
                // Access the edited cell and apply the desired style or color
                var editedCell = e.EditingElement as TextBox;

                if (editedCell != null)
                {
                    // Get the DataGridCell container for the edited cell
                    DataGridCell cell = GetCell(e.Row, e.Column);

                    // Get the new value from the edited cell
                    var newValue = editedCell.Text;

                    // Check if the text has changed
                    if (originalValue.ToString() != newValue)
                    {
                        // Set the background color of the DataGridCell
                        cell.Foreground = Brushes.Red;
                    }
                }
            }
        }

        private DataGridCell GetCell(DataGridRow row, DataGridColumn column)
        {
            var cellContent = column.GetCellContent(row);

            if (cellContent != null)
            {
                return (DataGridCell)cellContent.Parent;
            }

            return null;
        }*/
    }
}
