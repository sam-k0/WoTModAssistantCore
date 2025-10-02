import json
from enum import Enum
from dataclasses import dataclass

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

    def get_full_json(self) -> str:
        # Convert enum values to their numeric representation
        return json.dumps({
            "message": self.message,
            "errorCode": self.errorCode.value,
            "actionCode": self.actionCode.value
        })