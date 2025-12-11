#!/usr/bin/env python3
"""
Script de génération de licences pour Auto-École
À utiliser par le vendeur/support uniquement
"""

import sys
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.license_manager import LicenseManager


def main():
    """Génère une clé de licence"""
    print("=" * 60)
    print("🔐 GÉNÉRATEUR DE LICENCES - AUTO-ÉCOLE")
    print("=" * 60)
    print()
    
    license_manager = LicenseManager()
    
    # Demander les informations
    print("📋 Informations requises:")
    print()
    
    company_name = input("Nom de l'auto-école: ").strip()
    if not company_name:
        print("❌ Le nom est obligatoire!")
        return
    
    hardware_id = input("Hardware ID du client (fourni par le client): ").strip().upper()
    if not hardware_id:
        print("❌ Le Hardware ID est obligatoire!")
        return
    
    try:
        duration_str = input("Durée de validité en jours [365]: ").strip()
        duration_days = int(duration_str) if duration_str else 365
    except ValueError:
        print("❌ Durée invalide, utilisation de 365 jours par défaut")
        duration_days = 365
    
    print()
    print("⏳ Génération de la licence en cours...")
    print()
    
    # Générer la licence
    license_key = license_manager.generate_license_key(
        company_name=company_name,
        duration_days=duration_days,
        hardware_id=hardware_id
    )
    
    print("=" * 60)
    print("✅ LICENCE GÉNÉRÉE AVEC SUCCÈS!")
    print("=" * 60)
    print()
    print(f"📌 Auto-École      : {company_name}")
    print(f"🖥️  Hardware ID    : {hardware_id}")
    print(f"📅 Validité        : {duration_days} jours")
    print()
    print("🔑 CLÉ DE LICENCE :")
    print("-" * 60)
    print(license_key)
    print("-" * 60)
    print()
    print("⚠️  IMPORTANT:")
    print("   - Cette clé est UNIQUE et liée à cet ordinateur")
    print("   - Elle ne fonctionnera pas sur un autre ordinateur")
    print("   - Conservez une copie pour vos archives")
    print()
    print("📧 Envoyez cette clé au client par email sécurisé")
    print()


if __name__ == "__main__":
    main()
