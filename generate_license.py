#!/usr/bin/env python3
"""
Script pour générer une clé de licence pour l'Auto-École Manager
Usage: python generate_license.py [company_name] [duration_days]
"""

import sys
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent))

from src.utils.license_manager import get_license_manager

def main():
    """Générer une licence"""
    print("=" * 70)
    print("🔑 Générateur de Licence - Auto-École Manager")
    print("=" * 70)
    print()
    
    # Obtenir le gestionnaire de licence
    license_manager = get_license_manager()
    
    # Afficher le Hardware ID
    hardware_id = license_manager.get_hardware_id()
    print(f"📟 Hardware ID de cet ordinateur:")
    print(f"   {hardware_id}")
    print()
    
    # Obtenir les paramètres
    if len(sys.argv) >= 2:
        company_name = sys.argv[1]
    else:
        company_name = input("🏢 Nom de l'Auto-École (défaut: Auto-École Test): ").strip() or "Auto-École Test"
    
    if len(sys.argv) >= 3:
        try:
            duration_days = int(sys.argv[2])
        except ValueError:
            print("⚠️  Durée invalide, utilisation de 365 jours")
            duration_days = 365
    else:
        duration_input = input("📅 Durée de validité en jours (défaut: 365): ").strip()
        duration_days = int(duration_input) if duration_input else 365
    
    print()
    print("🔧 Génération de la licence...")
    print(f"   Entreprise: {company_name}")
    print(f"   Durée: {duration_days} jours")
    print(f"   Hardware ID: {hardware_id}")
    print()
    
    # Générer la clé
    try:
        license_key = license_manager.generate_license_key(
            company_name=company_name,
            duration_days=duration_days,
            hardware_id=hardware_id
        )
        
        print("✅ Licence générée avec succès!")
        print()
        print("=" * 70)
        print("🔑 CLÉ DE LICENCE")
        print("=" * 70)
        print()
        print(f"   {license_key}")
        print()
        print("=" * 70)
        print()
        
        # Option pour activer directement
        activate = input("💡 Voulez-vous activer cette licence maintenant ? (o/N): ").strip().lower()
        
        if activate in ['o', 'oui', 'y', 'yes']:
            success, message = license_manager.activate_license(license_key)
            print()
            if success:
                print(f"✅ {message}")
                
                # Afficher les infos de la licence
                license_info = license_manager.get_license_info()
                print()
                print("📋 Informations de la licence:")
                print(f"   Entreprise: {license_info.get('company')}")
                print(f"   Expiration: {license_info.get('expiration_date')}")
                print(f"   Jours restants: {license_info.get('days_remaining')}")
                print(f"   Actif: {'✅ OUI' if license_info.get('is_active') else '❌ NON'}")
            else:
                print(f"❌ {message}")
        
        print()
        print("=" * 70)
        print("📝 Notes:")
        print("   • Conservez cette clé en lieu sûr")
        print("   • La clé est liée à cet ordinateur uniquement")
        print("   • Pour utiliser sur un autre PC, générez une nouvelle clé")
        print("=" * 70)
        
    except Exception as e:
        print(f"❌ Erreur lors de la génération: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
