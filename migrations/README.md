# 🗄️ Migrations de Base de Données

Ce dossier contient les scripts de migration pour harmoniser la base de données.

## 📋 Liste des Migrations

| ID | Nom | Priorité | Status | Description |
|----|-----|----------|--------|-------------|
| 001 | base_audit | 🔴 CRITIQUE | ✅ Prête | Ajout champs d'audit (created_by, updated_by, soft delete) |
| 002 | harmonize_types | 🔴 CRITIQUE | 📝 À venir | Harmonisation des types (Boolean, Time) |
| 003 | student_critical_fields | 🔴 CRITIQUE | 📝 À venir | Champs médicaux et légaux (Student) |
| 004 | relations_missing | 🟠 HAUTE | 📝 À venir | Relations manquantes (Payment→Session/Exam, etc.) |
| 005 | financial_details | 🟠 HAUTE | 📝 À venir | Champs financiers détaillés |
| 006 | audit_log_table | 🔴 CRITIQUE | 📝 À venir | Création table audit_logs |
| 007 | status_history_table | 🟠 HAUTE | 📝 À venir | Création table status_history |
| 008 | vehicle_maintenance_table | 🟠 HAUTE | 📝 À venir | Création table vehicle_maintenance |

## 🚀 Comment Utiliser

### 1. Vérifier le Statut

```bash
cd /home/user/webapp/migrations
python migration_001_base_audit.py status
```

### 2. Créer un Backup

```bash
# Automatique lors de la migration
# Ou manuel:
cp data/autoecole.db backups/backup_manual_$(date +%Y%m%d_%H%M%S).db
```

### 3. Appliquer une Migration

```bash
python migration_001_base_audit.py upgrade
```

### 4. Rollback (si nécessaire)

```bash
python migration_001_base_audit.py downgrade
```

## ⚠️ Avertissements

### Avant Toute Migration

1. **TOUJOURS faire un backup** (automatique dans le script)
2. **Tester en environnement de développement d'abord**
3. **Fermer l'application** pendant la migration
4. **Informer les utilisateurs** du downtime

### SQLite Limitations

- SQLite ne supporte pas `ALTER TABLE ... DROP COLUMN`
- Les rollbacks nécessitent de restaurer un backup
- Les modifications de type nécessitent une recréation de table

## 📊 Migration 001 : Base Audit

### Objectif

Ajouter des champs de traçabilité à toutes les tables applicatives.

### Changements

**Colonnes ajoutées à toutes les tables** :
- `created_by_id` (INTEGER) - ID de l'utilisateur créateur
- `updated_by_id` (INTEGER) - ID du dernier utilisateur modif icateur
- `deleted_at` (TEXT/DateTime) - Date de suppression (soft delete)
- `is_deleted` (INTEGER/Boolean) - Flag de suppression

### Tables Affectées

- ✅ `students`
- ✅ `instructors`
- ✅ `vehicles`
- ✅ `sessions`
- ✅ `payments`
- ✅ `exams`

### Impact

- **Taille DB** : +4 colonnes par table = ~24 colonnes
- **Performance** : Impact minimal (colonnes indexées si nécessaire)
- **Code** : Controllers à mettre à jour pour utiliser soft delete

### Utilisation Après Migration

#### Soft Delete

```python
# Au lieu de:
db.session.delete(student)

# Faire:
student.is_deleted = True
student.deleted_at = datetime.now()
student.updated_by_id = current_user.id
db.session.commit()
```

#### Requêtes Filtrées

```python
# Exclure les éléments supprimés
students = Student.query.filter_by(is_deleted=False).all()

# Ou inclure tout
students = Student.query.all()

# Voir seulement les supprimés
deleted_students = Student.query.filter_by(is_deleted=True).all()
```

#### Traçabilité

```python
# À la création
new_student = Student(...)
new_student.created_by_id = current_user.id
db.session.add(new_student)

# À la modification
student.updated_by_id = current_user.id
student.updated_at = datetime.now()
db.session.commit()
```

## 🔧 Développement de Nouvelles Migrations

### Template

```python
"""
Migration XXX: [Titre]
Date: YYYY-MM-DD
Priorité: [CRITIQUE/HAUTE/MOYENNE]

Description:
    [Description détaillée]
"""

def upgrade(db_path='data/autoecole.db'):
    # Backup
    backup_database(db_path)
    
    # Connexion
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    
    try:
        # Changements ici
        cursor.execute("ALTER TABLE ...")
        
        conn.commit()
        print("✓ Migration appliquée")
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"✗ Erreur: {e}")
        return False
        
    finally:
        conn.close()

def downgrade(db_path='data/autoecole.db'):
    # Rollback
    pass

def check_migration_status(db_path='data/autoecole.db'):
    # Vérification
    pass
```

## 📞 Support

### Problèmes Courants

**Migration échoue** :
1. Vérifier que la base n'est pas utilisée
2. Vérifier les permissions
3. Regarder les logs d'erreur
4. Restaurer le backup si nécessaire

**Rollback échoue** :
1. Restaurer manuellement depuis le backup
2. Commande : `cp backups/backup_XXX.db data/autoecole.db`

**Performances dégradées** :
1. Reconstruire les index : `REINDEX`
2. Analyser la base : `ANALYZE`
3. Vacuum : `VACUUM`

## 📚 Documentation Complète

Voir `docs/HARMONISATION_BASE_DE_DONNEES.md` pour :
- Audit complet des modèles
- Liste exhaustive des harmonisations
- Plan de migration détaillé (12 semaines)
- Impacts et risques
- Recommandations

## ✅ Checklist Pré-Migration

Avant d'appliquer une migration en production :

- [ ] Backup manuel créé
- [ ] Migration testée en développement
- [ ] Utilisateurs informés du downtime
- [ ] Application fermée
- [ ] Script de rollback testé
- [ ] Monitoring post-migration prévu

## 🎯 Roadmap

### Court Terme (Mois 1-2)
- [x] Migration 001 : Base Audit
- [ ] Migration 002 : Harmonisation Types
- [ ] Migration 003 : Student Critical Fields

### Moyen Terme (Mois 3-4)
- [ ] Migration 004-005 : Relations et Champs Financiers
- [ ] Migration 006-008 : Nouvelles Tables

### Long Terme (Mois 5-6)
- [ ] Optimisations
- [ ] Index avancés
- [ ] Partitionnement (si nécessaire)

---

**Dernière mise à jour** : 08/12/2024  
**Version** : 1.0.0
