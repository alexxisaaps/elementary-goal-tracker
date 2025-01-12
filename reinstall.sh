#!/bin/sh

# Exit on any error
set -e

# Define paths
PROJECT_DIR="/home/alexis/Projects/elementary-goal-tracker"
BACKUP_DIR="$PROJECT_DIR/backup"
DATA_DIR="/home/alexis/.local/share/goaltracker"
SYSTEM_DATA_DIR="/usr/share/goaltracker"
APP_ID="io.github.alexxisaapps.elementary_goal_tracker"

echo "Backing up user data..."
# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Copy user data files if they exist
if [ -d "$DATA_DIR" ]; then
    cp -f "$DATA_DIR"/*.json "$BACKUP_DIR/" 2>/dev/null || true
    echo "User data backed up to $BACKUP_DIR"
else
    echo "No user data found to backup"
fi

echo "Removing old installation..."
# Remove system-wide installation files
sudo rm -rf "$SYSTEM_DATA_DIR"
sudo rm -f "/usr/bin/$APP_ID"
sudo rm -f "/usr/share/applications/$APP_ID.desktop"
sudo rm -f "/usr/share/metainfo/$APP_ID.metainfo.xml"
sudo rm -f "/usr/share/dbus-1/services/$APP_ID.service"
sudo rm -f "/usr/share/glib-2.0/schemas/$APP_ID.gschema.xml"

# Remove icons
for size in 16 24 32 48 64 128 512; do
    sudo rm -f "/usr/share/icons/hicolor/${size}x${size}/apps/$APP_ID.svg"
    sudo rm -f "/usr/share/icons/hicolor/${size}x${size}@2/apps/$APP_ID.svg"
done

echo "Cleaning build directory..."
cd "$PROJECT_DIR"
rm -rf build/

echo "Removing old Python modules..."
sudo rm -rf "/usr/share/goaltracker/goaltracker"

echo "Building and installing..."
# Configure and build with Meson
mkdir build
cd build
meson setup --prefix=/usr ..
ninja

# Install the application
sudo ninja install

echo "Compiling schemas..."
sudo glib-compile-schemas /usr/share/glib-2.0/schemas/

echo "Updating system caches..."
sudo update-desktop-database
sudo gtk-update-icon-cache /usr/share/icons/hicolor

echo "Restoring user data..."
# Create data directory if it doesn't exist
mkdir -p "$DATA_DIR"

# Copy backed up data files back if they exist
if [ -d "$BACKUP_DIR" ]; then
    cp -f "$BACKUP_DIR"/*.json "$DATA_DIR/" 2>/dev/null || true
    echo "User data restored from $BACKUP_DIR"
fi

# Ensure quotes.json is available
if [ ! -f "$DATA_DIR/quotes.json" ]; then
    cp -f "$SYSTEM_DATA_DIR/quotes.json" "$DATA_DIR/" 2>/dev/null || true
    echo "Installed default quotes.json"
fi

# Set proper permissions for user data directory
chmod 755 "$DATA_DIR"
chmod 644 "$DATA_DIR"/*.json 2>/dev/null || true

echo "Installation complete! You can now launch the application."