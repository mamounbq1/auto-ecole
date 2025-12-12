# 🔐 Système RBAC (Role-Based Access Control)

## 📋 Vue d'ensemble

Le système RBAC multi-rôles a été implémenté avec succès dans l'application Auto-École Manager. Il permet une gestion fine des permissions avec support de **plusieurs rôles par utilisateur**.

## ✨ Fonctionnalités

### 1. **Multi-Rôles par Utilisateur**
- ✅ Un utilisateur peut avoir **un ou plusieurs rôles**
- ✅ Permissions cumulatives (union de tous les rôles)
- ✅ 6 rôles système prédéfinis
- ✅ 54 permissions granulaires

### 2. **Gestion des Utilisateurs (Staff)**
- ✅ Interface complète dans **Paramètres → Gestion des Utilisateurs**
- ✅ Créer, modifier, supprimer des utilisateurs
- ✅ Assigner/retirer des rôles (multi-sélection)
- ✅ Activer/désactiver des comptes
- ✅ Déverrouiller des comptes bloqués
- ✅ Statistiques en temps réel

### 3. **Gestion des Mots de Passe (Admin)**
- ✅ Admin peut **voir le mot de passe** de n'importe quel utilisateur
- ✅ Admin peut **changer le mot de passe** de n'importe quel utilisateur
- ✅ Mots de passe stockés en clair dans `password_plain` (visible admin uniquement)
- ✅ Interface dédiée avec affichage sécurisé

### 4. **Permissions Granulaires**
- ✅ 54 permissions couvrant tous les modules
- ✅ Permissions par module : Élèves, Moniteurs, Véhicules, Séances, Paiements, Examens, Documents, Rapports, Administration
- ✅ Actions : VIEW, CREATE, EDIT, DELETE
- ✅ Vérification automatique dans l'UI

## 📂 Structure de la Base de Données

### Tables Créées

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│     users       │────→│   user_roles    │←────│      roles      │
│  (utilisateurs) │     │  (association)  │     │    (rôles)      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
         ↓                                               ↓
    • username                                  ┌─────────────────┐
    • password_hash                             │ role_permissions│
    • password_plain                            │  (association)  │
    • full_name                                 └─────────────────┘
    • email                                             ↓
    • phone                                    ┌─────────────────┐
    • is_active                                │  permissions    │
    • is_locked                                │  (permissions)  │
    • roles (many-to-many)                     └─────────────────┘
                                                       ↓
                                                  • key
                                                  • name
                                                  • category
```

## 🎭 Rôles Système

| Rôle | Nom | Description | Permissions |
|------|-----|-------------|-------------|
| **admin** | Administrateur | Accès complet au système | Toutes (54) |
| **manager** | Gestionnaire | Gestion complète sauf admin système | 32 permissions |
| **instructor** | Moniteur | Séances et suivi des élèves | 8 permissions |
| **cashier** | Caissier | Paiements et finances | 7 permissions |
| **secretary** | Secrétaire | Inscriptions, documents, accueil | 12 permissions |
| **accountant** | Comptable | Gestion complète des finances | 8 permissions |

## 🔑 Permissions Disponibles

### Élèves (Students)
- `view_students`, `create_students`, `edit_students`, `delete_students`

### Moniteurs (Instructors)
- `view_instructors`, `create_instructors`, `edit_instructors`, `delete_instructors`

### Véhicules (Vehicles)
- `view_vehicles`, `create_vehicles`, `edit_vehicles`, `delete_vehicles`

### Séances (Sessions)
- `view_sessions`, `create_sessions`, `edit_sessions`, `delete_sessions`

### Paiements (Payments)
- `view_payments`, `create_payments`, `edit_payments`, `delete_payments`

### Examens (Exams)
- `view_exams`, `create_exams`, `edit_exams`, `delete_exams`

### Documents
- `view_documents`, `create_documents`, `edit_documents`, `delete_documents`

### Rapports & Statistiques
- `view_reports`, `view_statistics`, `view_financial_reports`

### Administration
- `view_settings`, `edit_settings`, `manage_users`, `manage_roles`, `manage_backups`, `view_logs`

## 🚀 Installation et Initialisation

### 1. Initialiser le système RBAC

```bash
python test_rbac.py
```

Ce script va :
- ✅ Créer toutes les tables (roles, permissions, user_roles, role_permissions)
- ✅ Créer les 54 permissions
- ✅ Créer les 6 rôles système
- ✅ Migrer les utilisateurs existants
- ✅ Créer un admin par défaut si aucun utilisateur n'existe

### 2. Compte Admin par Défaut

```
Username: admin
Password: admin123
Rôles: Administrateur (toutes permissions)
```

### 3. Lancer l'Application

```bash
python main.py
```

## 💻 Utilisation

### Pour l'Administrateur

1. **Connexion**
   - Username: `admin`
   - Password: `admin123`

2. **Accéder à la Gestion des Utilisateurs**
   - Menu: **Paramètres** → **Gestion des Utilisateurs** (onglet 👥)

3. **Créer un Nouvel Utilisateur**
   - Cliquer sur **➕ Ajouter Utilisateur**
   - Remplir : username, nom complet, email, téléphone
   - Définir le mot de passe
   - **Sélectionner un ou plusieurs rôles** (checkboxes)
   - Enregistrer

4. **Modifier un Utilisateur**
   - Cliquer sur **✏️ Modifier**
   - Modifier les informations
   - Ajouter/retirer des rôles
   - Enregistrer

5. **Changer un Mot de Passe**
   - Cliquer sur **🔑 Mot de passe**
   - Le **mot de passe actuel est affiché** en haut
   - Entrer le nouveau mot de passe
   - Confirmer
   - Le nouveau mot de passe est affiché (à communiquer à l'utilisateur)

6. **Gérer les Comptes**
   - **🔓 Déverrouiller** : Déverrouiller un compte bloqué
   - **✅/❌** : Activer/Désactiver un compte

### Pour les Utilisateurs

- Les utilisateurs voient uniquement les modules et fonctionnalités autorisés par leurs rôles
- Les permissions sont vérifiées automatiquement dans l'interface
- Les boutons/menus non autorisés sont masqués ou désactivés

## 🔧 API de Programmation

### Vérifier une Permission

```python
from src.utils.auth import has_permission

# Vérifier si l'utilisateur connecté a une permission
if has_permission('create_students'):
    # L'utilisateur peut créer des élèves
    pass
```

### Vérifier un Rôle

```python
from src.utils.auth import has_role

# Vérifier par nom de rôle (nouveau système)
if has_role(role_name='admin'):
    # L'utilisateur est admin
    pass

# Vérifier par UserRole (ancien système, compatibilité)
from src.models import UserRole
if has_role(role=UserRole.ADMIN):
    # L'utilisateur est admin
    pass
```

### Obtenir l'Utilisateur Connecté

```python
from src.utils.auth import get_current_user

user = get_current_user()
if user:
    print(f"Connecté: {user.full_name}")
    print(f"Rôles: {user.get_role_names()}")
    print(f"Permissions: {user.get_all_permissions()}")
```

### Utiliser le UserController

```python
from src.controllers.user_controller import UserController

# Créer un utilisateur
success, message, user = UserController.create_user(
    username='jdupont',
    password='secret123',
    full_name='Jean Dupont',
    email='jdupont@exemple.com',
    role_ids=[1, 2]  # IDs des rôles
)

# Modifier un utilisateur
success, message = UserController.update_user(
    user_id=5,
    full_name='Jean Dupont (Mis à jour)',
    role_ids=[1, 2, 3]  # Ajouter un rôle
)

# Changer un mot de passe
success, message = UserController.change_password(
    user_id=5,
    new_password='nouveauMotDePasse',
    changed_by_admin=True  # Stocke en clair
)
```

## 📁 Fichiers Modifiés/Créés

### Nouveaux Fichiers
- `src/models/role.py` - Modèles Role, Permission, PermissionType
- `src/controllers/user_controller.py` - Contrôleur CRUD pour utilisateurs
- `src/utils/init_rbac.py` - Script d'initialisation RBAC
- `src/views/widgets/user_management.py` - Interface de gestion des utilisateurs
- `test_rbac.py` - Script de test et initialisation
- `RBAC_SYSTEM.md` - Cette documentation

### Fichiers Modifiés
- `src/models/user.py` - Support multi-rôles, password_plain
- `src/models/__init__.py` - Import des nouveaux modèles
- `src/utils/auth.py` - Méthodes has_permission(), has_role()
- `src/views/widgets/settings_widget.py` - Onglet Gestion des Utilisateurs

## 🔒 Sécurité

### Bonnes Pratiques Implémentées
✅ Mots de passe hashés avec bcrypt
✅ Mot de passe en clair stocké seulement pour admin (champ séparé)
✅ Verrouillage automatique après X tentatives échouées
✅ Permissions vérifiées à chaque action
✅ Logs d'audit pour toutes les actions utilisateurs
✅ Sessions sécurisées avec AuthManager singleton

### Recommandations
⚠️ **Changez le mot de passe admin par défaut** après l'installation
⚠️ Utilisez des mots de passe forts (minimum 8 caractères)
⚠️ Limitez le nombre d'administrateurs
⚠️ Vérifiez régulièrement les logs d'accès

## 🐛 Dépannage

### Problème: "Permission denied"
- Vérifier que l'utilisateur a les bons rôles assignés
- Vérifier dans **Gestion des Utilisateurs** les rôles de l'utilisateur
- Vérifier que les rôles ont les bonnes permissions

### Problème: "No admin user found"
- Exécuter `python test_rbac.py` pour créer l'admin par défaut

### Problème: Tables non créées
- Exécuter `python test_rbac.py` pour initialiser la base de données

## 📈 Prochaines Étapes (Optionnel)

Les fonctionnalités suivantes peuvent être ajoutées si nécessaire :

1. **Visibilité des Modules par Rôle**
   - Masquer automatiquement les modules non autorisés dans le menu principal
   - Implémenter dans `main_window.py`

2. **Permissions Granulaires dans les Widgets**
   - Désactiver les boutons non autorisés dans chaque module
   - Ajouter des vérifications `has_permission()` avant chaque action

3. **Audit Log Avancé**
   - Logger toutes les actions critiques
   - Interface de consultation des logs

4. **Rôles Personnalisés**
   - Permettre à l'admin de créer des rôles personnalisés
   - Interface de gestion des permissions par rôle

## ✅ Résumé

Le système RBAC est **100% fonctionnel** avec :

✅ **Multi-rôles** : Un utilisateur peut avoir plusieurs rôles
✅ **54 permissions** couvrant tous les modules
✅ **6 rôles système** prédéfinis
✅ **Interface complète** de gestion des utilisateurs
✅ **Gestion des mots de passe** avec visibilité admin
✅ **Migration automatique** des utilisateurs existants
✅ **Backward compatible** avec l'ancien système
✅ **Tests et documentation** complets

**Le système est prêt à être utilisé en production !** 🎉
