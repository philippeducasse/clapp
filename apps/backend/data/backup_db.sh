#!/bin/bash

# Change to the script's directory to ensure relative paths work
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

BACKUP_DIR="backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_PATH="db.sqlite3"
BACKUP_FILE="$BACKUP_DIR/db_backup_$DATE.sqlite3"

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

# Use SQLite's .backup command for a safe, consistent backup
# Falls back to cp if sqlite3 is not available
if command -v sqlite3 &> /dev/null; then
    sqlite3 $DB_PATH ".backup '$BACKUP_FILE'"
    echo "Backup created using SQLite .backup: $BACKUP_FILE"
else
    cp $DB_PATH $BACKUP_FILE
    echo "Backup created using cp: $BACKUP_FILE"
fi

# Keep only last 7 backups
ls -t $BACKUP_DIR/db_backup_*.sqlite3 2>/dev/null | tail -n +8 | xargs -r rm

echo "✓ Backup completed: $BACKUP_FILE"