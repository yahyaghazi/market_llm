"""
Module de génération de graphiques pour les rapports PDF
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from typing import List, Optional

from models import ProductAnalysis, MarketAnalysisResult
from config import config, colors


class ChartGenerator:
    """Générateur de graphiques pour les rapports PDF"""
    
    def __init__(self, output_dir: Path = None):
        """
        Initialiser le générateur de graphiques
        
        Args:
            output_dir: Dossier de sortie pour les graphiques
        """
        self.output_dir = output_dir or config.REPORTS_DIR
        self.colors = colors.CHART_COLORS
        self.dpi = config.CHART_DPI
        self.figsize = (config.CHART_WIDTH, config.CHART_HEIGHT)
    
    def generate_all_charts(self, data: MarketAnalysisResult) -> dict:
        """
        Génère tous les graphiques pour un rapport
        
        Args:
            data: Données d'analyse de marché
            
        Returns:
            dict: Chemins vers les graphiques générés
        """
        return {
            'market_share': self.generate_market_share_chart(data),
            'scatter': self.generate_scatter_chart(data),
            'growth': self.generate_growth_chart(data)
        }
    
    def generate_market_share_chart(self, data: MarketAnalysisResult) -> Optional[Path]:
        """
        Génère un graphique de parts de marché (camembert)
        
        Args:
            data: Données d'analyse de marché
            
        Returns:
            Path: Chemin vers le fichier généré ou None si erreur
        """
        try:
            fig, ax = plt.subplots(figsize=self.figsize)
            
            products = [p.name for p in data.products]
            shares = [p.market_share for p in data.products]
            
            # Créer le camembert
            wedges, texts, autotexts = ax.pie(
                shares,
                labels=products,
                autopct='%1.1f%%',
                colors=self.colors[:len(products)],
                startangle=90,
                textprops={'fontsize': 10}
            )
            
            # Formatter les pourcentages
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
                autotext.set_fontsize(11)
            
            # Formatter les labels
            for text in texts:
                text.set_fontsize(10)
                text.set_fontweight('bold')
            
            plt.title(
                'Répartition des Parts de Marché', 
                fontsize=14, 
                fontweight='bold', 
                pad=20
            )
            
            # Sauvegarder
            path = self.output_dir / 'temp_pie.png'
            plt.savefig(path, dpi=self.dpi, bbox_inches='tight', facecolor='white')
            plt.close()
            
            print(f"✅ Graphique parts de marché généré: {path}")
            return path
            
        except Exception as e:
            print(f"❌ Erreur génération graphique pie: {e}")
            return None
    
    def generate_scatter_chart(self, data: MarketAnalysisResult) -> Optional[Path]:
        """
        Génère un graphique de dispersion prix vs satisfaction
        
        Args:
            data: Données d'analyse de marché
            
        Returns:
            Path: Chemin vers le fichier généré ou None si erreur
        """
        try:
            fig, ax = plt.subplots(figsize=self.figsize)
            
            prices = [p.price for p in data.products]
            satisfactions = [p.satisfaction for p in data.products]
            products = [p.name for p in data.products]
            shares = [p.market_share for p in data.products]
            
            # Taille des bulles proportionnelle à la part de marché
            sizes = [s * 30 for s in shares]
            
            # Créer le scatter plot
            scatter = ax.scatter(
                prices, 
                satisfactions, 
                s=sizes, 
                alpha=0.6, 
                c=range(len(products)), 
                cmap='viridis', 
                edgecolors='black', 
                linewidth=1.5
            )
            
            # Ajouter les annotations
            for i, product in enumerate(products):
                ax.annotate(
                    product, 
                    (prices[i], satisfactions[i]),
                    xytext=(8, 8), 
                    textcoords='offset points',
                    fontsize=9, 
                    fontweight='bold',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.7)
                )
            
            # Lignes de référence
            avg_satisfaction = np.mean(satisfactions)
            avg_price = np.mean(prices)
            
            ax.axhline(
                y=avg_satisfaction, 
                color='red', 
                linestyle='--', 
                alpha=0.4, 
                linewidth=1.5, 
                label=f'Satisfaction moyenne ({avg_satisfaction:.1f})'
            )
            ax.axvline(
                x=avg_price, 
                color='blue', 
                linestyle='--', 
                alpha=0.4, 
                linewidth=1.5,
                label=f'Prix moyen ({avg_price:.0f}€)'
            )
            
            # Quadrants
            ax.text(
                ax.get_xlim()[1] * 0.05, 
                ax.get_ylim()[1] * 0.95, 
                'Premium\nHaute qualité',
                fontsize=9, 
                alpha=0.4, 
                verticalalignment='top'
            )
            
            # Labels et titre
            ax.set_xlabel('Prix (€)', fontsize=12, fontweight='bold')
            ax.set_ylabel('Satisfaction Client (/5)', fontsize=12, fontweight='bold')
            ax.set_title(
                'Positionnement Prix vs Satisfaction', 
                fontsize=14, 
                fontweight='bold', 
                pad=15
            )
            ax.legend(loc='best', framealpha=0.9)
            ax.grid(True, alpha=0.3, linestyle='--')
            
            # Sauvegarder
            path = self.output_dir / 'temp_scatter.png'
            plt.savefig(path, dpi=self.dpi, bbox_inches='tight', facecolor='white')
            plt.close()
            
            print(f"✅ Graphique scatter généré: {path}")
            return path
            
        except Exception as e:
            print(f"❌ Erreur génération graphique scatter: {e}")
            return None
    
    def generate_growth_chart(self, data: MarketAnalysisResult) -> Optional[Path]:
        """
        Génère un graphique de croissance (barres horizontales)
        
        Args:
            data: Données d'analyse de marché
            
        Returns:
            Path: Chemin vers le fichier généré ou None si erreur
        """
        try:
            fig, ax = plt.subplots(figsize=self.figsize)
            
            products = [p.name for p in data.products]
            growth = [p.growth for p in data.products]
            
            # Couleurs conditionnelles (vert si positif, rouge si négatif)
            bar_colors = [colors.SUCCESS if g > 0 else colors.DANGER for g in growth]
            
            # Créer les barres
            bars = ax.barh(
                products, 
                growth, 
                color=bar_colors, 
                alpha=0.7, 
                edgecolor='black', 
                linewidth=1.2
            )
            
            # Ligne de référence zéro
            ax.axvline(x=0, color='black', linestyle='-', linewidth=2, zorder=0)
            
            # Ajouter les valeurs sur les barres
            for bar, value in zip(bars, growth):
                width = bar.get_width()
                label_x = width + (1 if width > 0 else -1)
                
                ax.text(
                    label_x, 
                    bar.get_y() + bar.get_height()/2,
                    f'{value:+.1f}%',
                    ha='left' if value > 0 else 'right',
                    va='center', 
                    fontweight='bold', 
                    fontsize=10,
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8)
                )
            
            # Labels et titre
            ax.set_xlabel('Croissance Annuelle (%)', fontsize=12, fontweight='bold')
            ax.set_title(
                'Taux de Croissance par Produit', 
                fontsize=14, 
                fontweight='bold', 
                pad=15
            )
            ax.grid(True, alpha=0.3, axis='x', linestyle='--')
            
            # Ajuster les marges
            plt.tight_layout()
            
            # Sauvegarder
            path = self.output_dir / 'temp_bar.png'
            plt.savefig(path, dpi=self.dpi, bbox_inches='tight', facecolor='white')
            plt.close()
            
            print(f"✅ Graphique croissance généré: {path}")
            return path
            
        except Exception as e:
            print(f"❌ Erreur génération graphique bar: {e}")
            return None
    
    def cleanup_temp_files(self):
        """Nettoie les fichiers temporaires de graphiques"""
        temp_files = [
            'temp_pie.png',
            'temp_scatter.png',
            'temp_bar.png'
        ]
        
        for filename in temp_files:
            filepath = self.output_dir / filename
            if filepath.exists():
                try:
                    filepath.unlink()
                    print(f"🧹 Fichier temporaire supprimé: {filename}")
                except Exception as e:
                    print(f"⚠️  Impossible de supprimer {filename}: {e}")