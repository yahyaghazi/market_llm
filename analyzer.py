"""
Module d'analyse de marché
Génère des analyses réalistes basées sur des données simulées
"""
import numpy as np
from typing import List
from datetime import datetime

from models import ProductAnalysis, MarketAnalysisResult
from config import swot_data, recommendations_data


class MarketAnalyzer:
    """
    Analyseur de marché avec génération de données réalistes
    
    Note: En production, cette classe devrait appeler une vraie API LLM
    (OpenAI GPT-4, Anthropic Claude, etc.) pour des analyses authentiques.
    """
    
    def __init__(self):
        """Initialiser l'analyseur"""
        self.swot_data = swot_data
        self.recommendations_data = recommendations_data
    
    def analyze_products(self, products: List[str], sector: str) -> MarketAnalysisResult:
        """
        Génère une analyse complète pour plusieurs produits
        
        Args:
            products: Liste des noms de produits à analyser
            sector: Secteur d'activité
            
        Returns:
            MarketAnalysisResult: Analyse complète du marché
        """
        print(f"🔍 Analyse de {len(products)} produits dans le secteur: {sector}")
        
        # Analyser chaque produit
        analyses = []
        for product in products:
            analysis = self._analyze_single_product(product, sector)
            analyses.append(analysis)
        
        # Générer le résumé et les recommandations
        summary = self._generate_executive_summary(analyses, sector)
        recommendations = self._generate_recommendations(analyses, sector)
        
        return MarketAnalysisResult(
            sector=sector,
            analysis_date=datetime.now().strftime('%d/%m/%Y'),
            products=analyses,
            summary=summary,
            recommendations=recommendations
        )
    
    def _analyze_single_product(self, product: str, sector: str) -> ProductAnalysis:
        """
        Analyse un produit individuel
        
        Args:
            product: Nom du produit
            sector: Secteur d'activité
            
        Returns:
            ProductAnalysis: Analyse détaillée du produit
        """
        # Seed pour reproductibilité (même produit = mêmes résultats)
        seed = abs(hash(product)) % 10000
        np.random.seed(seed)
        
        # Générer les métriques
        market_share = round(np.random.uniform(5, 35), 2)
        price = round(np.random.uniform(100, 2000), 2)
        satisfaction = round(np.random.uniform(3.0, 4.8), 2)
        growth = round(np.random.uniform(-10, 40), 2)
        
        # Sélectionner les éléments SWOT
        num_strengths = np.random.randint(3, 6)
        num_weaknesses = np.random.randint(3, 5)
        num_opportunities = np.random.randint(3, 6)
        num_threats = np.random.randint(3, 5)
        
        strengths = np.random.choice(
            self.swot_data.STRENGTHS, 
            size=num_strengths, 
            replace=False
        ).tolist()
        
        weaknesses = np.random.choice(
            self.swot_data.WEAKNESSES,
            size=num_weaknesses,
            replace=False
        ).tolist()
        
        opportunities = np.random.choice(
            self.swot_data.OPPORTUNITIES,
            size=num_opportunities,
            replace=False
        ).tolist()
        
        threats = np.random.choice(
            self.swot_data.THREATS,
            size=num_threats,
            replace=False
        ).tolist()
        
        # Générer le positionnement et la cible
        positioning = self._generate_positioning(product, sector, market_share, price)
        target_audience = self._generate_target_audience(sector, price, satisfaction)
        
        return ProductAnalysis(
            name=product,
            market_share=market_share,
            price=price,
            satisfaction=satisfaction,
            growth=growth,
            strengths=strengths,
            weaknesses=weaknesses,
            opportunities=opportunities,
            threats=threats,
            positioning=positioning,
            target_audience=target_audience
        )
    
    def _generate_positioning(
        self, 
        product: str, 
        sector: str, 
        market_share: float, 
        price: float
    ) -> str:
        """Génère une description de positionnement"""
        if market_share > 25:
            position = "Leader incontesté"
        elif market_share > 15:
            position = "Acteur majeur"
        else:
            position = "Challenger stratégique"
        
        if price > 1000:
            segment = "ultra-premium"
        elif price > 500:
            segment = "premium"
        else:
            segment = "accessible premium"
        
        return (
            f"{position} dans le segment {segment} du secteur {sector}, "
            f"{product} se distingue par une stratégie de différenciation axée "
            f"sur l'innovation et la qualité."
        )
    
    def _generate_target_audience(
        self, 
        sector: str, 
        price: float, 
        satisfaction: float
    ) -> str:
        """Génère une description du public cible"""
        if price > 1000:
            audience = "clientèle haut de gamme et décideurs d'entreprise"
        elif price > 500:
            audience = "professionnels et particuliers exigeants"
        else:
            audience = "grand public averti et early adopters"
        
        loyalty = "très fidèle" if satisfaction > 4.2 else "fidèle"
        
        return (
            f"Cible principalement une {audience} du secteur {sector}, "
            f"caractérisée par une base {loyalty} et des attentes élevées "
            f"en termes de qualité et d'innovation."
        )
    
    def _generate_executive_summary(
        self, 
        analyses: List[ProductAnalysis], 
        sector: str
    ) -> str:
        """
        Génère un résumé exécutif de l'analyse
        
        Args:
            analyses: Liste des analyses de produits
            sector: Secteur d'activité
            
        Returns:
            str: Résumé exécutif
        """
        # Calculer les statistiques globales
        avg_growth = np.mean([a.growth for a in analyses])
        avg_satisfaction = np.mean([a.satisfaction for a in analyses])
        total_market_share = sum([a.market_share for a in analyses])
        
        # Identifier le leader
        leader = max(analyses, key=lambda x: x.market_share)
        
        # Déterminer la dynamique du marché
        market_dynamic = "positive" if avg_growth > 5 else "contrastée" if avg_growth > 0 else "difficile"
        
        # Évaluer la perception client
        if avg_satisfaction > 4.3:
            perception = "excellente perception globale"
        elif avg_satisfaction > 4.0:
            perception = "bonne perception globale"
        else:
            perception = "perception mitigée"
        
        return (
            f"Le secteur {sector} montre une dynamique {market_dynamic} "
            f"avec une croissance moyenne de {avg_growth:.1f}%. {leader.name} domine le marché avec "
            f"{leader.market_share:.1f}% de parts de marché. La satisfaction client moyenne s'établit à "
            f"{avg_satisfaction:.1f}/5, reflétant une {perception}. Les {len(analyses)} produits "
            f"analysés représentent {total_market_share:.1f}% du marché total, témoignant d'une "
            f"concentration significative. L'analyse révèle des opportunités substantielles dans "
            f"la transformation digitale, l'innovation produit et l'expansion géographique."
        )
    
    def _generate_recommendations(
        self, 
        analyses: List[ProductAnalysis], 
        sector: str
    ) -> List[str]:
        """
        Génère des recommandations stratégiques
        
        Args:
            analyses: Liste des analyses de produits
            sector: Secteur d'activité
            
        Returns:
            List[str]: Liste de 6 recommandations
        """
        # Sélectionner 6 recommandations pertinentes
        np.random.seed(abs(hash(sector)) % 10000)
        selected = np.random.choice(
            self.recommendations_data.RECOMMENDATIONS,
            size=6,
            replace=False
        )
        
        return selected.tolist()