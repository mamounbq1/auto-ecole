# Tests du projet Auto-École

Ce répertoire contient tous les tests unitaires et d'intégration.

## Fichiers de test

- `test_app.py` - Tests de l'application complète
- `test_backend.py` - Tests du backend
- `test_dashboard.py` - Tests du dashboard
- `test_documents_integration.py` - Tests d'intégration documents
- `test_gui.py` - Tests de l'interface graphique
- `test_new_modules.py` - Tests des nouveaux modules
- `test_payments.py` - Tests module paiements
- `test_payments_complete.py` - Tests paiements complets
- `test_phase1_features.py` - Tests fonctionnalités phase 1
- `test_students_module.py` - Tests module élèves
- `test_students_widget.py` - Tests widget élèves
- `verifier_tout.py` - Script de vérification globale

## Exécution des tests

```bash
# Tous les tests
cd tests/
python -m pytest

# Test spécifique
python test_app.py
```
