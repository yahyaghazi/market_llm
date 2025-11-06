# 🤖 Guide Ollama - Market Study Generator

## 📋 Table des Matières

1. [Installation Ollama](#installation-ollama)
2. [Configuration](#configuration)
3. [Utilisation](#utilisation)
4. [Hyperparamètres](#hyperparamètres)
5. [Modèles Recommandés](#modèles-recommandés)
6. [Exemples](#exemples)
7. [Dépannage](#dépannage)

---

## 🚀 Installation Ollama

### Windows

```powershell
# 1. Télécharger Ollama
# Aller sur: https://ollama.com/download
# Télécharger OllamaSetup.exe et l'installer

# 2. Vérifier l'installation
ollama --version

# 3. Démarrer le service (automatique normalement)
# Si besoin manuel:
ollama serve
```

### Linux / Mac

```bash
# Installation
curl -fsSL https://ollama.com/install.sh | sh

# Vérifier
ollama --version

# Démarrer (automatique normalement)
ollama serve
```

---

## 📥 Télécharger les Modèles

### DeepSeek-R1 (Recommandé)

```bash
# Version 14B (14 milliards de paramètres)
ollama pull gemma3:4b

# Version 7B (plus légère, ~8GB RAM)
ollama pull deepseek-r1:7b

# Version 1.5B (très légère, ~2GB RAM)
ollama pull deepseek-r1:1.5b
```

### Autres Modèles Recommandés

```bash
# Llama 3.1 (excellent pour analyses)
ollama pull llama3.1:8b
ollama pull llama3.1:70b  # Si GPU puissant

# Mistral (rapide et efficace)
ollama pull mistral:7b

# Qwen 2.5 (bon pour français)
ollama pull qwen2.5:7b

# Gemma 2 (de Google)
ollama pull gemma2:9b
```

### Vérifier les Modèles Installés

```bash
# Lister tous les modèles
ollama list

# Exemple de sortie:
# NAME                    ID              SIZE    MODIFIED
# gemma3:4b        a1b2c3d4        8.1GB   2 hours ago
# llama3.1:8b            e5f6g7h8        4.7GB   1 day ago
```

---

## ⚙️ Configuration de l'Application

### 1. Installation des Dépendances Python

```bash
# Activer l'environnement virtuel
.\venv\Scripts\Activate.ps1  # Windows
source venv/bin/activate     # Linux/Mac

# Installer (requests est la seule nouvelle dépendance)
pip install requests
```

### 2. Structure des Fichiers

```
market-study/
├── ollama_analyzer.py      # ✨ Nouveau module Ollama
├── app_ollama.py           # ✨ App Flask avec Ollama
├── config.py               # Configuration
├── models.py               # Modèles de données
├── charts.py               # Graphiques
├── pdf_generator.py        # Génération PDF
└── requirements.txt        # Dépendances
```

### 3. Démarrer l'Application

```bash
# Option 1: Utiliser le nouveau fichier
python app_ollama.py

# Option 2: Renommer et utiliser
cp app_ollama.py app.py
python app.py
```

---

## 🎛️ Hyperparamètres Expliqués

### Temperature (0.0 - 2.0)

**Contrôle la créativité/randomness des réponses**

```python
# Temperature = 0.0 → Déterministe, répétable
{
  "ollama": {
    "temperature": 0.0
  }
}
# Parfait pour: Analyses factuelles, données précises

# Temperature = 0.7 → Équilibré (DÉFAUT)
{
  "ollama": {
    "temperature": 0.7
  }
}
# Parfait pour: Usage général, bon mix créativité/précision

# Temperature = 1.5 → Très créatif
{
  "ollama": {
    "temperature": 1.5
  }
}
# Parfait pour: Recommandations innovantes, brainstorming
```

**Recommandations:**
- Analyses financières: `0.2 - 0.4`
- Analyses de marché: `0.6 - 0.8` ✅ **Recommandé**
- Recommandations stratégiques: `0.8 - 1.2`

### Top-P / Nucleus Sampling (0.0 - 1.0)

**Contrôle la diversité du vocabulaire**

```python
# Top-P = 0.5 → Vocabulaire restreint, conservateur
{
  "ollama": {
    "top_p": 0.5
  }
}

# Top-P = 0.9 → Bon équilibre (DÉFAUT)
{
  "ollama": {
    "top_p": 0.9
  }
}
# ✅ Recommandé pour usage général

# Top-P = 1.0 → Vocabulaire complet
{
  "ollama": {
    "top_p": 1.0
  }
}
```

### Max Tokens (100 - 4000+)

**Longueur maximale de la réponse**

```python
# Court
{
  "ollama": {
    "max_tokens": 500
  }
}
# Usage: Résumés courts

# Moyen (DÉFAUT)
{
  "ollama": {
    "max_tokens": 2000
  }
}
# ✅ Recommandé: Analyses complètes

# Long
{
  "ollama": {
    "max_tokens": 4000
  }
}
# Usage: Analyses très détaillées
```

### Top-K (1 - 100)

**Limite le nombre de tokens candidats**

```python
{
  "ollama": {
    "top_k": 40  # Défaut
  }
}
```

- `top_k: 10` → Très conservateur
- `top_k: 40` → Équilibré ✅ **Recommandé**
- `top_k: 100` → Très diversifié

### Repeat Penalty (1.0 - 2.0)

**Pénalise la répétition de mots**

```python
{
  "ollama": {
    "repeat_penalty": 1.1  # Défaut
  }
}
```

- `1.0` → Pas de pénalité
- `1.1` → Léger ✅ **Recommandé**
- `1.5+` → Fort (peut devenir incohérent)

---

## 🎯 Modèles Recommandés par Usage

### Pour Qualité Maximale

**gemma3:4b** + Configuration:
```json
{
  "ollama": {
    "model": "gemma3:4b",
    "temperature": 0.7,
    "top_p": 0.9,
    "max_tokens": 2500
  }
}
```

**Avantages:**
- Analyses très précises
- Excellent en français
- Bon raisonnement

**Inconvénients:**
- Nécessite ~16GB RAM
- Plus lent (~30-60s par produit)

### Pour Rapidité

**Llama 3.1:8b** + Configuration:
```json
{
  "ollama": {
    "model": "llama3.1:8b",
    "temperature": 0.7,
    "top_p": 0.9,
    "max_tokens": 2000
  }
}
```

**Avantages:**
- Rapide (~10-20s par produit)
- Nécessite ~8GB RAM
- Bon équilibre qualité/vitesse

### Pour Machine Légère

**DeepSeek-R1:1.5b** + Configuration:
```json
{
  "ollama": {
    "model": "deepseek-r1:1.5b",
    "temperature": 0.8,
    "top_p": 0.95,
    "max_tokens": 1500
  }
}
```

**Avantages:**
- Très rapide (~5-10s)
- Nécessite seulement ~2GB RAM
- Fonctionne sans GPU

**Inconvénients:**
- Qualité moindre
- Moins de nuance

---

## 📝 Exemples d'Utilisation

### Exemple 1: Analyse Standard

```bash
curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "products": ["iPhone 15", "Samsung Galaxy S24"],
    "sector": "Smartphones Premium",
    "ollama": {
      "use_ollama": true,
      "model": "gemma3:4b",
      "temperature": 0.7,
      "top_p": 0.9
    }
  }'
```

### Exemple 2: Analyse Créative

```bash
curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "products": ["Tesla Model 3", "BMW i4"],
    "sector": "Véhicules Électriques",
    "ollama": {
      "model": "gemma3:4b",
      "temperature": 1.2,
      "top_p": 0.95,
      "max_tokens": 3000
    }
  }'
```

### Exemple 3: Analyse Factuelle (Déterministe)

```bash
curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "products": ["Product A", "Product B"],
    "sector": "Technology",
    "ollama": {
      "model": "llama3.1:8b",
      "temperature": 0.2,
      "top_p": 0.8,
      "seed": 42
    }
  }'
```

### Exemple 4: Mode Fallback (Sans Ollama)

```bash
curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "products": ["Product X", "Product Y"],
    "sector": "Market",
    "ollama": {
      "use_ollama": false
    }
  }'
```

### Exemple Python

```python
import requests

# Configuration
data = {
    "products": ["MacBook Pro M3", "Dell XPS 15", "ThinkPad X1"],
    "sector": "Laptops Professionnels",
    "ollama": {
        "use_ollama": True,
        "model": "gemma3:4b",
        "temperature": 0.7,
        "top_p": 0.9,
        "max_tokens": 2000
    }
}

# Appel API
response = requests.post(
    'http://localhost:5000/api/analyze',
    json=data,
    timeout=300  # 5 minutes max
)

# Résultat
if response.status_code == 200:
    result = response.json()
    print(f"✅ PDF généré: {result['pdf_filename']}")
    print(f"📊 {result['analysis']['products_count']} produits analysés")
    print(f"🤖 Modèle utilisé: {result['analysis']['model']}")
else:
    print(f"❌ Erreur: {response.json()}")
```

---

## 🔍 Vérification et Tests

### 1. Tester la Connexion Ollama

```bash
# Endpoint health
curl http://localhost:5000/health

# Réponse attendue:
{
  "status": "healthy",
  "version": "2.1.0-ollama",
  "ollama": {
    "available": true,
    "default_model": "gemma3:4b"
  }
}
```

### 2. Lister les Modèles Disponibles

```bash
curl http://localhost:5000/ollama/models

# Réponse:
{
  "success": true,
  "models": [
    "gemma3:4b",
    "llama3.1:8b",
    "mistral:7b"
  ],
  "count": 3
}
```

### 3. Test Complet

```bash
# Lancer l'app
python app_ollama.py

# Dans un autre terminal
python test_ollama.py  # Script de test (à créer)
```

---

## 🐛 Dépannage

### Problème: "Ollama non accessible"

**Causes possibles:**
1. Ollama n'est pas démarré
2. Mauvais port
3. Firewall bloque

**Solutions:**
```bash
# Vérifier si Ollama tourne
curl http://localhost:11434/api/tags

# Démarrer Ollama
ollama serve

# Vérifier le port (par défaut: 11434)
# Dans ollama_analyzer.py, modifier si nécessaire:
host: str = "http://localhost:11434"
```

### Problème: "Modèle non trouvé"

**Solution:**
```bash
# Télécharger le modèle
ollama pull gemma3:4b

# Vérifier
ollama list
```

### Problème: "Timeout après 120s"

**Causes:**
- Modèle trop gros pour votre machine
- Pas de GPU, traitement lent

**Solutions:**
```python
# 1. Augmenter le timeout dans ollama_analyzer.py
timeout: int = 300  # 5 minutes

# 2. Utiliser un modèle plus léger
"model": "deepseek-r1:7b"  # Au lieu de 14b

# 3. Réduire max_tokens
"max_tokens": 1000  # Au lieu de 2000
```

### Problème: "Erreur parsing JSON"

**Cause:** Le LLM ne génère pas un JSON valide

**Solution automatique:** Le système utilise déjà le fallback

**Solution manuelle:** Ajuster temperature
```python
# Plus bas = plus structuré
"temperature": 0.3
```

### Problème: "Out of Memory"

**Solutions:**
```bash
# 1. Utiliser un modèle plus petit
ollama pull deepseek-r1:1.5b

# 2. Fermer autres applications
# 3. Vérifier RAM disponible

# Windows
wmic OS get FreePhysicalMemory

# Linux
free -h
```

---

## 📊 Comparaison des Modèles

| Modèle | Taille | RAM Requise | Vitesse | Qualité | Français |
|--------|--------|-------------|---------|---------|----------|
| **gemma3:4b** | 8.1GB | 16GB | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **deepseek-r1:7b** | 4.1GB | 8GB | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **llama3.1:8b** | 4.7GB | 8GB | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **mistral:7b** | 4.1GB | 8GB | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **qwen2.5:7b** | 4.4GB | 8GB | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **gemma2:9b** | 5.4GB | 10GB | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |

**Légende:**
- ⭐⭐⭐⭐⭐ Excellent
- ⭐⭐⭐⭐ Très bon
- ⭐⭐⭐ Bon
- ⭐⭐ Moyen

---

## 🎓 Bonnes Pratiques

### 1. Configuration par Défaut (Recommandée)

```json
{
  "ollama": {
    "model": "gemma3:4b",
    "temperature": 0.7,
    "top_p": 0.9,
    "max_tokens": 2000,
    "top_k": 40,
    "repeat_penalty": 1.1
  }
}
```

### 2. Pour Données Financières

```json
{
  "ollama": {
    "model": "gemma3:4b",
    "temperature": 0.3,
    "top_p": 0.8,
    "max_tokens": 1500
  }
}
```

### 3. Pour Brainstorming

```json
{
  "ollama": {
    "model": "llama3.1:8b",
    "temperature": 1.2,
    "top_p": 0.95,
    "max_tokens": 3000
  }
}
```

### 4. Pour Tests Rapides

```json
{
  "ollama": {
    "model": "deepseek-r1:1.5b",
    "temperature": 0.7,
    "max_tokens": 1000
  }
}
```

---

## 📚 Ressources Supplémentaires

- **Ollama Docs:** https://github.com/ollama/ollama/blob/main/docs/api.md
- **DeepSeek:** https://ollama.com/library/deepseek-r1
- **Llama 3.1:** https://ollama.com/library/llama3.1
- **Mistral:** https://ollama.com/library/mistral

---

## ✅ Checklist de Démarrage

- [ ] Ollama installé (`ollama --version`)
- [ ] Modèle téléchargé (`ollama pull gemma3:4b`)
- [ ] Ollama démarré (`ollama serve` ou automatique)
- [ ] Fichier `ollama_analyzer.py` copié
- [ ] Fichier `app_ollama.py` copié
- [ ] Application lancée (`python app_ollama.py`)
- [ ] Health check OK (`curl localhost:5000/health`)
- [ ] Modèles listés (`curl localhost:5000/ollama/models`)
- [ ] Premier test réussi

---

**🎉 Vous êtes prêt à utiliser DeepSeek-R1 pour vos études de marché !**

*Market Study Generator v2.1 - Ollama Edition*