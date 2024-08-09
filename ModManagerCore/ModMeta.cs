using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Xml;

namespace ModAssistant
{
    public class ModInfo
    {
        public string ModName { get; set; } = "unknown"; // The display name of the mod
        public string ModID { get; set; } = "unknown"; // The ID of the mod, used for identifying the mod on wgmods
        public string PackageID { get; set; } = "unknown"; // using reverse Domain Name notation
        public string Version { get; set; } = "0.0"; // The version of the mod
        public string Description { get; set; } = ""; // The description of the mod
        public string LocalFileName { get; set; } // can be null , this is ONLY the filename, not the full path
        public bool IsEnabled { get; set; } = false; // For browse results this is obv false

        public ModInfo()
        {
        }

        public ModInfo(string modName, string modID, string author, string version, string description, string localFileName)
        {
            ModName = modName;
            ModID = modID;
            PackageID = author;
            Version = version;
            Description = description;
            LocalFileName = localFileName;
        }

        public ModInfo(string modName, string modID, string author, string version,
            string description, string localFileName, bool isEnabled)
        {
            ModName = modName;
            ModID = modID;
            PackageID = author;
            Version = version;
            Description = description;
            LocalFileName = localFileName;
            IsEnabled = isEnabled;
        }

        public ModInfo(string xmlstr, bool isEnabled, string localFileName)
        {
            Dictionary<string, string> xmlDict = new Dictionary<string, string>();

            XmlDocument xmlDoc = new XmlDocument();
            xmlDoc.LoadXml(xmlstr);

            XmlNode root = xmlDoc.DocumentElement;
            if (root != null)
            {
                foreach (XmlNode node in root.ChildNodes)
                {
                    xmlDict[node.Name] = node.InnerText;
                }
            }else
            {
                System.Console.WriteLine("Error parsing xml string!!! Root is missing!");
            }

            // Bruh not all keys always exist
            if(xmlKeyExists(xmlDoc, "name"))
            {
                ModName = xmlDict["name"];
            }

            if (xmlKeyExists(xmlDoc, "version"))
            {
                Version = xmlDict["version"];
            }

            if (xmlKeyExists(xmlDoc, "id"))
            {
                PackageID = xmlDict["id"];
            }

            if (xmlKeyExists(xmlDoc, "description"))
            {
                Description = xmlDict["description"];
            }

            IsEnabled = isEnabled;
            LocalFileName = localFileName;

        }

        public override string ToString()
        {
            // Return information as a formatted string
            return "Mod Name: " + ModName + "\n" +
                   "Mod ID: " + ModID + "\n" +
                   "Package ID: " + PackageID + "\n" +
                   "Version: " + Version + "\n" +
                   "Description: " + Description + "\n" +
                   "Local File Name: " + LocalFileName + "\n" +
                   "Is Enabled: " + IsEnabled + "\n";
        }

        private bool xmlKeyExists(XmlDocument xmlDoc, string keyToCheck)
        {
            XmlNode node = xmlDoc.SelectSingleNode("//" + keyToCheck);

            return (node != null);
        }
    }
}