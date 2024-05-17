using System.Collections.Generic;
using System.ComponentModel;
using System.Text.Json;

namespace twobillionarcgisaddin
{
    public class DataEntry : INotifyPropertyChanged
    {
        private string _projectNumber;
        public string ProjectNumber
        {
            get { return _projectNumber; }
            set
            {
                if (_projectNumber != value)
                {
                    _projectNumber = value;
                    OnPropertyChanged(nameof(ProjectNumber));
                }
            }
        }

        private string _siteID;
        public string SiteID
        {
            get { return _siteID; }
            set
            {
                if (_siteID != value)
                {
                    _siteID = value;
                    OnPropertyChanged(nameof(SiteID));
                }
            }
        }

        private string _siteName;
        public string SiteName
        {
            get { return _siteName; }
            set
            {
                if (_siteName != value)
                {
                    _siteName = value;
                    OnPropertyChanged(nameof(SiteName));
                }
            }
        }

        // Constructor
        public DataEntry(string projectNumber, string siteID, string siteName)
        {
            ProjectNumber = projectNumber;
            SiteID = siteID;
            SiteName = siteName;
        }

        public event PropertyChangedEventHandler PropertyChanged;

        protected virtual void OnPropertyChanged(string propertyName)
        {
            PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
        }
    }

    public class DataContainer
    {
        public List<DataEntry> Data { get; private set; }

        public DataContainer(string rawJSONString)
        {
            Data = new List<DataEntry>();
            ProcessRawString(rawJSONString);
        }

        public void ProcessRawString(string rawJSONString)
        {
            // Parse the JSON string
            JsonDocument jsonDocument = JsonDocument.Parse(rawJSONString);

            // Access the parsed data
            JsonElement dataElement = jsonDocument.RootElement.GetProperty("data");

            foreach (JsonElement rowElement in dataElement.EnumerateArray())
            {
                // Access properties by index
                string projectNumber = rowElement[0].ToString();
                string siteID = rowElement[1].ToString();
                string siteName = rowElement[2].ToString();

                // Create a DataEntry object with the row data
                DataEntry entry = new DataEntry(projectNumber, siteID, siteName);

                // Add the entry to the list
                Data.Add(entry);
            }
        }

        public DataEntry GetDataEntryBySiteID(string siteID)
        {
            // Find the DataEntry with the given SiteID
            return Data.Find(entry => entry.SiteID == siteID);
        }
    }
}
