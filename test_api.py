"""
Script de test pour l'API Market Study
Exécuter avec: python test_api.py
"""

import requests
import json
from datetime import datetime

BASE_URL = 'http://localhost:5000'

def print_header(title):
    """Affiche un en-tête formaté"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def test_health():
    """Test du health check"""
    print_header("TEST 1: Health Check")
    
    try:
        response = requests.get(f'{BASE_URL}/health')
        
        if response.status_code == 200:
            print("✅ Service opérationnel")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"❌ Erreur {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Impossible de se connecter à l'API")
        print("   Assurez-vous que le serveur Flask est démarré (python app.py)")

def test_simple_analysis():
    """Test d'analyse simple avec 2 produits"""
    print_header("TEST 2: Analyse Simple (2 produits)")
    
    data = {
        "products": ["iPhone 15 Pro", "Samsung Galaxy S24 Ultra", "Pixel 8"],
        "sector": "Smartphones Premium"
    }
    
    print(f"\n📤 Envoi de la requête...")
    print(f"Produits: {', '.join(data['products'])}")
    print(f"Secteur: {data['sector']}")
    
    try:
        response = requests.post(
            f'{BASE_URL}/api/analyze',
            json=data,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            print("\n✅ Analyse réussie!")
            print(f"\n📄 PDF généré: {result['pdf_filename']}")
            print(f"🔗 URL téléchargement: {BASE_URL}{result['pdf_url']}")
            
            print("\n📊 Résultats:")
            for product in result['analysis']['products']:
                print(f"\n  • {product['name']}")
                print(f"    Part de marché: {product['market_share']:.1f}%")
                print(f"    Prix: {product['price']:.0f}€")
                print(f"    Satisfaction: {product['satisfaction']:.1f}/5")
                print(f"    Croissance: {product['growth']:+.1f}%")
            
            print(f"\n📝 Résumé:")
            print(f"   {result['analysis']['summary'][:200]}...")
            
            return result['pdf_filename']
        else:
            print(f"\n❌ Erreur {response.status_code}")
            print(response.json())
            
    except requests.exceptions.Timeout:
        print("\n❌ Timeout - L'analyse prend trop de temps")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
    
    return None

def test_complex_analysis():
    """Test d'analyse complexe avec 5 produits"""
    print_header("TEST 3: Analyse Complexe (5 produits)")
    
    data = {
        "products": [
            "Tesla Model 3",
            "BMW i4",
            "Mercedes EQS",
            "Audi e-tron GT",
            "Polestar 2"
        ],
        "sector": "Véhicules Électriques Premium"
    }
    
    print(f"\n📤 Envoi de la requête...")
    print(f"Produits ({len(data['products'])}): {', '.join(data['products'])}")
    print(f"Secteur: {data['sector']}")
    print("\n⏳ Génération en cours (cela peut prendre 10-20 secondes)...")
    
    try:
        response = requests.post(
            f'{BASE_URL}/api/analyze',
            json=data,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            print("\n✅ Analyse réussie!")
            print(f"\n📄 PDF généré: {result['pdf_filename']}")
            
            return result['pdf_filename']
        else:
            print(f"\n❌ Erreur {response.status_code}")
            print(response.json())
            
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
    
    return None

def test_download(filename):
    """Test du téléchargement d'un PDF"""
    if not filename:
        print("\n⚠️  Pas de fichier à télécharger")
        return
    
    print_header("TEST 4: Téléchargement PDF")
    
    print(f"\n📥 Téléchargement de: {filename}")
    
    try:
        response = requests.get(f'{BASE_URL}/api/download/{filename}')
        
        if response.status_code == 200:
            # Sauvegarder le PDF
            output_path = f'downloaded_{filename}'
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            print(f"✅ PDF téléchargé avec succès!")
            print(f"📁 Sauvegardé dans: {output_path}")
            print(f"📊 Taille: {len(response.content) / 1024:.1f} KB")
        else:
            print(f"❌ Erreur {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")

def test_list_reports():
    """Test de la liste des rapports"""
    print_header("TEST 5: Liste des Rapports")
    
    try:
        response = requests.get(f'{BASE_URL}/api/reports')
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n📚 Total de rapports: {data['total']}")
            
            if data['reports']:
                print("\nRapports disponibles:")
                for i, report in enumerate(data['reports'][:5], 1):
                    print(f"\n  {i}. {report['filename']}")
                    print(f"     Créé: {report['created']}")
                    print(f"     Taille: {report['size'] / 1024:.1f} KB")
                
                if data['total'] > 5:
                    print(f"\n  ... et {data['total'] - 5} autre(s)")
            else:
                print("\n  Aucun rapport disponible")
        else:
            print(f"❌ Erreur {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")

def test_validation():
    """Test de la validation des entrées"""
    print_header("TEST 6: Validation des Entrées")
    
    tests = [
        {
            "name": "Produits manquants",
            "data": {"sector": "Test"},
            "should_fail": True
        },
        {
            "name": "Un seul produit",
            "data": {"products": ["Produit A"], "sector": "Test"},
            "should_fail": True
        },
        {
            "name": "Secteur manquant",
            "data": {"products": ["A", "B"]},
            "should_fail": True
        },
        {
            "name": "Données valides",
            "data": {"products": ["A", "B"], "sector": "Test"},
            "should_fail": False
        }
    ]
    
    for test in tests:
        print(f"\n  Test: {test['name']}")
        
        try:
            response = requests.post(
                f'{BASE_URL}/api/analyze',
                json=test['data'],
                timeout=30
            )
            
            if test['should_fail']:
                if response.status_code != 200:
                    print(f"    ✅ Échec attendu - {response.json().get('error', 'Erreur')}")
                else:
                    print(f"    ❌ Aurait dû échouer!")
            else:
                if response.status_code == 200:
                    print(f"    ✅ Succès attendu")
                else:
                    print(f"    ❌ Aurait dû réussir!")
                    
        except Exception as e:
            print(f"    ❌ Erreur: {e}")

def main():
    """Fonction principale"""
    print("\n" + "="*60)
    print(" "*15 + "🧪 SUITE DE TESTS API")
    print("="*60)
    print("\n⚠️  Assurez-vous que le serveur Flask est démarré!")
    print("   Commande: python app.py")
    print("\n" + "="*60)
    
    input("\nAppuyez sur Entrée pour commencer les tests...")
    
    # Test 1: Health Check
    test_health()
    
    # Test 2: Analyse simple
    filename1 = test_simple_analysis()
    
    # Test 3: Analyse complexe
    filename2 = test_complex_analysis()
    
    # Test 4: Téléchargement
    test_download(filename1 or filename2)
    
    # Test 5: Liste des rapports
    test_list_reports()
    
    # Test 6: Validation
    test_validation()
    
    # Résumé
    print("\n" + "="*60)
    print(" "*20 + "✅ TESTS TERMINÉS")
    print("="*60)
    print("\n💡 Vérifiez le dossier 'reports/' pour voir les PDFs générés")
    print("💡 Les PDFs téléchargés sont préfixés par 'downloaded_'")
    print("\n")

if __name__ == '__main__':
    main()
