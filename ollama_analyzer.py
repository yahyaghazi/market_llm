"""
Module d'intégration avec Ollama pour analyses LLM locales
Supporte DeepSeek-R1 et autres modèles Ollama
"""
import requests
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import logging

from models import ProductAnalysis, MarketAnalysisResult
from config import swot_data, recommendations_data

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class OllamaConfig:
    """Configuration pour Ollama"""
    host: str = "http://localhost:11434"
    model: str = "gemma3:4b"
    temperature: float = 0.7
    top_p: float = 0.9
    max_tokens: Optional[int] = 2000
    timeout: int = 120  # secondes
    
    # Options avancées
    num_ctx: int = 4096  # Taille du contexte
    num_predict: Optional[int] = None  # Alias pour max_tokens
    top_k: int = 40
    repeat_penalty: float = 1.1
    seed: Optional[int] = None
    
    def to_options_dict(self) -> Dict[str, Any]:
        """Convertit la config en dict pour l'API Ollama"""
        options = {
            "temperature": self.temperature,
            "top_p": self.top_p,
            "top_k": self.top_k,
            "repeat_penalty": self.repeat_penalty,
            "num_ctx": self.num_ctx,
        }
        
        if self.max_tokens:
            options["num_predict"] = self.max_tokens
        if self.num_predict:
            options["num_predict"] = self.num_predict
        if self.seed is not None:
            options["seed"] = self.seed
            
        return options


class OllamaClient:
    """Client pour interagir avec Ollama"""
    
    def __init__(self, config: OllamaConfig = None):
        """
        Initialiser le client Ollama
        
        Args:
            config: Configuration Ollama (utilise les valeurs par défaut si None)
        """
        self.config = config or OllamaConfig()
        self.base_url = self.config.host
        logger.info(f"🤖 OllamaClient initialisé avec modèle: {self.config.model}")
    
    def check_connection(self) -> bool:
        """
        Vérifie la connexion avec Ollama
        
        Returns:
            bool: True si Ollama est accessible
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                logger.info("✅ Connexion Ollama OK")
                return True
            else:
                logger.error(f"❌ Ollama répond avec code {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Impossible de se connecter à Ollama: {e}")
            return False
    
    def list_models(self) -> List[str]:
        """
        Liste les modèles disponibles dans Ollama
        
        Returns:
            List[str]: Liste des noms de modèles
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=10)
            if response.status_code == 200:
                data = response.json()
                models = [model['name'] for model in data.get('models', [])]
                logger.info(f"📋 Modèles disponibles: {', '.join(models)}")
                return models
            else:
                logger.error("❌ Impossible de lister les modèles")
                return []
        except Exception as e:
            logger.error(f"❌ Erreur lors du listing: {e}")
            return []
    
    def check_model_exists(self, model_name: str = None) -> bool:
        """
        Vérifie si un modèle est disponible
        
        Args:
            model_name: Nom du modèle (utilise config.model si None)
            
        Returns:
            bool: True si le modèle existe
        """
        model = model_name or self.config.model
        models = self.list_models()
        exists = model in models
        
        if not exists:
            logger.warning(f"⚠️  Modèle '{model}' non trouvé. Modèles disponibles: {models}")
        
        return exists
    
    def generate(
        self, 
        prompt: str, 
        system: str = None,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Génère une réponse avec Ollama
        
        Args:
            prompt: Le prompt utilisateur
            system: Prompt système (optionnel)
            stream: Streaming activé (non implémenté pour l'instant)
            
        Returns:
            Dict contenant la réponse et les métadonnées
        """
        url = f"{self.base_url}/api/generate"
        
        payload = {
            "model": self.config.model,
            "prompt": prompt,
            "stream": False,  # Forcer False pour simplifier
            "options": self.config.to_options_dict()
        }
        
        if system:
            payload["system"] = system
        
        logger.info(f"🚀 Génération avec {self.config.model}...")
        logger.debug(f"Prompt: {prompt[:100]}...")
        
        try:
            response = requests.post(
                url, 
                json=payload, 
                timeout=self.config.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info("✅ Génération réussie")
                logger.debug(f"Réponse: {result.get('response', '')[:100]}...")
                return result
            else:
                logger.error(f"❌ Erreur Ollama: {response.status_code}")
                logger.error(f"Détails: {response.text}")
                return {"error": f"Status {response.status_code}", "response": ""}
                
        except requests.exceptions.Timeout:
            logger.error(f"❌ Timeout après {self.config.timeout}s")
            return {"error": "Timeout", "response": ""}
        except Exception as e:
            logger.error(f"❌ Erreur lors de la génération: {e}")
            return {"error": str(e), "response": ""}
    
    def chat(
        self, 
        messages: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        Utilise l'API chat d'Ollama
        
        Args:
            messages: Liste de messages [{"role": "user", "content": "..."}]
            
        Returns:
            Dict contenant la réponse
        """
        url = f"{self.base_url}/api/chat"
        
        payload = {
            "model": self.config.model,
            "messages": messages,
            "stream": False,
            "options": self.config.to_options_dict()
        }
        
        logger.info(f"💬 Chat avec {self.config.model}...")
        
        try:
            response = requests.post(
                url, 
                json=payload, 
                timeout=self.config.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info("✅ Chat réussi")
                return result
            else:
                logger.error(f"❌ Erreur chat: {response.status_code}")
                return {"error": f"Status {response.status_code}", "message": {}}
                
        except Exception as e:
            logger.error(f"❌ Erreur chat: {e}")
            return {"error": str(e), "message": {}}


class PromptTemplates:
    """Templates de prompts pour différentes analyses"""
    
    @staticmethod
    def product_analysis_prompt(product: str, sector: str) -> str:
        """
        Crée un prompt pour analyser un produit
        
        Args:
            product: Nom du produit
            sector: Secteur d'activité
            
        Returns:
            str: Prompt formaté
        """
        return f"""Tu es un expert en analyse de marché et stratégie commerciale.

Analyse le produit suivant:
- **Produit:** {product}
- **Secteur:** {sector}

Fournis une analyse structurée au format JSON avec les clés suivantes:

{{
    "market_share": <float entre 5 et 35>,
    "price": <float entre 100 et 2000>,
    "satisfaction": <float entre 3.0 et 4.8>,
    "growth": <float entre -10 et 40>,
    "strengths": [<liste de 3-5 forces COURTES en français, 50 caractères max par item>],
    "weaknesses": [<liste de 3-4 faiblesses COURTES en français, 50 caractères max par item>],
    "opportunities": [<liste de 3-5 opportunités COURTES en français, 50 caractères max par item>],
    "threats": [<liste de 3-4 menaces COURTES en français, 50 caractères max par item>],
    "positioning": "<description du positionnement stratégique, 100-150 caractères>",
    "target_audience": "<description du public cible, 100-150 caractères>"
}}

IMPORTANT pour SWOT:
- Chaque item doit être COURT et CONCIS (max 50 caractères)
- Phrases complètes mais brèves
- Éviter les longues descriptions
- Exemple CORRECT: "Prix élevé limitant l'accessibilité"
- Exemple INCORRECT: "Prix premium élevé qui limite considérablement l'accessibilité pour une grande partie du marché cible potentiel"

Sois précis, réaliste et base-toi sur des données de marché actuelles.
Réponds UNIQUEMENT avec le JSON, sans texte avant ou après.
    """
    @staticmethod
    def executive_summary_prompt(
        products_data: List[Dict], 
        sector: str
    ) -> str:
        """
        Crée un prompt pour le résumé exécutif
        
        Args:
            products_data: Données des produits analysés
            sector: Secteur d'activité
            
        Returns:
            str: Prompt formaté
        """
        products_list = "\n".join([
            f"- {p['name']}: Part de marché {p['market_share']:.1f}%, "
            f"Satisfaction {p['satisfaction']:.1f}/5, "
            f"Croissance {p['growth']:+.1f}%"
            for p in products_data
        ])
        
        return f"""Tu es un consultant senior en stratégie.

Rédige un résumé exécutif professionnel (150-200 mots MAXIMUM) pour une étude de marché du secteur **{sector}**.

Données des produits analysés:
{products_list}

Le résumé doit:
1. Faire 150-200 mots MAXIMUM
2. Être en français professionnel et fluide
3. Mentionner le leader et sa part de marché
4. Inclure la satisfaction client moyenne
5. Évoquer les tendances et opportunités clés

CRITIQUE: 
- NE PAS utiliser de JSON ou code
- NE PAS mettre de balises markdown (pas de ```, pas de **bold**)
- NE PAS mettre de titre
- Rédiger en TEXTE BRUT continu
- UN SEUL paragraphe fluide (maximum 2 paragraphes)

Commence directement par: "Le secteur {sector}..."
    """
    @staticmethod
    def recommendations_prompt(
        products_data: List[Dict], 
        sector: str
    ) -> str:
        """
        Crée un prompt pour les recommandations stratégiques
        
        Args:
            products_data: Données des produits
            sector: Secteur d'activité
            
        Returns:
            str: Prompt formaté
        """
        return f"""Tu es un consultant en stratégie d'entreprise.

Fournis 6 recommandations stratégiques pour le secteur **{sector}**.

Contexte:
- Nombre de produits analysés: {len(products_data)}
- Secteur: {sector}

Fournis la liste au format JSON:
{{
    "recommendations": [
        "Recommandation 1 (30-60 mots)",
        "Recommandation 2 (30-60 mots)",
        "Recommandation 3 (30-60 mots)",
        "Recommandation 4 (30-60 mots)",
        "Recommandation 5 (30-60 mots)",
        "Recommandation 6 (30-60 mots)"
    ]
}}

Les recommandations doivent être:
- Concrètes et actionnables
- Spécifiques au secteur
- Professionnelles
- En français

Réponds UNIQUEMENT avec le JSON."""
    
    @staticmethod
    def system_prompt() -> str:
        """Prompt système pour tous les appels"""
        return """Tu es un expert en analyse de marché et stratégie commerciale avec 15 ans d'expérience. 
Tu fournis des analyses précises, factuelles et professionnelles basées sur des données de marché réelles.
Tu réponds toujours en français et au format demandé (JSON ou texte selon les instructions)."""


class OllamaMarketAnalyzer:
    """
    Analyseur de marché utilisant Ollama (LLM local)
    Compatible avec DeepSeek-R1, Llama3, Mistral, etc.
    """
    
    def __init__(
        self, 
        ollama_config: OllamaConfig = None,
        fallback_to_simulation: bool = True
    ):
        """
        Initialiser l'analyseur Ollama
        
        Args:
            ollama_config: Configuration Ollama personnalisée
            fallback_to_simulation: Utiliser simulation si Ollama indisponible
        """
        self.config = ollama_config or OllamaConfig()
        self.client = OllamaClient(self.config)
        self.fallback = fallback_to_simulation
        self.prompt_templates = PromptTemplates()
        
        # Vérifier la connexion
        if not self.client.check_connection():
            logger.warning("⚠️  Ollama non accessible")
            if not self.fallback:
                raise ConnectionError("Ollama non accessible et fallback désactivé")
        
        # Vérifier le modèle
        if not self.client.check_model_exists():
            logger.warning(f"⚠️  Modèle {self.config.model} non trouvé")
            if not self.fallback:
                raise ValueError(f"Modèle {self.config.model} non disponible")
        
        logger.info(f"✅ OllamaMarketAnalyzer initialisé")
        logger.info(f"   Modèle: {self.config.model}")
        logger.info(f"   Temperature: {self.config.temperature}")
        logger.info(f"   Top-P: {self.config.top_p}")
        logger.info(f"   Max tokens: {self.config.max_tokens}")
    
    def analyze_products(
        self, 
        products: List[str], 
        sector: str
    ) -> MarketAnalysisResult:
        """
        Analyse plusieurs produits avec Ollama
        
        Args:
            products: Liste des noms de produits
            sector: Secteur d'activité
            
        Returns:
            MarketAnalysisResult: Analyse complète
        """
        from datetime import datetime
        
        logger.info(f"\n{'='*70}")
        logger.info(f"🔍 ANALYSE OLLAMA - {len(products)} produits")
        logger.info(f"{'='*70}")
        
        # Analyser chaque produit
        analyses = []
        for i, product in enumerate(products, 1):
            logger.info(f"\n📊 Analyse {i}/{len(products)}: {product}")
            analysis = self._analyze_single_product(product, sector)
            analyses.append(analysis)
        
        # Générer résumé et recommandations
        logger.info(f"\n📝 Génération du résumé exécutif...")
        summary = self._generate_executive_summary(analyses, sector)
        
        logger.info(f"\n💡 Génération des recommandations...")
        recommendations = self._generate_recommendations(analyses, sector)
        
        logger.info(f"\n{'='*70}")
        logger.info(f"✅ ANALYSE TERMINÉE")
        logger.info(f"{'='*70}\n")
        
        return MarketAnalysisResult(
            sector=sector,
            analysis_date=datetime.now().strftime('%d/%m/%Y'),
            products=analyses,
            summary=summary,
            recommendations=recommendations
        )
    
    def _analyze_single_product(
        self, 
        product: str, 
        sector: str
    ) -> ProductAnalysis:
        """
        Analyse un produit avec Ollama
        
        Args:
            product: Nom du produit
            sector: Secteur d'activité
            
        Returns:
            ProductAnalysis: Analyse du produit
        """
        # Créer le prompt
        prompt = self.prompt_templates.product_analysis_prompt(product, sector)
        system = self.prompt_templates.system_prompt()
        
        # Appeler Ollama
        result = self.client.generate(prompt, system=system)
        
        # Parser la réponse
        if "error" in result or not result.get("response"):
            logger.warning(f"⚠️  Erreur LLM, utilisation simulation pour {product}")
            return self._fallback_analysis(product, sector)
        
        try:
            # Extraire le JSON de la réponse
            response_text = result["response"].strip()
            
            # Nettoyer la réponse (parfois le LLM ajoute du texte avant/après)
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                logger.warning("⚠️  JSON non trouvé dans la réponse")
                return self._fallback_analysis(product, sector)
            
            json_str = response_text[json_start:json_end]
            data = json.loads(json_str)
            
            # Valider et créer ProductAnalysis
            return ProductAnalysis(
                name=product,
                market_share=float(data.get('market_share', 20.0)),
                price=float(data.get('price', 500.0)),
                satisfaction=float(data.get('satisfaction', 4.0)),
                growth=float(data.get('growth', 10.0)),
                strengths=data.get('strengths', [])[:8],
                weaknesses=data.get('weaknesses', [])[:7],
                opportunities=data.get('opportunities', [])[:8],
                threats=data.get('threats', [])[:7],
                positioning=data.get('positioning', f"Acteur majeur dans {sector}"),
                target_audience=data.get('target_audience', f"Public cible {sector}")
            )
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.error(f"❌ Erreur parsing JSON: {e}")
            logger.debug(f"Réponse brute: {result.get('response', '')[:500]}")
            return self._fallback_analysis(product, sector)
    
    def _generate_executive_summary(
        self, 
        analyses: List[ProductAnalysis], 
        sector: str
    ) -> str:
        """Génère le résumé exécutif avec Ollama"""
        products_data = [
            {
                'name': a.name,
                'market_share': a.market_share,
                'satisfaction': a.satisfaction,
                'growth': a.growth
            }
            for a in analyses
        ]
        
        prompt = self.prompt_templates.executive_summary_prompt(products_data, sector)
        result = self.client.generate(prompt, system=self.prompt_templates.system_prompt())
        
        if "error" in result or not result.get("response"):
            return self._fallback_summary(analyses, sector)
        
        # Nettoyer la réponse
        summary = result["response"].strip()
        
        # Retirer les balises JSON si présentes
        if summary.startswith('```json'):
            summary = summary.replace('```json', '').replace('```', '')
        if summary.startswith('{') and summary.endswith('}'):
            # Tenter d'extraire le texte du JSON
            try:
                import json
                data = json.loads(summary)
                if 'resume_executif' in data:
                    summary = data['resume_executif']
                elif 'summary' in data:
                    summary = data['summary']
                elif 'text' in data:
                    summary = data['text']
            except:
                pass
        
        # Nettoyer les balises markdown
        summary = summary.replace('**', '').replace('__', '')
        summary = summary.replace('```', '').replace('`', '')
        
        # Nettoyer les sauts de ligne excessifs
        summary = ' '.join(summary.split())
        
        # Limiter à 250 mots max
        words = summary.split()
        if len(words) > 250:
            summary = ' '.join(words[:250]) + '...'
        
        return summary
    
    def _generate_recommendations(
        self, 
        analyses: List[ProductAnalysis], 
        sector: str
    ) -> List[str]:
        """Génère les recommandations avec Ollama"""
        products_data = [{'name': a.name} for a in analyses]
        
        prompt = self.prompt_templates.recommendations_prompt(products_data, sector)
        result = self.client.generate(prompt, system=self.prompt_templates.system_prompt())
        
        if "error" in result or not result.get("response"):
            return self._fallback_recommendations()
        
        try:
            response_text = result["response"].strip()
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start != -1 and json_end != 0:
                json_str = response_text[json_start:json_end]
                data = json.loads(json_str)
                recs = data.get('recommendations', [])
                if len(recs) >= 6:
                    return recs[:6]
        except:
            pass
        
        return self._fallback_recommendations()
    
    def _fallback_analysis(self, product: str, sector: str) -> ProductAnalysis:
        """Analyse de secours (simulation)"""
        import numpy as np
        seed = abs(hash(product)) % 10000
        np.random.seed(seed)
        
        return ProductAnalysis(
            name=product,
            market_share=round(np.random.uniform(5, 35), 2),
            price=round(np.random.uniform(100, 2000), 2),
            satisfaction=round(np.random.uniform(3.0, 4.8), 2),
            growth=round(np.random.uniform(-10, 40), 2),
            strengths=np.random.choice(swot_data.STRENGTHS, size=4, replace=False).tolist(),
            weaknesses=np.random.choice(swot_data.WEAKNESSES, size=3, replace=False).tolist(),
            opportunities=np.random.choice(swot_data.OPPORTUNITIES, size=4, replace=False).tolist(),
            threats=np.random.choice(swot_data.THREATS, size=3, replace=False).tolist(),
            positioning=f"Acteur dans le segment {sector}",
            target_audience=f"Public cible {sector}"
        )
    
    def _fallback_summary(self, analyses: List[ProductAnalysis], sector: str) -> str:
        """Résumé de secours"""
        import numpy as np
        avg_growth = np.mean([a.growth for a in analyses])
        avg_satisfaction = np.mean([a.satisfaction for a in analyses])
        leader = max(analyses, key=lambda x: x.market_share)
        
        return (
            f"Le secteur {sector} montre une dynamique "
            f"{'positive' if avg_growth > 0 else 'contrastée'} avec une croissance moyenne "
            f"de {avg_growth:.1f}%. {leader.name} domine avec {leader.market_share:.1f}% "
            f"de parts de marché. Satisfaction moyenne: {avg_satisfaction:.1f}/5."
        )
    
    def _fallback_recommendations(self) -> List[str]:
        """Recommandations de secours"""
        import numpy as np
        return np.random.choice(
            recommendations_data.RECOMMENDATIONS,
            size=6,
            replace=False
        ).tolist()