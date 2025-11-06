"""
Script de test pour l'intégration Ollama
Teste la connexion, les modèles et la génération d'analyses
"""
import requests
import json
import time
from datetime import datetime


BASE_URL = 'http://localhost:5000'


def print_header(title):
    """Affiche un en-tête formaté"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


def test_health_check():
    """Test du health check avec statut Ollama"""
    print_header("TEST 1: Health Check + Statut Ollama")
    
    try:
        response = requests.get(f'{BASE_URL}/health', timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API opérationnelle")
            print(f"\n📊 Informations:")
            print(f"   Status: {data.get('status')}")
            print(f"   Version: {data.get('version')}")
            print(f"   Service: {data.get('service')}")
            
            ollama_info = data.get('ollama', {})
            print(f"\n🤖 Ollama:")
            print(f"   Disponible: {'✅ OUI' if ollama_info.get('available') else '❌ NON'}")
            print(f"   Modèle défaut: {ollama_info.get('default_model')}")
            
            if not ollama_info.get('available'):
                print("\n⚠️  ATTENTION: Ollama n'est pas accessible!")
                print("   1. Vérifiez qu'Ollama est démarré: ollama serve")
                print("   2. Vérifiez le port: http://localhost:11434")
                
        else:
            print(f"❌ Erreur {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Impossible de se connecter à l'API")
        print("   Assurez-vous que le serveur est démarré: python app_ollama.py")
    except Exception as e:
        print(f"❌ Erreur: {e}")


def test_list_models():
    """Test du listing des modèles Ollama"""
    print_header("TEST 2: Liste des Modèles Ollama")
    
    try:
        response = requests.get(f'{BASE_URL}/ollama/models', timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            models = data.get('models', [])
            
            print(f"✅ {data.get('count')} modèle(s) disponible(s)")
            print(f"\n📋 Liste:")
            for i, model in enumerate(models, 1):
                marker = "⭐" if model == data.get('default') else "  "
                print(f"   {marker} {i}. {model}")
            
            if not models:
                print("⚠️  Aucun modèle trouvé!")
                print("   Téléchargez un modèle: ollama pull gemma3:4b")
                
        elif response.status_code == 503:
            print("❌ Ollama non accessible")
            data = response.json()
            print(f"   {data.get('error')}")
            print(f"   {data.get('details')}")
        else:
            print(f"❌ Erreur {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")


def test_simple_analysis_ollama():
    """Test d'analyse avec Ollama"""
    print_header("TEST 3: Analyse Simple avec Ollama")
    
    data = {
        "products": ["iPhone 15 Pro", "Samsung Galaxy S24 Ultra"],
        "sector": "Smartphones Premium",
        "ollama": {
            "use_ollama": True,
            "model": "gemma3:4b",
            "temperature": 0.7,
            "top_p": 0.9,
            "max_tokens": 2000
        }
    }
    
    print(f"\n📤 Envoi de la requête...")
    print(f"   Produits: {', '.join(data['products'])}")
    print(f"   Secteur: {data['sector']}")
    print(f"   Modèle: {data['ollama']['model']}")
    print(f"   Temperature: {data['ollama']['temperature']}")
    print(f"\n⏳ Génération en cours (peut prendre 1-3 minutes avec LLM)...")
    
    start_time = time.time()
    
    try:
        response = requests.post(
            f'{BASE_URL}/api/analyze',
            json=data,
            timeout=300  # 5 minutes
        )
        
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"\n✅ Analyse réussie en {elapsed:.1f}s!")
            print(f"\n📄 PDF généré: {result['pdf_filename']}")
            print(f"🔗 URL: {BASE_URL}{result['pdf_url']}")
            
            analysis = result.get('analysis', {})
            print(f"\n📊 Résultats:")
            print(f"   Secteur: {analysis.get('sector')}")
            print(f"   Date: {analysis.get('date')}")
            print(f"   Produits analysés: {analysis.get('products_count')}")
            print(f"   Ollama utilisé: {analysis.get('ollama_used')}")
            print(f"   Modèle: {analysis.get('model')}")
            
            print(f"\n💰 Métriques par produit:")
            for product in analysis.get('products', []):
                print(f"\n   • {product['name']}")
                print(f"     Part de marché: {product['market_share']:.1f}%")
                print(f"     Prix: {product['price']:.0f}€")
                print(f"     Satisfaction: {product['satisfaction']:.1f}/5")
                print(f"     Croissance: {product['growth']:+.1f}%")
            
            print(f"\n📝 Résumé exécutif:")
            summary = analysis.get('summary', '')
            print(f"   {summary[:200]}...")
            
            return result['pdf_filename']
            
        else:
            print(f"\n❌ Erreur {response.status_code}")
            error_data = response.json()
            print(f"   {error_data.get('error')}")
            if 'details' in error_data:
                print(f"   Détails: {error_data['details']}")
                
    except requests.exceptions.Timeout:
        print(f"\n❌ Timeout après {elapsed:.1f}s")
        print("   Le LLM prend trop de temps. Solutions:")
        print("   1. Utiliser un modèle plus léger (deepseek-r1:7b)")
        print("   2. Réduire max_tokens")
        print("   3. Augmenter le timeout")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
    
    return None


def test_fallback_mode():
    """Test du mode fallback (sans Ollama)"""
    print_header("TEST 4: Mode Fallback (Simulation)")
    
    data = {
        "products": ["Produit A", "Produit B"],
        "sector": "Test Secteur",
        "ollama": {
            "use_ollama": False  # Forcer fallback
        }
    }
    
    print(f"\n📤 Envoi en mode simulation...")
    print(f"⏳ Génération (rapide, simulation)...")
    
    start_time = time.time()
    
    try:
        response = requests.post(
            f'{BASE_URL}/api/analyze',
            json=data,
            timeout=60
        )
        
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"\n✅ Simulation réussie en {elapsed:.1f}s!")
            print(f"📄 PDF: {result['pdf_filename']}")
            
            analysis = result.get('analysis', {})
            print(f"\n📊 Mode utilisé: {'Simulation' if not analysis.get('ollama_used') else 'Ollama'}")
            
            return result['pdf_filename']
        else:
            print(f"\n❌ Erreur {response.status_code}")
            
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
    
    return None


def test_different_temperatures():
    """Test avec différentes températures"""
    print_header("TEST 5: Comparaison Températures")
    
    temperatures = [0.2, 0.7, 1.5]
    
    print("\n🌡️  Test avec 3 températures différentes:")
    print("   0.2 = Factuel/Déterministe")
    print("   0.7 = Équilibré (défaut)")
    print("   1.5 = Créatif")
    
    for temp in temperatures:
        print(f"\n{'─'*50}")
        print(f"🌡️  Temperature: {temp}")
        
        data = {
            "products": ["Produit Test"],
            "sector": "Test",
            "ollama": {
                "use_ollama": True,
                "model": "gemma3:4b",
                "temperature": temp,
                "max_tokens": 500  # Court pour rapidité
            }
        }
        
        try:
            start = time.time()
            response = requests.post(
                f'{BASE_URL}/api/analyze',
                json=data,
                timeout=180
            )
            elapsed = time.time() - start
            
            if response.status_code == 200:
                print(f"   ✅ Succès en {elapsed:.1f}s")
            else:
                print(f"   ❌ Erreur {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Erreur: {e}")


def test_download(filename):
    """Test du téléchargement"""
    if not filename:
        print("\n⚠️  Pas de fichier à télécharger")
        return
    
    print_header("TEST 6: Téléchargement PDF")
    
    print(f"\n📥 Téléchargement: {filename}")
    
    try:
        response = requests.get(f'{BASE_URL}/api/download/{filename}', timeout=10)
        
        if response.status_code == 200:
            output_path = f'test_download_{filename}'
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            print(f"✅ PDF téléchargé!")
            print(f"📁 Sauvegardé: {output_path}")
            print(f"📊 Taille: {len(response.content) / 1024:.1f} KB")
        else:
            print(f"❌ Erreur {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")


def main():
    """Fonction principale"""
    print("\n" + "="*70)
    print(" "*15 + "🧪 SUITE DE TESTS OLLAMA")
    print("="*70)
    print("\n⚠️  Pré-requis:")
    print("   1. Ollama démarré: ollama serve")
    print("   2. Modèle téléchargé: ollama pull gemma3:4b")
    print("   3. API lancée: python app_ollama.py")
    print("\n" + "="*70)
    
    input("\nAppuyez sur Entrée pour commencer les tests...")
    
    # Test 1: Health check
    test_health_check()
    
    # Test 2: Liste modèles
    test_list_models()
    
    # Demander si on continue avec Ollama
    print("\n" + "─"*70)
    continue_ollama = input("\n🤖 Continuer avec les tests Ollama (lents, 1-3 min)? [o/N]: ")
    
    if continue_ollama.lower() in ['o', 'oui', 'y', 'yes']:
        # Test 3: Analyse Ollama
        filename = test_simple_analysis_ollama()
        
        # Test 4: Fallback
        test_fallback_mode()
        
        # Test 5: Températures (optionnel)
        test_temps = input("\n🌡️  Tester différentes températures (lent)? [o/N]: ")
        if test_temps.lower() in ['o', 'oui', 'y', 'yes']:
            test_different_temperatures()
        
        # Test 6: Téléchargement
        if filename:
            test_download(filename)
    else:
        print("\n⏭️  Tests Ollama ignorés")
        
        # Test fallback uniquement
        filename = test_fallback_mode()
        if filename:
            test_download(filename)
    
    # Résumé
    print("\n" + "="*70)
    print(" "*20 + "✅ TESTS TERMINÉS")
    print("="*70)
    print("\n💡 Conseils:")
    print("   • Vérifiez les PDFs générés dans le dossier 'reports/'")
    print("   • Ajustez les hyperparamètres selon vos besoins")
    print("   • Utilisez un modèle plus léger si timeouts fréquents")
    print("\n📚 Documentation: Voir OLLAMA_GUIDE.md")
    print("\n")


if __name__ == '__main__':
    main()