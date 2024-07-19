using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Data;
using System.Windows.Documents;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Navigation;
using System.Windows.Shapes;
using static twobillionarcgisaddin.TwoBillionTreesToolLogisticsView;

namespace twobillionarcgisaddin
{
    /// <summary>
    /// Interaction logic for DataLayerOptionsPopup.xaml
    /// </summary>
    public partial class DataLayerOptionsPopup : ArcGIS.Desktop.Framework.Controls.ProWindow
    {
        private DataLayer selectedDataLayer;

        public DataLayerOptionsPopup(DataLayer selectedDataLayer)
        {
            InitializeComponent();
            this.selectedDataLayer = selectedDataLayer;

            // Set the DataContext of the window to the selected item
            this.DataContext = selectedDataLayer;
        }

        // Handle the Cancel button click event
        private void CloseButton_Click(object sender, RoutedEventArgs e)
        {
            // Close the window
            this.Close();
        }
    }
}
