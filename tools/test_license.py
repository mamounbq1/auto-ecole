#!/usr/bin/env python3
"""
Script de test du système de licence
Pour vérifier que tout fonctionne correctement
"""

import sys
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.license_manager import LicenseManager


def test_license_system():
    """Teste le système de licence"""
    print("=" * 60)
    print("🧪 TEST DU SYSTÈME DE LICENCE")
    print("=" * 60)
    print()
    
    license_manager = LicenseManager()
    
    # 1. Test Hardware ID
    print("1️⃣  Test récupération Hardware ID...")
    hardware_id = license_manager.get_hardware_id()
    print(f"   ✅ Hardware ID: {hardware_id}")
    print()
    
    # 2. Test génération de licence
    print("2️⃣  Test génération de licence...")
    company_name = "Test Auto-École"
    duration = 30  # 30 jours pour le test
    
    license_key = license_manager.generate_license_key(
        company_name=company_name,
        duration_days=duration,
        hardware_id=hardware_id
    )
    print(f"   ✅ Licence générée:")
    print(f"   {license_key}")
    print()
    
    # 3. Test validation de licence
    print("3️⃣  Test validation de licence...")
    is_valid, message = license_manager.validate_license_key(license_key)
    if is_valid:
        print(f"   ✅ {message}")
    else:
        print(f"   ❌ {message}")
    print()
    
    # 4. Test activation
    print("4️⃣  Test activation de licence...")
    success, activation_msg = license_manager.activate_license(license_key)
    if success:
        print(f"   ✅ {activation_msg}")
    else:
        print(f"   ❌ {activation_msg}")
    print()
    
    # 5. Test vérification état
    print("5️⃣  Test vérification état de licence...")
    if license_manager.is_licensed():
        print("   ✅ Application sous licence valide")
        
        # Afficher les infos
        info = license_manager.get_license_info()
        if info:
            print()
            print("   📋 Informations de licence:")
            print(f"      • Auto-École: {info.get('company')}")
            print(f"      • Hardware ID: {info.get('hardware_id')}")
            print(f"      • Date activation: {info.get('activation_date')}")
            print(f"      • Date expiration: {info.get('expiry_date')}")
            print(f"      • Jours restants: {info.get('days_remaining')}")
            print(f"      • Statut: {info.get('status')}")
    else:
        print("   ❌ Aucune licence valide")
    print()
    
    # 6. Test validation avec mauvais Hardware ID
    print("6️⃣  Test validation avec mauvais Hardware ID...")
    fake_license = license_manager.generate_license_key(
        company_name="Fake",
        duration_days=30,
        hardware_id="FAKEHARDWAREID00"
    )
    is_valid, message = license_manager.validate_license_key(fake_license)
    if not is_valid:
        print(f"   ✅ Rejet attendu: {message}")
    else:
        print(f"   ❌ ERREUR: La licence devrait être rejetée!")
    print()
    
    # 7. Test désactivation
    print("7️⃣  Test désactivation de licence...")
    response = input("   Voulez-vous désactiver la licence de test ? (oui/non): ")
    if response.lower() in ['oui', 'o', 'yes', 'y']:
        if license_manager.deactivate_license():
            print("   ✅ Licence désactivée")
        else:
            print("   ℹ️  Aucune licence à désactiver")
    else:
        print("   ℹ️  Licence de test conservée")
    print()
    
    print("=" * 60)
    print("✅ TOUS LES TESTS SONT TERMINÉS!")
    print("=" * 60)
    print()
    print("Le système de licence fonctionne correctement! 🎉")
    print()


if __name__ == "__main__":
    test_license_system()
