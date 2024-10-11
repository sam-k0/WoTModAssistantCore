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
        # Should be in *this*/Core/ModManagerCore
        # The file on Windows is ModManagerCore.exe and on Linux it is ModManagerCore
        installation_path = ""
        if sys.platform == "win32":
            installation_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Core","ModManagerCore.exe")
        elif sys.platform == "linux":
            installation_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Core", "ModManagerCore")
        else:
            raise Exception("Unsupported platform: "+sys.platform)
        return installation_path

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
    
    #TODO: call this from the GUI
    def set_all_mods(self, enable:bool):
        arg = "enabled" if enable else "disabled"
        arglist = ["--set-all", arg]
        out = self.invoke(arglist)
        return out


    def invoke(self, args:list, json_output=True):
        # prepend args list with json_args if json_output is True
        if json_output:
            args = ["-o","json"] + args
        # prepend installation path to args list
        args = [self.installation_path] + args
        # invoke the ModManagerCore with the args list
        print("Running command: ", args)
        
        popen = None
        if sys.platform == "win32":#hide the console window on Windows
            popen = subprocess.Popen(args, stdout=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW)
        elif sys.platform == "linux":
            popen = subprocess.Popen(args, stdout=subprocess.PIPE)
        popen.wait()
        output = popen.stdout.read()
        print("Core output: ", output)
        return output
    
    def set_game_installation_dir(self, path:str)->bool:
        # check if the config file exists in ./Core/config.json
        if not os.path.isfile(os.path.join(os.path.dirname(self.installation_path), "config.json")):
            # missing, create it
            with open(os.path.join(os.path.dirname(self.installation_path), "config.json"), "w") as f:
                # serialize the json object
                f.write(json.dumps({"GameInstallDir":path}))
            return True
        else:
            return False
        
    def get_game_installation_dir(self)->str:
        # check if the config file exists in ./Core/config.json
        if not os.path.isfile(os.path.join(os.path.dirname(self.installation_path), "config.json")):
            # missing, return None
            return None
        else:
            # read the file and return the GameInstallDir
            with open(os.path.join(os.path.dirname(self.installation_path), "config.json"), "r") as f:
                return json.loads(f.read())["GameInstallDir"]
    

if __name__ == '__main__':
    print("This is the ModManagerCore invoker class")
