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
        self.installation_path ="/home/sam/Applications/WoTMod/ModManagerCore"

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
        arglist = ["--move", keyword]
        out = self.invoke(arglist)
        return out

    def invoke(self, args:list, json_output=True):
        # prepend args list with json_args if json_output is True
        if json_output:
            args = ["-o","json"] + args
        # prepend installation path to args list
        args = [self.installation_path] + args
        # invoke the ModManagerCore with the args list
        popen = subprocess.Popen(args, stdout=subprocess.PIPE)
        popen.wait()
        output = popen.stdout.read()
        return output
    

if __name__ == '__main__':
    core = ModManagerCore()
    arglist = ["--list", "all"]
    out = core.invoke(arglist)
    mods, errcode, actioncode = core.parse_mods_list(out)

    print(mods[0].name)


    sys.exit(0)
