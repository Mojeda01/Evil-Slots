import subprocess
from datetime import datetime
import os

db_user = os.getenv("marcoojeda")

def backup_database(db_name, backup_dir):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"{backup_dir}/{db_name}_backup_{timestamp}.sql"
    
    try:
        subprocess.run(["pg_dump", "-U", db_user, "-d", db_name, "-f", backup_file], check=True)
        print(f"Backup created successfully: {backup_file}")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while creating the backup: {e}")

def restore_database(db_name, backup_file):
    try:
        subprocess.run(["psql", "-U", db_user, "-d", db_name, "-f", backup_file], check=True)
        print(f"Database restored successfully from {backup_file}")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while restoring the database: {e}")

# Usage
# backup_database("slot_machine_db", "/path/to/backup/directory")
# restore_database("slot_machine_db", "/path/to/backup/file.sql")
