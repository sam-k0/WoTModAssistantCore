#!/bin/bash

# Navigate to the project directory which is ./ModManagerCore
cd ./ModManagerCore

# Restore dependencies
dotnet restore

# Build the project
dotnet build --configuration Release

# Publish the project
dotnet publish --configuration Release --output ../publish/Core

echo "Build and publish completed."

# Build ModManagerGUI with pyinstaller
cd ../ModManagerGUI


# ask the user if they want to have a console window
echo "Do you want to have a console window? (y/n)"
read console

if [ "$console" = "y" ]; then
    pyinstaller --add-data "../publish/Core:Core" --name ModManagerGUI main.py --icon=ico.ico
    echo "Build can be found in ModManagerGUI/dist/ModManagerGUI"
    exit 0
fi

# assume we are in venv so we can use pyinstaller
# we need to add the publish/Core directory
pyinstaller --add-data "../publish/Core:Core" --name ModManagerGUI --windowed --icon=ico.ico main.py

echo "Build can be found in ModManagerGUI/dist/ModManagerGUI"
