# ModManagerGUI

Please see the `readme.md` file in parent directory for general information.

## Building (Linux)
- python 3.11+
- pyside6
- pyinstaller

Make sure you have a subdirectory `Core` that includes a functional install of ModManagerCore!

Run `pyinstaller --add-data "Core:Core" main.py`.
Now run `./dist/main/main`.

* You can change the executable name as a flag in pyinstaller. Please help yourself.
