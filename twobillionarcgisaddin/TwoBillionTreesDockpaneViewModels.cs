using ArcGIS.Desktop.Framework;
using ArcGIS.Desktop.Framework.Contracts;


namespace twobillionarcgisaddin
{
    internal class TwoBillionTreesDockpaneViewModel1 : DockPane
    {
        private const string _dockPaneID = "TwoBillionTrees_Dockpane1";

        public TwoBillionTreesDockpaneViewModel1(){}

        /// <summary>
        /// Show the DockPane.
        /// </summary>
        internal static void Show()
        {
            DockPane pane = FrameworkApplication.DockPaneManager.Find(_dockPaneID);
            if (pane == null)
                return;

            pane.Activate();
        }

        /// <summary>
        /// Text shown near the top of the DockPane.
        /// </summary>
        private string _heading = "Site Mapper";
        public string Heading
        {
            get => _heading;
            set => SetProperty(ref _heading, value);
        }
    }

    internal class TwoBillionTreesDockpaneViewModel2 : DockPane
    {
        private const string _dockPaneID = "TwoBillionTrees_Dockpane2";

        public TwoBillionTreesDockpaneViewModel2() { }

        /// <summary>
        /// Show the DockPane.
        /// </summary>
        internal static void Show()
        {
            DockPane pane = FrameworkApplication.DockPaneManager.Find(_dockPaneID);
            if (pane == null)
                return;

            pane.Activate();
        }

        /// <summary>
        /// Text shown near the top of the DockPane.
        /// </summary>
        private string _heading = "Site Mapper";
        public string Heading
        {
            get => _heading;
            set => SetProperty(ref _heading, value);
        }
    }

    /// <summary>
    /// Button implementation to show the DockPane.
    /// </summary>
    internal class TwoBillionTrees_Dockpane_ShowButton : Button
    {
        protected override void OnClick()
        {
            TwoBillionTreesDockpaneViewModel1.Show();
        }
    }
}
