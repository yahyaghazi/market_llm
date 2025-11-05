# 📊 Application d'Étude de Marché - Guide Complet

Application Flask professionnelle pour générer automatiquement des études de marché comparatives avec rapports PDF, graphiques et analyses SWOT.

## 🎯 Fonctionnalités

✅ **Analyse comparative multi-produits** (2 à 10 produits)  
✅ **Génération de PDF professionnels** avec mise en page soignée  
✅ **3 types de graphiques** (parts de marché, prix/satisfaction, croissance)  
✅ **Analyse SWOT complète** pour chaque produit  
✅ **Tableaux comparatifs détaillés**  
✅ **API REST** simple et intuitive  
✅ **Interface web** pour tests rapides  

---

## 🚀 Installation (Windows)

### Prérequis

- Python 3.9+ installé ([Télécharger](https://www.python.org/downloads/))
- Git (optionnel)

### Étape 1: Cloner ou créer le projet

```powershell
# Option A: Si vous avez Git
git clone <votre-repo>
cd market-study

# Option B: Créer manuellement
mkdir market-study
cd market-study
```

### Étape 2: Créer l'environnement virtuel

```powershell
# Créer l'environnement
python -m venv venv

# Si erreur de politique d'exécution:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process

# Activer l'environnement
.\venv\Scripts\Activate.ps1
```

### Étape 3: Installer les dépendances

**Méthode automatique** (recommandée):
```powershell
# Lancer le script d'installation
.\install.bat
```

**Méthode manuelle**:
```powershell
# 1. Mettre à jour pip
python -m pip install --upgrade pip setuptools wheel

# 2. NumPy en premier (crucial!)
pip install numpy>=1.24.0

# 3. Flask
pip install Flask==3.0.0 flask-cors==4.0.0

# 4. Matplotlib
pip install matplotlib>=3.7.0

# 5. Autres packages
pip install reportlab Pillow pandas pydantic python-dotenv requests
```

### Étape 4: Vérifier l'installation

```powershell
python -c "import flask, numpy, matplotlib, reportlab; print('✓ Tout fonctionne!')"
```

---

## 📁 Structure du Projet

```
market-study/
│
├── venv/                   # Environnement virtuel
├── reports/                # PDFs générés (créé automatiquement)
├── logs/                   # Logs application (créé automatiquement)
│
├── app.py                  # Application Flask principale
├── test_api.py             # Script de test
├── install.bat             # Script d'installation Windows
├── .env                    # Configuration (à créer)
├── README.md               # Ce fichier
│
└── requirements.txt        # Dépendances (optionnel)
```

---

## ⚙️ Configuration

Créez un fichier `.env` à la racine :

```ini
# Configuration Flask
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=votre_cle_secrete_aleatoire

# Dossiers
REPORTS_DIR=reports
LOGS_DIR=logs
```

---

## 🎮 Utilisation

### 1. Démarrer le serveur

```powershell
# Activer l'environnement si pas déjà fait
.\venv\Scripts\Activate.ps1

# Lancer l'application
python app.py
```

Vous devriez voir :
```
======================================================================
                    🚀 MARKET STUDY API
======================================================================

📁 Dossier des rapports: C:\...\market-study\reports
📁 Dossier des logs: C:\...\market-study\logs

🌐 URL: http://localhost:5000
📊 Interface: http://localhost:5000/
❤️  Health Check: http://localhost:5000/health

======================================================================

💡 Appuyez sur Ctrl+C pour arrêter le serveur
```

### 2. Tester l'API

**Option A: Depuis le navigateur**

Ouvrez http://localhost:5000 dans votre navigateur

**Option B: Avec le script de test**

Dans un nouveau terminal PowerShell :
```powershell
.\venv\Scripts\Activate.ps1
python test_api.py
```

**Option C: Avec curl**
```powershell
# Health check
curl http://localhost:5000/health

# Analyse de marché
curl -X POST http://localhost:5000/api/analyze `
  -H "Content-Type: application/json" `
  -d '{\"products\":[\"iPhone 15\",\"Galaxy S24\"],\"sector\":\"Smartphones\"}'
```

**Option D: Avec Python**
```python
import requests

data = {
    "products": ["Produit A", "Produit B", "Produit C"],
    "sector": "Votre Secteur"
}

response = requests.post('http://localhost:5000/api/analyze', json=data)
print(response.json())
```

---

## 📡 API Endpoints

### GET /health
Vérification de l'état du service

**Réponse:**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-05T10:30:00",
  "version": "1.0.0",
  "service": "Market Study API"
}
```

### POST /api/analyze
Génère une étude de marché complète

**Body:**
```json
{
  "products": ["Produit 1", "Produit 2", "Produit 3"],
  "sector": "Nom du Secteur"
}
```

**Contraintes:**
- Minimum 2 produits
- Maximum 10 produits
- Secteur obligatoire

**Réponse (succès):**
```json
{
  "success": true,
  "pdf_filename": "etude_marche_20251105_103045.pdf",
  "pdf_url": "/api/download/etude_marche_20251105_103045.pdf",
  "analysis": {
    "sector": "Smartphones",
    "date": "05/11/2025",
    "products_count": 2,
    "products": [
      {
        "name": "iPhone 15",
        "market_share": 28.5,
        "price": 1179.0,
        "satisfaction": 4.5,
        "growth": 12.3
      }
    ],
    "summary": "Le secteur Smartphones présente..."
  }
}
```

**Réponse (erreur):**
```json
{
  "error": "Au moins 2 produits sont requis"
}
```

### GET /api/download/<filename>
Télécharge un rapport PDF généré

**Exemple:**
```
http://localhost:5000/api/download/etude_marche_20251105_103045.pdf
```

### GET /api/reports
Liste tous les rapports disponibles

**Réponse:**
```json
{
  "total": 5,
  "reports": [
    {
      "filename": "etude_marche_20251105_103045.pdf",
      "size": 1234567,
      "created": "2025-11-05T10:30:45",
      "download_url": "/api/download/etude_marche_20251105_103045.pdf"
    }
  ]
}
```

---

## 📄 Structure du Rapport PDF

Le rapport généré contient :

### 1. Page de Garde
- Titre du secteur
- Type d'analyse
- Date de génération
- Métadonnées

### 2. Résumé Exécutif
- Vue d'ensemble du marché
- Statistiques clés
- Insights principaux

### 3. Analyse Comparative
- Tableau comparatif complet
- Parts de marché
- Prix moyens
- Satisfaction client
- Taux de croissance

### 4. Visualisations Graphiques
- **Graphique 1:** Parts de marché (camembert)
- **Graphique 2:** Prix vs Satisfaction (nuage de points)
- **Graphique 3:** Croissance annuelle (barres)

### 5. Analyses Détaillées par Produit
Pour chaque produit :
- Indicateurs clés
- Analyse SWOT (tableau 2x2)
- Positionnement
- Public cible

### 6. Conclusion et Recommandations
- Synthèse des constats
- 6 recommandations stratégiques
- Prochaines étapes suggérées

---

## 🧪 Exemples d'Utilisation

### Exemple 1: Analyse Smartphones

```python
import requests

data = {
    "products": [
        "iPhone 15 Pro",
        "Samsung Galaxy S24 Ultra",
        "Google Pixel 8 Pro"
    ],
    "sector": "Smartphones Premium"
}

response = requests.post('http://localhost:5000/api/analyze', json=data)
result = response.json()

print(f"PDF généré: {result['pdf_filename']}")
print(f"Télécharger: http://localhost:5000{result['pdf_url']}")
```

### Exemple 2: Analyse Automobile

```python
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

response = requests.post('http://localhost:5000/api/analyze', json=data)
```

### Exemple 3: Analyse SaaS

```python
data = {
    "products": [
        "Salesforce",
        "HubSpot",
        "Microsoft Dynamics 365",
        "Zoho CRM"
    ],
    "sector": "Solutions CRM Entreprise"
}

response = requests.post('http://localhost:5000/api/analyze', json=data)
```

---

## 🛠️ Dépannage

### Problème: Erreur lors de l'installation de NumPy

**Solution:**
```powershell
# Installer NumPy séparément
python -m pip install --upgrade pip setuptools wheel
pip install numpy
```

### Problème: "cannot be loaded" lors de l'activation

**Solution:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
.\venv\Scripts\Activate.ps1
```

### Problème: Port 5000 déjà utilisé

**Solution:**
Modifier dans `app.py` :
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Changer le port
```

### Problème: Les graphiques ne s'affichent pas

**Solution:**
Vérifier que matplotlib utilise le bon backend :
```python
import matplotlib
matplotlib.use('Agg')  # Ajouté au début de app.py
```

---

## 📝 Notes Importantes

### Limitations Actuelles

- Les analyses sont simulées (pas de vraie API LLM)
- Données générées aléatoirement mais réalistes
- Limite de 10 produits par analyse
- Pas d'authentification (pour dev uniquement)

### Pour la Production

Pour utiliser en production :

1. **Ajouter une vraie API LLM** :
```python
import openai

def analyze_with_llm(products, sector):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[...]
    )
    return response
```

2. **Ajouter l'authentification** :
```python
from flask_httpauth import HTTPBasicAuth
auth = HTTPBasicAuth()
```

3. **Utiliser un serveur de production** :
```powershell
pip install gunicorn
gunicorn -w 4 app:app
```

4. **Ajouter une base de données** pour l'historique

---

## 🎓 Explication Technique

### Prompts LLM (Structure)

Le système utilise des prompts structurés pour obtenir des analyses cohérentes :

```
CONTEXTE: Expert en études de marché
TÂCHE: Analyser les produits {products} dans {sector}
FORMAT: JSON structuré
SECTIONS: 
  - Métriques (parts, prix, satisfaction, croissance)
  - SWOT (forces, faiblesses, opportunités, menaces)
  - Positionnement
  - Public cible
```

### Génération PDF

Utilise ReportLab avec :
- Styles personnalisés cohérents
- Mise en page professionnelle
- Tableaux formatés
- Images intégrées (graphiques)

### Graphiques

Matplotlib génère 3 types de visualisations :
1. **Pie Chart**: Parts de marché
2. **Scatter Plot**: Prix vs Satisfaction
3. **Bar Chart**: Croissance

---

## 🤝 Contribution

Pour contribuer :

1. Fork le projet
2. Créer une branche (`git checkout -b feature/amazing`)
3. Commit (`git commit -m 'Add feature'`)
4. Push (`git push origin feature/amazing`)
5. Ouvrir une Pull Request

---

## 📄 Licence

MIT License - Libre d'utilisation pour projets personnels et commerciaux

---

## 📞 Support

Pour toute question :
- Ouvrir une issue sur GitHub
- Consulter la documentation dans les commentaires du code

---

## ✨ Améliorations Futures

- [ ] Intégration API LLM réelle (GPT-4, Claude)
- [ ] Authentification utilisateur
- [ ] Base de données pour historique
- [ ] Export PowerPoint (.pptx)
- [ ] Envoi par email automatique
- [ ] Dashboard d'administration
- [ ] API publique avec rate limiting
- [ ] Support multilingue

---

**Développé avec ❤️ pour l'analyse de marché automatisée**