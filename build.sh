#!/usr/bin/env bash

set -e

echo "== Step 1: Installing dependencies =="
pip install --upgrade pip
pip install -r requirements.txt
echo "== Finished Step 1 =="

echo "== Step 2: Building the app =="
python setup.py py2app
echo "== Finished Step 2 =="

echo "== Step 3: Checking & installing 'create-dmg' if needed =="
which create-dmg || brew install create-dmg
echo "== Finished Step 3 =="

echo "== Step 4: Removing old DMG files =="
rm -f dist/*.dmg
echo "== Finished Step 4 =="

# Sign the .app
codesign -f -s "Developer ID Application: Mohammad Hamza Husain (86ZAL8H6TZ)" "dist/Mac Menubar App.app"


echo "== Step 5: Creating DMG =="
create-dmg --volname "Mac Menubar App" \
  --app-drop-link \
  "dist/Mac Menubar App.dmg" \
  "dist/Mac Menubar App.app"
echo "== Finished Step 5 =="

echo "== Step 6: Creating and uploading release =="
VERSION=${1:-"1.0.0"}
gh release create "$VERSION" "dist/Mac Menubar App.dmg" --title "Mac Menubar App $VERSION" --notes "Release $VERSION"
echo "== Finished Step 6 =="
echo "== Build script completed =="