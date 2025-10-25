import os
import shutil

print("🔧 Correction des noms de dossiers...")

# Vérifier si 'emplates' existe et le renommer
if os.path.exists('emplates') and not os.path.exists('templates'):
    os.rename('emplates', 'templates')
    print("✅ Dossier 'emplates' renommé en 'templates'")

# Vérifier si 'templates' existe
if os.path.exists('templates'):
    print("✅ Dossier templates trouvé")
    print(f"📁 Contenu templates: {os.listdir('templates')}")
else:
    print("❌ Dossier templates manquant")

print("🔧 Correction terminée")