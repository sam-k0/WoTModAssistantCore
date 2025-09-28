import subprocess
import sys
import os
import json

class Mod: # mirrors the Mod class in ModManagerCore
    def __init__(self, name:str, wgid:str, pckid:str, version:str, desc:str, localfilename:str, isenabled:bool):
        self.name = name
        self.wgid = wgid
        self.pckid = pckid
        self.version = version
        self.desc = desc
        self.localfilename = localfilename
        self.isenabled = isenabled

    def __repr__(self) -> str:
        return f"{self.name} (v{self.version}) - {self.pckid}"

class ModManagerCore:
    def __init__(self):
        # check if the ModManagerCore is in the same
        self.installation_path = self.__expected_core_path()
    def __expected_core_path(self):
        import sys
        import os

        # Determine base path
        if getattr(sys, "frozen", False):
            # PyInstaller bundle
            base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.realpath(__file__)))
        elif os.environ.get("FLATPAK_ID") is not None:
            # Running inside Flatpak sandbox
            base_path = "/app"
        else:
            # Development mode
            base_path = os.path.dirname(os.path.realpath(__file__))

        # Determine executable name by platform
        if sys.platform == "win32":
            core_name = "ModManagerCore.exe"
        elif sys.platform == "linux":
            core_name = "ModManagerCore"
        else:
            raise Exception("Unsupported platform: " + sys.platform)

        return os.path.join(base_path, "Core", core_name)

    def get_extraction_path(self):
        extract_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Core", "extract")
        if not os.path.isdir(extract_dir):
            os.mkdir(extract_dir)
        return extract_dir

    def __parse_mod(self, jstr:str):
        jmod = json.loads(jstr)
        return Mod(jmod["ModName"],
                   jmod["ModID"],
                   jmod["PackageID"], 
                   jmod["Version"], 
                   jmod["Description"], 
                   jmod["LocalFileName"], 
                   jmod["IsEnabled"])

    def __parse_mods_list(self, output:str):
            parent = json.loads(output)
            message_raw = parent["message"] # json escaped string
            errcode = parent["errorCode"]
            actioncode = parent["actionCode"]

            if errcode != 0:
                return message_raw, errcode, actioncode

            message = json.loads(message_raw)
            # parse every element in message list to json and create a Mod object
            mods = []
            for modstr in message:
                mods.append(self.__parse_mod(modstr))
            return mods, errcode, actioncode
    
    # parse the output of the ModManagerCore json response
    def parse_response(self, output_json:str):
        try:
            parent = json.loads(output_json)
        except json.JSONDecodeError as e:
            return (str(output_json), -1, -1)
        else:
            return (parent["message"], parent["errorCode"], parent["actionCode"])

    def get_mods_list(self):
        arglist = ["--list", "all"]
        out = self.invoke(arglist)
        return self.__parse_mods_list(out)

    def get_mod(self, pckid:str):
        Exception("Not implemented")
        arglist = ["--list", pckid]
        out = self.invoke(arglist)
        mods, errcode, actioncode = self.__parse_mods_list(out)
        return mods[0]

    def install_mod(self, filename:str):
        arglist = ["--install", filename]
        out = self.invoke(arglist)
        return out
    
    def uninstall_mod(self, pckid:str):
        arglist = ["--uninstall", pckid]
        out = self.invoke(arglist)
        return out
    
    def move_mods(self, keyword:str):
        arglist = ["--move-to-new", keyword]
        out = self.invoke(arglist)
        return out
    
    # Raw function to get the mod folders, either returns string or list of strings in message
    def get_mod_folders(self, keyword:str):
        allowed = ["newest", "all"]
        if keyword not in allowed:
            raise Exception(f"Keyword must be one of {allowed}")
        arglist = ["--mod-folder", keyword]
        out = self.invoke(arglist)
        return out
    
    # returns a single string with the path to the newest mod folder
    def get_newest_mod_folder(self):
        resp = self.get_mod_folders("newest")
        msg, err, act = self.parse_response(resp)
        if err != 0:
            raise Exception(f"Error code {err} in response: {msg}")
        return msg
    
    def get_all_mod_folders(self)->list:
        resp = self.get_mod_folders("all")
        msg, err, act = self.parse_response(resp)
        if err != 0:
            raise Exception(f"Error code {err} in response: {msg}")
        # the msg is a json list of strings
        return json.loads(msg)
    
    def toggle_mod(self, pckid:str):
        arglist = ["--toggle", pckid]
        out = self.invoke(arglist)
        return out
    
    def set_all_mods(self, enable:bool):
        arg = "enabled" if enable else "disabled"
        arglist = ["--set-all", arg]
        out = self.invoke(arglist)
        return out


    def invoke(self, args: list, json_output=True):
        """
        Run the ModManagerCore executable with the given arguments.

        Args:
            args (list): List of command-line arguments.
            json_output (bool): If True, prepend '-o json' to the arguments.

        Returns:
            str: The standard output of the process as a decoded string.
        """

        # Prepend JSON output argument if requested
        if json_output:
            args = ["-o", "json"] + args

        # Prepend installation path to arguments
        args = [self.installation_path] + args
        print("Running command: ", args)

        # Configure subprocess
        popen = subprocess.Popen(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        # Safely read stdout and stderr
        output, errors = popen.communicate()

        # Decode bytes to string
        output_str = output.decode("utf-8", errors="replace").strip()
        errors_str = errors.decode("utf-8", errors="replace").strip()

        # Print outputs for debugging
        if output_str:
            print("Core output: ", output_str)
        if errors_str:
            print("Core errors: ", errors_str)

        # Raise exception if the core process failed
        if popen.returncode != 0:
            raise subprocess.CalledProcessError(popen.returncode, args, output=output_str, stderr=errors_str)

        return output_str
        
    def get_config_path(self) -> str:
        """Return the path to the config.json file in a writable location."""
        # Detect Flatpak runtime
        if os.environ.get("FLATPAK_ID"):
            config_dir = os.path.join(os.path.expanduser("~/.config"), "wotmodassistant")
        else:
            config_dir = os.path.join(os.path.dirname(self.installation_path), "Core")
        
        os.makedirs(config_dir, exist_ok=True)
        return os.path.join(config_dir, "config.json")


    def set_game_installation_dir(self, path: str) -> bool:
        config_path = self.get_config_path()
        
        if not os.path.isfile(config_path):
            with open(config_path, "w") as f:
                json.dump({"GameInstallDir": path}, f)
            return True
        else:
            return False


    def get_game_installation_dir(self) -> str:
        config_path = self.get_config_path()
        
        if not os.path.isfile(config_path):
            return None
        else:
            with open(config_path, "r") as f:
                return json.load(f).get("GameInstallDir")
            
    # move all mods to the newest version folder
    def move_all_to_newest_from_game_version(self, version_folder:str):
        arglist = ["--move-all-new-version", version_folder]
        out = self.invoke(arglist)
        return out
    
    def move_all_to_previous_version(self, version_folder:str):
        arglist = ["--move-all-previous-version", version_folder]
        out = self.invoke(arglist)
        return out
    
    def get_about(self):
        arglist = ["--about", "any"]
        out = self.invoke(arglist)
        return out

if __name__ == '__main__':
    print("This is the ModManagerCore invoker class")
