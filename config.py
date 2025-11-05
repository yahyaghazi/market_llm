"""
Configuration centralisée de l'application Market Study
"""
from pathlib import Path
from dataclasses import dataclass
from typing import List


@dataclass
class AppConfig:
    """Configuration principale de l'application"""
    
    # Dossiers
    REPORTS_DIR: Path = Path('reports')
    LOGS_DIR: Path = Path('logs')
    
    # Flask
    DEBUG: bool = True
    HOST: str = '0.0.0.0'
    PORT: int = 5000
    MAX_CONTENT_LENGTH: int = 16 * 1024 * 1024  # 16MB
    
    # Limites de validation
    MIN_PRODUCTS: int = 2
    MAX_PRODUCTS: int = 10
    
    # Graphiques
    CHART_DPI: int = 150
    CHART_WIDTH: int = 10
    CHART_HEIGHT: int = 7
    
    # PDF
    PDF_PAGE_SIZE: tuple = (595.27, 841.89)  # A4
    PDF_MARGIN: int = 60
    
    def __post_init__(self):
        """Créer les dossiers nécessaires"""
        self.REPORTS_DIR.mkdir(exist_ok=True)
        self.LOGS_DIR.mkdir(exist_ok=True)


@dataclass
class Colors:
    """Palette de couleurs pour les graphiques et PDF"""
    
    # Couleurs principales
    PRIMARY: str = '#4f46e5'
    SECONDARY: str = '#7c3aed'
    SUCCESS: str = '#10b981'
    WARNING: str = '#f59e0b'
    DANGER: str = '#ef4444'
    INFO: str = '#3b82f6'
    
    # Couleurs graphiques
    CHART_COLORS: List[str] = None
    
    def __post_init__(self):
        self.CHART_COLORS = [
            '#4f46e5', '#7c3aed', '#ec4899', 
            '#f59e0b', '#10b981', '#06b6d4'
        ]


@dataclass
class SWOTData:
    """Données prédéfinies pour l'analyse SWOT"""
    
    STRENGTHS: List[str] = None
    WEAKNESSES: List[str] = None
    OPPORTUNITIES: List[str] = None
    THREATS: List[str] = None
    
    def __post_init__(self):
        self.STRENGTHS = [
            "Innovation technologique constante",
            "Forte reconnaissance de marque",
            "Qualité et fiabilité du produit",
            "Service client de qualité supérieure",
            "Réseau de distribution étendu",
            "Expertise technique reconnue",
            "Chaîne d'approvisionnement robuste",
            "Investissements R&D conséquents"
        ]
        
        self.WEAKNESSES = [
            "Prix premium limitant l'accessibilité",
            "Dépendance à certains marchés géographiques",
            "Complexité de l'offre produit",
            "Coûts de production élevés",
            "Cycle de développement long",
            "Dépendance aux fournisseurs clés",
            "Canaux de distribution limités"
        ]
        
        self.OPPORTUNITIES = [
            "Expansion sur les marchés émergents",
            "Transformation digitale du secteur",
            "Nouveaux segments de clientèle",
            "Partenariats stratégiques",
            "Innovation produit disruptive",
            "Évolution des comportements consommateurs",
            "Consolidation du marché",
            "Nouvelles technologies disponibles"
        ]
        
        self.THREATS = [
            "Intensification de la concurrence",
            "Évolutions réglementaires strictes",
            "Changements des préférences consommateurs",
            "Instabilité économique globale",
            "Disruption technologique",
            "Pression sur les marges",
            "Volatilité des matières premières",
            "Risques géopolitiques"
        ]


@dataclass
class RecommendationsData:
    """Recommandations stratégiques prédéfinies"""
    
    RECOMMENDATIONS: List[str] = None
    
    def __post_init__(self):
        self.RECOMMENDATIONS = [
            "Investir massivement dans l'innovation pour maintenir l'avantage concurrentiel",
            "Renforcer la présence sur les canaux digitaux et e-commerce",
            "Explorer activement les opportunités d'expansion géographique",
            "Optimiser la structure de coûts pour améliorer la rentabilité opérationnelle",
            "Développer des partenariats stratégiques dans l'écosystème",
            "Améliorer l'expérience client à tous les points de contact",
            "Diversifier le portefeuille produit pour réduire les risques",
            "Accélérer la transformation digitale des opérations"
        ]


# Instances globales
config = AppConfig()
colors = Colors()
swot_data = SWOTData()
recommendations_data = RecommendationsData()