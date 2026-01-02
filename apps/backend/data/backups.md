# Database Backup Guide

## Backup Script

The backup script `backup_db.sh` automatically:
- Creates timestamped backups: `db_backup_YYYYMMDD_HHMMSS.sqlite3`
- Stores backups in the `backups/` directory
- Keeps only the last 7 backups (auto-deletes older ones)
- Uses SQLite's `.backup` command for safe backups (falls back to `cp` if unavailable)

## Manual Backup

Run the backup script manually whenever needed:

```bash
./data/backup_db.sh
```

## Automated Daily Backups

### Option 1: Cron Job (WSL2/Linux)

⚠️ **Important:** Cron jobs in WSL2 only run when WSL2 is running. If you shut down WSL2, scheduled jobs won't execute.

To set up daily backups at 2 AM:

```bash
# Open crontab editor
crontab -e

# Add this line:
0 2 * * * /home/philippe/projects/cab/data/backup_db.sh >> /home/philippe/projects/cab/data/backups/backup.log 2>&1
```

**Verify cron job is added:**
```bash
crontab -l
```

**View backup logs:**
```bash
cat data/backups/backup.log
```

### Option 2: Windows Task Scheduler (Recommended for WSL2)

More reliable for WSL2 users since it doesn't depend on WSL2 being continuously running:

1. Open **Windows Task Scheduler**
2. Click **Create Basic Task**
3. Name: "Database Backup - CAB"
4. Trigger: **Daily** at **2:00 AM**
5. Action: **Start a program**
   - Program: `wsl`
   - Arguments: `/home/philippe/projects/cab/data/backup_db.sh`
6. Finish and test

## Restore from Backup

### Step 1: Choose a backup

List available backups:
```bash
ls -lh data/backups/db_backup_*.sqlite3
```

### Step 2: Stop Django

Make sure no Django processes are running:
```bash
# Stop development server if running
# Press Ctrl+C in the terminal running the server
```

### Step 3: Restore

```bash
# Replace YYYYMMDD_HHMMSS with your chosen backup timestamp
cp data/backups/db_backup_YYYYMMDD_HHMMSS.sqlite3 data/db.sqlite3
```

### Step 4: Verify

```bash
python manage.py shell -c "from profiles.models import Profile; print(f'Users: {Profile.objects.count()}')"
```

## Backup Before Risky Operations

Always backup before:
- Running migrations: `./data/backup_db.sh && python manage.py migrate`
- Major data imports/changes
- Database schema modifications
- Restoring from old backups

## Backup Storage

Current backup location: `data/backups/`

**Backups are stored locally only.** Consider:
- Adding `data/backups/` to cloud sync (Dropbox, Google Drive, etc.)
- Copying important backups to external storage
- The backup directory keeps only the last 7 backups automatically