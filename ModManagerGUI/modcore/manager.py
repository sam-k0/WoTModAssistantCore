import os
import json
import zipfile
import shutil
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from .config import ConfigIO, Config
from .mod import ModInfo
from typing import List, Tuple

# ---- Enums & Output ----
class ErrorCode(Enum):
    Success = 0
    FilesystemFailed = 1
    ModNotFound = 2


class ActionCode(Enum):
    Install = 0
    Uninstall = 1
    Toggle = 2
    MoveToNew = 3
    SetAll = 4
    List = 5
    GetFolders = 6
    Setup = 7


@dataclass
class Output:
    message: str
    errorCode: ErrorCode
    actionCode: ActionCode

    def get_full_json(self):
        return json.dumps({
            "message": self.message,
            "errorCode": self.errorCode.value,
            "actionCode": self.actionCode.value
        })


# ---- Main ModManager ----
class ModManager:
    def __init__(self, json_output=True):
        self.json_output = json_output
        ConfigIO.clear_extract_folder()
        self.config = ConfigIO.read_config()
        if self.config is None or not self.config.GameInstallDir:
            raise Exception("Missing or invalid config file.")

    def _log(self, message: str, code: ErrorCode, action: ActionCode) -> Output:
        output = Output(message, code, action)
        if not self.json_output:
            print(message)
        return output

    # --- Helpers ---
    def _mods_root(self) -> str:
        cfg = ConfigIO.read_config()
        if cfg is None or cfg.GameInstallDir is None:
            raise Exception("No GameInstallDir in config")
        return os.path.join(cfg.GameInstallDir, "mods")

    def _version_folders(self) -> list[str]:
        path = self._mods_root()
        folders = []
        for sub in os.listdir(path):
            full = os.path.join(path, sub)
            if not os.path.isdir(full):
                continue
            if any(bad in sub for bad in ["config", "temp"]):
                continue
            if all(c.isdigit() or c == "." for c in sub):
                folders.append(full)
        folders.sort()
        return folders

    def _newest_version_folder(self) -> str:
        folders = self._version_folders()
        if not folders:
            raise Exception("No version folders found.")
        return folders[-1]

    def _extract_meta(self, file_path: str) -> ModInfo:
        extract_dir = ConfigIO.get_extract_folder()
        with zipfile.ZipFile(file_path, "r") as zf:
            zf.extractall(extract_dir)
        xml_path = os.path.join(extract_dir, "meta.xml")
        if not os.path.exists(xml_path):
            ConfigIO.clear_extract_folder()
            return ModInfo(
                modName=os.path.basename(file_path),
                modID="unknown",
                packageID=os.path.basename(file_path),
                version="0.0.0",
                description="No description",
                localFileName=os.path.basename(file_path),
                isEnabled=False,
            )
        with open(xml_path, "r") as f:
            xml_data = f.read()
        mod = ModInfo(xmlstr=xml_data)
        ConfigIO.clear_extract_folder()
        return mod

    # --- Commands ---
    def list_mods(self, keyword="all") -> Output:
        mods_dir = self._newest_version_folder()
        mods = self._get_installed_mods(mods_dir)

        results = []
        for mod in mods:
            if keyword == "all" or keyword.lower() in mod.ModName.lower():
                results.append(json.dumps(mod.__dict__))

        return self._log(json.dumps(results), ErrorCode.Success, ActionCode.List)

    def _get_installed_mods(self, version_dir: str) -> list[ModInfo]:
        mods = []
        for file in Path(version_dir).glob("*.wotmod*"):
            enabled = not file.name.endswith(".disabled")
            mod = self._extract_meta(str(file))
            mod.IsEnabled = enabled
            mods.append(mod)
        return mods

    def install_mod(self, filename: str) -> Output:
        mods_dir = self._newest_version_folder()
        if not os.path.exists(filename):
            return self._log("Mod file not found.", ErrorCode.ModNotFound, ActionCode.Install)
        try:
            shutil.copy2(filename, mods_dir)
        except Exception as e:
            return self._log(str(e), ErrorCode.FilesystemFailed, ActionCode.Install)
        return self._log(f"Installed {os.path.basename(filename)}", ErrorCode.Success, ActionCode.Install)

    def uninstall_mod(self, package_id: str) -> Output:
        mods_dir = self._newest_version_folder()
        found = False
        for file in Path(mods_dir).glob("*.wotmod*"):
            if package_id.lower() in file.name.lower():
                found = True
                try:
                    file.unlink()
                except Exception as e:
                    return self._log(str(e), ErrorCode.FilesystemFailed, ActionCode.Uninstall)
        if not found:
            return self._log("Mod not found.", ErrorCode.ModNotFound, ActionCode.Uninstall)
        return self._log(f"Uninstalled {package_id}", ErrorCode.Success, ActionCode.Uninstall)

    def toggle_mod(self, package_id: str) -> Output:
        mods_dir = self._newest_version_folder()
        found = False
        for file in Path(mods_dir).glob("*.wotmod*"):
            if package_id.lower() in file.name.lower():
                found = True
                new_name = file.with_suffix(file.suffix + ".disabled") if not file.name.endswith(".disabled") else file.with_suffix("")
                try:
                    os.rename(file, new_name)
                except Exception as e:
                    return self._log(str(e), ErrorCode.FilesystemFailed, ActionCode.Toggle)
        if not found:
            return self._log("Mod not found.", ErrorCode.ModNotFound, ActionCode.Toggle)
        return self._log(f"Toggled {package_id}", ErrorCode.Success, ActionCode.Toggle)

    def move_to_newest_from(self, origin_folder:str) -> Output:
        folders = self._version_folders()
        if len(folders) < 2:
            return self._log("No older version to move from.", ErrorCode.FilesystemFailed, ActionCode.MoveToNew)
        newest = folders[-1]

        for mod in Path(origin_folder).glob("*.wotmod*"):
            dest = Path(newest) / mod.name
            if not dest.exists():
                shutil.copy2(mod, dest)

        return self._log("Moved mods to newest folder.", ErrorCode.Success, ActionCode.MoveToNew)


    def move_from_newest_to(self, destination_folder:str)->Output:
        folders = self._version_folders()
        if len(folders) < 2:
            return self._log("No older version to move from.", ErrorCode.FilesystemFailed, ActionCode.MoveToNew)
        newest = folders[-1]

        for mod in Path(newest).glob("*.wotmod*"):
            dest = Path(destination_folder) / mod.name
            if not dest.exists():
                shutil.copy2(mod, dest)

        return self._log("Moved mods to newest folder.", ErrorCode.Success, ActionCode.MoveToNew)


    def set_all(self, enable: bool) -> Output:
        mods_dir = self._newest_version_folder()
        for file in Path(mods_dir).glob("*.wotmod*"):
            if enable and file.name.endswith(".disabled"):
                os.rename(file, file.with_suffix(""))  # remove .disabled
            elif not enable and not file.name.endswith(".disabled"):
                os.rename(file, file.with_suffix(file.suffix + ".disabled"))
        state = "enabled" if enable else "disabled"
        return self._log(f"Set all mods {state}", ErrorCode.Success, ActionCode.SetAll)

    def get_folders(self, mode="all") -> Output:
        folders = self._version_folders()
        if mode == "newest":
            return self._log(folders[-1], ErrorCode.Success, ActionCode.GetFolders)
        return self._log(json.dumps(folders), ErrorCode.Success, ActionCode.GetFolders)

    def about(self) -> Output:
        msg = {
            "name": "World of Tanks Mod Assistant",
            "version": "1.0.0 (Python Port)",
            "author": "sam-k0",
            "license": "MIT"
        }
        return self._log(json.dumps(msg), ErrorCode.Success, ActionCode.Setup)
    
    # Parsing

    def output_split(self,output:Output):
        return output.message, output.errorCode, output.actionCode
    
    def output_split_json(self, output:Output):
        return json.loads(output.message), output.errorCode, output.actionCode
    
    def __parse_mod(self,modstr:str)->ModInfo:
        jmod = json.loads(modstr)
        return ModInfo(
            jmod["ModName"],
            jmod["ModID"],
            jmod["PackageID"], 
            jmod["Version"], 
            jmod["Description"], 
            jmod["LocalFileName"], 
            jmod["IsEnabled"]
        )
        

    def parse_mods_list(self, msg:str)->List[ModInfo]:

        message = json.loads(msg)
        # parse every element in message list to json and create a Mod object
        mods = []
        for modstr in message:
            mods.append(self.__parse_mod(modstr))
        return mods

if __name__ == "__main__":
    m = ModManager()
    print(m.about().get_full_json())
