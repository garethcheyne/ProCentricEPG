#!/bin/bash

# Enable strict error handling
set -e

# Define paths
REPO_DIR="/root/ProCentricEPG"
VENV_PATH="$REPO_DIR/venv/bin/activate"
SCRIPT_DIR="$REPO_DIR/src"
OUTPUT_DIR="$SCRIPT_DIR/output/EPG"
DEST_DIR="/home/procentric/EPG"
LOG_FILE="$REPO_DIR/epg_run.log"
CRON_LOG="/var/log/cron_epg.log"

# Discord Webhook URL
WEBHOOK_URL=""

# Log function
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE" >> "$CRON_LOG"
}

# Send a message to Discord
send_discord_notification() {
    local message="$1"
    curl -H "Content-Type: application/json" -X POST -d "{\"content\": \"$message\"}" "$WEBHOOK_URL"
}

log "Starting EPG script execution..."
send_discord_notification "✅ EPG update started..."

# Navigate to repository directory
cd "$REPO_DIR" || { log "Error: Failed to change directory to $REPO_DIR"; exit 1; }

# Pull latest updates from Git
log "Forcibly pulling latest updates from Git..."
git fetch origin main

# Reset local changes and forcefully match the remote branch
if git reset --hard origin/main; then
    log "Git repository updated successfully."
else
    log "Error: Git pull failed. Something went wrong while updating."
    exit 1
fi

# Activate virtual environment
if [ -f "$VENV_PATH" ]; then
    source "$VENV_PATH"
else
    log "Error: Virtual environment not found at $VENV_PATH"
    send_discord_notification "❌ EPG update failed: Virtual environment missing!"
    exit 1
fi

# Navigate to script directory
cd "$SCRIPT_DIR" || { log "Error: Failed to change directory to $SCRIPT_DIR"; exit 1; }



# Run the Python script
log "Running Python script..."
if python3 ./main.py; then
    log "Python script executed successfully."
else
    log "Python script execution failed."
    send_discord_notification "❌ EPG update failed during script execution!"
    exit 1
fi

# Ensure the output directory exists
if [ ! -d "$OUTPUT_DIR" ]; then
    log "Error: Output directory $OUTPUT_DIR does not exist."
    send_discord_notification "❌ EPG update failed: Output directory missing!"
    exit 1
fi

# Remove existing contents inside EPG directory
EPG_DIR="$DEST_DIR/EPG"
if [ -d "$EPG_DIR" ]; then
    log "Removing existing contents in $EPG_DIR..."
    rm -rf "$EPG_DIR"/*
else
    log "EPG directory does not exist, skipping removal."
fi

# Copy files to the destination directory
log "Copying files from $OUTPUT_DIR to $DEST_DIR..."
mkdir -p "$DEST_DIR"  # Ensure destination exists

if cp -r "$OUTPUT_DIR"/* "$DEST_DIR"/; then
    log "Files copied successfully to $DEST_DIR"
    send_discord_notification "✅ EPG update completed successfully!"
else
    log "Error: Failed to copy files."
    send_discord_notification "❌ EPG update failed while copying files!"
    exit 1
fi

log "Script completed successfully."
exit 0
