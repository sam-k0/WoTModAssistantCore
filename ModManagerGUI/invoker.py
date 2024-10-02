import subprocess
import sys
import os
import json

def invoke(args:list,mmpath="/home/sam/Applications/WoTMod/ModManagerCore", json_output=True):
    args.insert(0, mmpath)
    args.append("-o")
    args.append("json")
    print(args)
    popen = subprocess.Popen(args, stdout=subprocess.PIPE)
    popen.wait()
    output = popen.stdout.read()
    return output
