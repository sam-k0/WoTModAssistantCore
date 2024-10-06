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

# assume we are in venv so we can use pyinstaller
# we need to add the publish/Core directory
pyinstaller --add-data "../publish/Core:Core" --name ModManagerGUI --windowed main.py

echo "Build can be found in ModManagerGUI/dist/ModManagerGUI"
