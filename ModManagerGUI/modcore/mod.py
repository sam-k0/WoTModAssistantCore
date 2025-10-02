import xml.etree.ElementTree as ET

class ModInfo:
    def __init__(self, 
                 modName="unknown", 
                 modID="unknown", 
                 packageID="unknown", 
                 version="0.0", 
                 description="", 
                 localFileName=None, 
                 isEnabled=False,
                 xmlstr=None):
        self.ModName = modName
        self.ModID = modID
        self.PackageID = packageID
        self.Version = version
        self.Description = description
        self.LocalFileName = localFileName
        self.IsEnabled = isEnabled

        # Constructor from XML
        if xmlstr is not None:
            try:
                xmlDoc = ET.fromstring(xmlstr)

                if self._xml_key_exists(xmlDoc, "name"):
                    self.ModName = xmlDoc.findtext("name")

                if self._xml_key_exists(xmlDoc, "version"):
                    self.Version = xmlDoc.findtext("version")

                if self._xml_key_exists(xmlDoc, "id"):
                    self.PackageID = xmlDoc.findtext("id")

                if self._xml_key_exists(xmlDoc, "description"):
                    self.Description = xmlDoc.findtext("description")

                if self._xml_key_exists(xmlDoc, "wgid"):
                    self.ModID = xmlDoc.findtext("wgid")

            except ET.ParseError:
                print("Error parsing xml string!!! Root is missing!")

    def __str__(self):
        return (
            f"Mod Name: {self.ModName}\n"
            f"Mod ID: {self.ModID}\n"
            f"Package ID: {self.PackageID}\n"
            f"Version: {self.Version}\n"
            f"Description: {self.Description}\n"
            f"Local File Name: {self.LocalFileName}\n"
            f"Is Enabled: {self.IsEnabled}\n"
        )

    def _xml_key_exists(self, xmlDoc, keyToCheck):
        return xmlDoc.find(keyToCheck) is not None
