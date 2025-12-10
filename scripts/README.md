# Scripts utilitaires

Ce répertoire contient des scripts d'aide à la maintenance et aux migrations.

## Scripts disponibles

### Migration et setup
- `setup_database.py` - Configuration initiale de la base de données
- `migrate_balance_logic.py` - Migration logique des soldes
- `migrate_payments_phase1.py` - Migration paiements phase 1

### Améliorations et vérifications
- `apply_students_improvements.py` - Appliquer améliorations module élèves
- `check_imports.py` - Vérifier les imports du projet
- `start_safe.py` - Démarrage sécurisé de l'application

## Utilisation

```bash
# Exécuter un script
cd /path/to/webapp
python scripts/setup_database.py
```

## Notes

Ces scripts ne sont pas nécessaires au fonctionnement quotidien de l'application.
Ils servent uniquement pour la maintenance technique.
