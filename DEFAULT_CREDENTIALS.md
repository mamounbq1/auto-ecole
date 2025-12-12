# 🔑 Default Login Credentials

## Admin Account

After running the database initialization (`src/init_db.py`), the following default accounts are created:

### Primary Admin Account
- **Username:** `admin`
- **Password:** `Admin123!`
- **Email:** admin@autoecole.ma
- **Role:** Administrator (full access)

---

## Other Default Accounts

### Cashier Account
- **Username:** `caissier`
- **Password:** `Caisse123!`
- **Role:** Cashier

### Instructor Account
- **Username:** `moniteur1`
- **Password:** `Moniteur123!`
- **Role:** Instructor

### Receptionist Account
- **Username:** `receptionniste`
- **Password:** `Reception123!`
- **Role:** Receptionist

---

## RBAC System (New Multi-Role System)

If you've initialized the RBAC system using `test_rbac.py`, the admin account credentials are:

- **Username:** `admin`
- **Password:** `admin123` (lowercase, no special characters)
- **Roles:** Administrateur (all permissions)

---

## Account Locked?

If your account gets locked after too many failed login attempts, you can unlock it by running:

```bash
python check_and_unlock_admin.py
```

This script will:
- Show the current admin account status
- Automatically unlock the account if it's locked
- Reset failed login attempts to 0
- Display the password if available

---

## Important Security Notes

⚠️ **Change default passwords immediately in production!**

1. Login with the default credentials
2. Go to `Paramètres` → `👥 Gestion des Utilisateurs`
3. Change all default passwords
4. Create new users with secure passwords
5. Disable or delete unused default accounts

---

## Troubleshooting

### "Mot de passe incorrect" error

If you're getting password incorrect errors:

1. Check if you're using the correct password format:
   - Old system: `Admin123!` (capital A, exclamation mark)
   - New RBAC system: `admin123` (lowercase, no special characters)

2. Check the database to see which users exist:
   ```bash
   python check_and_unlock_admin.py
   ```

3. The account will lock after 5 failed attempts. Use the unlock script if needed.

### "Compte verrouillé" error

Run the unlock script:
```bash
python check_and_unlock_admin.py
```

### Need to reset password

In the application:
1. Login as admin
2. Go to `Paramètres` → `👥 Gestion des Utilisateurs`
3. Select the user
4. Click `🔑 Mot de passe`
5. Enter new password

---

## Password Requirements

- Minimum 6 characters (recommended: 8+)
- Can include letters, numbers, and special characters
- Passwords are hashed using bcrypt
- Admin can view and change any user's password
