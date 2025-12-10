# 🚀 Setup Instructions - Auto-École Manager

## Problem: Database File Not Found

You're seeing this error:
```
sqlite3.OperationalError: unable to open database file
```

This means the database hasn't been created yet on your machine.

---

## Solution: Initialize the Database (1 Minute)

### Option 1: Use the Setup Script (Easiest)

Open Command Prompt in your project folder and run:

```bash
cd "C:\Users\DELL\Downloads\WTSP IMG\auto-ecole-main"
python setup_database.py
```

**This will**:
- ✅ Create the `data/` folder
- ✅ Create the database file `data/autoecole.db`
- ✅ Create all tables
- ✅ Add test data (users, students, instructors, vehicles, etc.)

### Option 2: Use the Batch File (Windows)

Double-click: `setup.bat`

Or from Command Prompt:
```bash
cd "C:\Users\DELL\Downloads\WTSP IMG\auto-ecole-main"
setup.bat
```

### Option 3: Manual Setup

```bash
cd "C:\Users\DELL\Downloads\WTSP IMG\auto-ecole-main"

# Create data folder
mkdir data

# Initialize database
python src/init_db.py
```

---

## After Setup

Once the database is created, launch the app:

```bash
python src/main_gui.py
```

### Login Credentials

**Administrator**:
- Username: `admin`
- Password: `Admin123!`

**Cashier**:
- Username: `caissier`
- Password: `Caisse123!`

**Receptionist**:
- Username: `receptionniste`
- Password: `Reception123!`

**Instructor**:
- Username: `moniteur`
- Password: `Moniteur123!`

---

## What Gets Created

### Database File
```
data/autoecole.db
```

### Test Data
- 👤 **4 Users** (admin, caissier, receptionniste, moniteur)
- 👥 **5 Students** with various statuses
- 👨‍🏫 **3 Instructors** (Ahmed, Fatima, Mohammed)
- 🚗 **3 Vehicles** (Dacia Logan, Renault Clio, Peugeot 208)
- 📝 **5 Exams** (theoretical and practical)
- 💰 **Payments** data
- 📅 **Sessions** data

---

## Troubleshooting

### Error: "No module named 'src'"

Make sure you're in the correct folder:
```bash
cd "C:\Users\DELL\Downloads\WTSP IMG\auto-ecole-main"
```

Then run:
```bash
python setup_database.py
```

### Error: "Permission denied"

Run Command Prompt as Administrator:
1. Press `Win + X`
2. Select "Command Prompt (Admin)" or "Windows PowerShell (Admin)"
3. Navigate to folder and run setup

### Database Already Exists

If you want to reset the database:

```bash
# Delete old database
del data\autoecole.db

# Create fresh one
python setup_database.py
```

---

## Verification

To verify the database was created:

### Check the File Exists
```bash
dir data\autoecole.db
```

**Should show**:
```
 Volume in drive C is ...
 Directory of C:\Users\DELL\Downloads\WTSP IMG\auto-ecole-main\data

[date/time]         [size] autoecole.db
               1 File(s)  [size] bytes
```

### Test Login

1. Run: `python src/main_gui.py`
2. Login with: `admin` / `Admin123!`
3. Should see the dashboard with 4 charts

---

## Quick Start (Complete Process)

```bash
# 1. Navigate to project
cd "C:\Users\DELL\Downloads\WTSP IMG\auto-ecole-main"

# 2. Setup database
python setup_database.py

# 3. Launch app
python src/main_gui.py

# 4. Login
#    Username: admin
#    Password: Admin123!
```

---

## What If Setup Fails?

### Check Python Version
```bash
python --version
```

Should be Python 3.10 or higher.

### Check Dependencies
```bash
pip install -r requirements.txt
```

### Check You're in the Right Folder
```bash
dir src\main_gui.py
```

Should show the file exists.

---

## Database Location

The database will be created at:
```
C:\Users\DELL\Downloads\WTSP IMG\auto-ecole-main\data\autoecole.db
```

This is an SQLite database file. You can:
- Back it up by copying the file
- Reset it by deleting and running setup again
- Open it with SQLite tools for inspection

---

## Summary

**The Issue**: Database file doesn't exist yet  
**The Fix**: Run `python setup_database.py`  
**The Result**: Database created with test data  
**Then**: Launch app with `python src/main_gui.py`

---

**Last Updated**: December 8, 2025  
**Status**: Database initialization required before first use
