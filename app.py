"""
Application Flask - Étude de Marché Comparative
Génère des rapports PDF professionnels avec analyses et graphiques
"""

from flask import Flask, request, jsonify, send_file, render_template_string
from flask_cors import CORS
from dataclasses import dataclass
from typing import List, Dict, Optional
import os
from datetime import datetime
from pathlib import Path

# PDF Generation
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, 
    Paragraph, Spacer, PageBreak, Image
)
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY

# Graphiques
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# Configuration
app = Flask(__name__)
CORS(app)

# Dossiers
REPORTS_DIR = Path('reports')
LOGS_DIR = Path('logs')
REPORTS_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# ============================================================================
# MODÈLES DE DONNÉES
# ============================================================================

@dataclass
class ProductAnalysis:
    """Analyse complète d'un produit"""
    name: str
    market_share: float
    price: float
    satisfaction: float
    growth: float
    strengths: List[str]
    weaknesses: List[str]
    opportunities: List[str]
    threats: List[str]
    positioning: str
    target_audience: str

# ============================================================================
# ANALYSEUR (Simulation intelligente)
# ============================================================================

class MarketAnalyzer:
    """Analyseur de marché avec génération de données réalistes"""
    
    @staticmethod
    def analyze_products(products: List[str], sector: str) -> Dict:
        """
        Génère une analyse complète pour plusieurs produits
        En production, cette fonction appellerait un vrai LLM (GPT-4, Claude, etc.)
        """
        print(f"🔍 Analyse de {len(products)} produits dans le secteur: {sector}")
        
        analyses = []
        for product in products:
            analysis = MarketAnalyzer._analyze_single_product(product, sector)
            analyses.append(analysis)
        
        return {
            'sector': sector,
            'analysis_date': datetime.now().strftime('%d/%m/%Y'),
            'products': analyses,
            'summary': MarketAnalyzer._generate_executive_summary(analyses, sector),
            'recommendations': MarketAnalyzer._generate_recommendations(analyses, sector)
        }
    
    @staticmethod
    def _analyze_single_product(product: str, sector: str) -> ProductAnalysis:
        """Analyse un produit individuel"""
        # Seed pour reproductibilité
        np.random.seed(abs(hash(product)) % 10000)
        
        return ProductAnalysis(
            name=product,
            market_share=round(np.random.uniform(5, 35), 2),
            price=round(np.random.uniform(100, 2000), 2),
            satisfaction=round(np.random.uniform(3.0, 4.8), 2),
            growth=round(np.random.uniform(-10, 40), 2),
            strengths=[
                "Innovation technologique constante",
                "Forte reconnaissance de marque",
                "Qualité et fiabilité du produit",
                "Service client de qualité",
                "Réseau de distribution étendu"
            ][:np.random.randint(3, 6)],
            weaknesses=[
                "Prix premium limitant l'accessibilité",
                "Dépendance à certains marchés géographiques",
                "Complexité de l'offre produit",
                "Coûts de production élevés"
            ][:np.random.randint(3, 5)],
            opportunities=[
                "Expansion sur les marchés émergents",
                "Transformation digitale du secteur",
                "Nouveaux segments de clientèle",
                "Partenariats stratégiques",
                "Innovation produit disruptive"
            ][:np.random.randint(3, 6)],
            threats=[
                "Intensification de la concurrence",
                "Évolutions réglementaires strictes",
                "Changements des préférences consommateurs",
                "Instabilité économique globale"
            ][:np.random.randint(3, 5)],
            positioning=f"Leader dans le segment {sector} avec un positionnement premium",
            target_audience=f"Professionnels et particuliers exigeants du secteur {sector}"
        )
    
    @staticmethod
    def _generate_executive_summary(analyses: List[ProductAnalysis], sector: str) -> str:
        """Génère un résumé exécutif"""
        avg_growth = np.mean([a.growth for a in analyses])
        avg_satisfaction = np.mean([a.satisfaction for a in analyses])
        leader = max(analyses, key=lambda x: x.market_share)
        total_market_share = sum([a.market_share for a in analyses])
        
        return f"""Le secteur {sector} montre une dynamique {'positive' if avg_growth > 0 else 'contrastée'} 
avec une croissance moyenne de {avg_growth:.1f}%. {leader.name} domine le marché avec 
{leader.market_share:.1f}% de parts. La satisfaction client moyenne s'établit à 
{avg_satisfaction:.1f}/5, reflétant une bonne perception globale. Les {len(analyses)} produits 
analysés représentent {total_market_share:.1f}% du marché total. L'analyse révèle des 
opportunités significatives dans la transformation digitale et l'innovation produit."""
    
    @staticmethod
    def _generate_recommendations(analyses: List[ProductAnalysis], sector: str) -> List[str]:
        """Génère des recommandations stratégiques"""
        return [
            "Investir dans l'innovation pour maintenir l'avantage concurrentiel",
            "Renforcer la présence sur les canaux digitaux",
            "Explorer les opportunités d'expansion géographique",
            "Optimiser la structure de coûts pour améliorer la rentabilité",
            "Développer des partenariats stratégiques dans l'écosystème",
            "Améliorer l'expérience client à tous les points de contact"
        ]

# ============================================================================
# GÉNÉRATEUR PDF
# ============================================================================

class PDFReportGenerator:
    """Génère des rapports PDF professionnels"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Configure les styles personnalisés"""
        # Titre principal
        self.styles.add(ParagraphStyle(
            name='MainTitle',
            parent=self.styles['Heading1'],
            fontSize=28,
            textColor=colors.HexColor('#1e40af'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # En-tête de section
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=18,
            textColor=colors.HexColor('#4f46e5'),
            spaceAfter=15,
            spaceBefore=20,
            fontName='Helvetica-Bold'
        ))
        
        # Sous-section
        self.styles.add(ParagraphStyle(
            name='SubSection',
            parent=self.styles['Heading3'],
            fontSize=14,
            textColor=colors.HexColor('#6366f1'),
            spaceAfter=10,
            spaceBefore=15,
            fontName='Helvetica-Bold'
        ))
        
        # Corps de texte justifié
        self.styles.add(ParagraphStyle(
            name='BodyJustified',
            parent=self.styles['Normal'],
            fontSize=11,
            alignment=TA_JUSTIFY,
            spaceAfter=12
        ))
    
    def generate_report(self, data: Dict) -> str:
        """Génère le rapport PDF complet"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"etude_marche_{timestamp}.pdf"
        filepath = REPORTS_DIR / filename
        
        print(f"📄 Génération du PDF: {filename}")
        
        doc = SimpleDocTemplate(
            str(filepath),
            pagesize=A4,
            rightMargin=60,
            leftMargin=60,
            topMargin=60,
            bottomMargin=40
        )
        
        story = []
        
        # Construction du document
        story.extend(self._create_cover_page(data))
        story.append(PageBreak())
        
        story.extend(self._create_executive_summary(data))
        story.append(PageBreak())
        
        story.extend(self._create_comparison_section(data))
        story.append(PageBreak())
        
        story.extend(self._create_charts_section(data))
        story.append(PageBreak())
        
        story.extend(self._create_detailed_analyses(data))
        
        story.extend(self._create_conclusion(data))
        
        # Build du PDF
        doc.build(story)
        
        print(f"✅ PDF généré avec succès: {filepath}")
        return filename
    
    def _create_cover_page(self, data: Dict) -> List:
        """Page de garde"""
        story = []
        
        story.append(Spacer(1, 2.5*inch))
        
        # Titre
        story.append(Paragraph(
            f"ÉTUDE DE MARCHÉ COMPLÈTE",
            self.styles['MainTitle']
        ))
        story.append(Spacer(1, 0.3*inch))
        
        story.append(Paragraph(
            f"{data['sector'].upper()}",
            self.styles['MainTitle']
        ))
        story.append(Spacer(1, 0.8*inch))
        
        # Sous-titre
        story.append(Paragraph(
            f"Analyse Comparative de {len(data['products'])} Produits",
            self.styles['Heading2']
        ))
        story.append(Spacer(1, 0.2*inch))
        
        story.append(Paragraph(
            f"Rapport généré le {data['analysis_date']}",
            self.styles['Heading3']
        ))
        story.append(Spacer(1, 1.5*inch))
        
        # Informations
        info = f"""
        <b>Secteur analysé:</b> {data['sector']}<br/>
        <b>Nombre de produits:</b> {len(data['products'])}<br/>
        <b>Date d'analyse:</b> {data['analysis_date']}<br/>
        <b>Type de rapport:</b> Analyse Comparative Complète
        """
        story.append(Paragraph(info, self.styles['Normal']))
        
        return story
    
    def _create_executive_summary(self, data: Dict) -> List:
        """Résumé exécutif"""
        story = []
        
        story.append(Paragraph("RÉSUMÉ EXÉCUTIF", self.styles['SectionHeader']))
        story.append(Spacer(1, 0.2*inch))
        
        story.append(Paragraph(data['summary'], self.styles['BodyJustified']))
        story.append(Spacer(1, 0.3*inch))
        
        # Statistiques clés
        story.append(Paragraph("Statistiques Clés", self.styles['SubSection']))
        
        products = data['products']
        stats_data = [
            ['Indicateur', 'Valeur'],
            ['Produits analysés', str(len(products))],
            ['Satisfaction moyenne', f"{np.mean([p.satisfaction for p in products]):.2f}/5"],
            ['Croissance moyenne', f"{np.mean([p.growth for p in products]):+.1f}%"],
            ['Parts de marché totales', f"{sum([p.market_share for p in products]):.1f}%"]
        ]
        
        stats_table = Table(stats_data, colWidths=[3*inch, 2*inch])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4f46e5')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f3f4f6')),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), 
             [colors.white, colors.HexColor('#f9fafb')])
        ]))
        
        story.append(stats_table)
        
        return story
    
    def _create_comparison_section(self, data: Dict) -> List:
        """Section comparative"""
        story = []
        
        story.append(Paragraph("ANALYSE COMPARATIVE", self.styles['SectionHeader']))
        story.append(Spacer(1, 0.2*inch))
        
        # Tableau comparatif
        table_data = [
            ['Produit', 'Part\nde marché', 'Prix\nmoyen', 'Satisf.\nclient', 'Crois.\nannuelle']
        ]
        
        for product in data['products']:
            table_data.append([
                product.name,
                f"{product.market_share:.1f}%",
                f"{product.price:.0f}€",
                f"{product.satisfaction:.1f}/5",
                f"{product.growth:+.1f}%"
            ])
        
        table = Table(table_data, colWidths=[2.2*inch, 1.1*inch, 1.1*inch, 1.1*inch, 1.1*inch])
        
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4f46e5')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), 
             [colors.white, colors.HexColor('#f3f4f6')])
        ]))
        
        story.append(table)
        story.append(Spacer(1, 0.3*inch))
        
        # Analyse du tableau
        leader = max(data['products'], key=lambda x: x.market_share)
        best_satisfaction = max(data['products'], key=lambda x: x.satisfaction)
        best_growth = max(data['products'], key=lambda x: x.growth)
        
        analysis_text = f"""
        <b>Points clés de l'analyse comparative:</b><br/>
        • <b>Leader de marché:</b> {leader.name} avec {leader.market_share:.1f}% de parts<br/>
        • <b>Meilleure satisfaction:</b> {best_satisfaction.name} ({best_satisfaction.satisfaction:.1f}/5)<br/>
        • <b>Croissance la plus forte:</b> {best_growth.name} ({best_growth.growth:+.1f}%)<br/>
        • Le tableau révèle une forte hétérogénéité des positionnements prix et performances
        """
        
        story.append(Paragraph(analysis_text, self.styles['Normal']))
        
        return story
    
    def _create_charts_section(self, data: Dict) -> List:
        """Section avec graphiques"""
        story = []
        
        story.append(Paragraph("VISUALISATIONS GRAPHIQUES", self.styles['SectionHeader']))
        story.append(Spacer(1, 0.2*inch))
        
        # Graphique 1: Parts de marché
        chart1_path = self._generate_market_share_chart(data)
        if chart1_path:
            story.append(Paragraph("Parts de Marché", self.styles['SubSection']))
            story.append(Image(str(chart1_path), width=5*inch, height=3.5*inch))
            story.append(Spacer(1, 0.3*inch))
        
        # Graphique 2: Prix vs Satisfaction
        chart2_path = self._generate_scatter_chart(data)
        if chart2_path:
            story.append(Paragraph("Positionnement Prix-Satisfaction", self.styles['SubSection']))
            story.append(Image(str(chart2_path), width=5*inch, height=3.5*inch))
            story.append(Spacer(1, 0.3*inch))
        
        # Graphique 3: Croissance
        chart3_path = self._generate_growth_chart(data)
        if chart3_path:
            story.append(Paragraph("Taux de Croissance Annuels", self.styles['SubSection']))
            story.append(Image(str(chart3_path), width=5*inch, height=3.5*inch))
        
        return story
    
    def _create_detailed_analyses(self, data: Dict) -> List:
        """Analyses détaillées par produit"""
        story = []
        
        for i, product in enumerate(data['products']):
            if i > 0:
                story.append(PageBreak())
            
            story.append(Paragraph(
                f"ANALYSE DÉTAILLÉE: {product.name}",
                self.styles['SectionHeader']
            ))
            story.append(Spacer(1, 0.2*inch))
            
            # Indicateurs clés
            metrics_text = f"""
            <b>Part de marché:</b> {product.market_share:.1f}% | 
            <b>Prix moyen:</b> {product.price:.0f}€ | 
            <b>Satisfaction:</b> {product.satisfaction:.1f}/5 | 
            <b>Croissance:</b> {product.growth:+.1f}%
            """
            story.append(Paragraph(metrics_text, self.styles['Normal']))
            story.append(Spacer(1, 0.2*inch))
            
            # SWOT
            story.append(Paragraph("Analyse SWOT", self.styles['SubSection']))
            
            swot_data = [
                ['FORCES', 'FAIBLESSES'],
                [
                    '\n'.join([f"• {s}" for s in product.strengths]),
                    '\n'.join([f"• {w}" for w in product.weaknesses])
                ],
                ['OPPORTUNITÉS', 'MENACES'],
                [
                    '\n'.join([f"• {o}" for o in product.opportunities]),
                    '\n'.join([f"• {t}" for t in product.threats])
                ]
            ]
            
            swot_table = Table(swot_data, colWidths=[3*inch, 3*inch])
            swot_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, 0), colors.HexColor('#10b981')),
                ('BACKGROUND', (1, 0), (1, 0), colors.HexColor('#ef4444')),
                ('BACKGROUND', (0, 2), (0, 2), colors.HexColor('#3b82f6')),
                ('BACKGROUND', (1, 2), (1, 2), colors.HexColor('#f59e0b')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('TEXTCOLOR', (0, 2), (-1, 2), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 2), (-1, 2), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#f0fdf4')),
                ('BACKGROUND', (0, 3), (-1, 3), colors.HexColor('#fef3c7')),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8)
            ]))
            
            story.append(swot_table)
            story.append(Spacer(1, 0.3*inch))
            
            # Positionnement
            story.append(Paragraph("Positionnement et Cible", self.styles['SubSection']))
            positioning_text = f"""
            <b>Positionnement:</b> {product.positioning}<br/>
            <b>Public cible:</b> {product.target_audience}
            """
            story.append(Paragraph(positioning_text, self.styles['Normal']))
            story.append(Spacer(1, 0.2*inch))
        
        return story
    
    def _create_conclusion(self, data: Dict) -> List:
        """Conclusion et recommandations"""
        story = []
        
        story.append(PageBreak())
        story.append(Paragraph("CONCLUSION ET RECOMMANDATIONS", self.styles['SectionHeader']))
        story.append(Spacer(1, 0.2*inch))
        
        conclusion_text = f"""
        Cette étude de marché comparative du secteur {data['sector']} révèle des dynamiques 
        concurrentielles complexes et des opportunités stratégiques significatives. L'analyse 
        détaillée de {len(data['products'])} produits majeurs permet d'identifier les forces, 
        faiblesses et positionnements relatifs de chaque acteur.
        """
        story.append(Paragraph(conclusion_text, self.styles['BodyJustified']))
        story.append(Spacer(1, 0.3*inch))
        
        # Recommandations
        story.append(Paragraph("Recommandations Stratégiques", self.styles['SubSection']))
        
        for i, rec in enumerate(data['recommendations'], 1):
            story.append(Paragraph(f"{i}. {rec}", self.styles['Normal']))
            story.append(Spacer(1, 0.1*inch))
        
        return story
    
    def _generate_market_share_chart(self, data: Dict) -> Optional[Path]:
        """Génère un graphique de parts de marché"""
        try:
            fig, ax = plt.subplots(figsize=(10, 7))
            
            products = [p.name for p in data['products']]
            shares = [p.market_share for p in data['products']]
            colors_list = ['#4f46e5', '#7c3aed', '#ec4899', '#f59e0b', '#10b981', '#06b6d4']
            
            wedges, texts, autotexts = ax.pie(
                shares,
                labels=products,
                autopct='%1.1f%%',
                colors=colors_list[:len(products)],
                startangle=90,
                textprops={'fontsize': 10}
            )
            
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
            
            plt.title('Répartition des Parts de Marché', 
                     fontsize=14, fontweight='bold', pad=20)
            
            path = REPORTS_DIR / 'temp_pie.png'
            plt.savefig(path, dpi=150, bbox_inches='tight')
            plt.close()
            
            return path
        except Exception as e:
            print(f"Erreur génération graphique pie: {e}")
            return None
    
    def _generate_scatter_chart(self, data: Dict) -> Optional[Path]:
        """Génère un graphique de dispersion prix vs satisfaction"""
        try:
            fig, ax = plt.subplots(figsize=(10, 7))
            
            prices = [p.price for p in data['products']]
            satisfactions = [p.satisfaction for p in data['products']]
            products = [p.name for p in data['products']]
            shares = [p.market_share for p in data['products']]
            
            # Taille des bulles proportionnelle à la part de marché
            sizes = [s * 30 for s in shares]
            
            scatter = ax.scatter(prices, satisfactions, s=sizes, 
                               alpha=0.6, c=range(len(products)), 
                               cmap='viridis', edgecolors='black', linewidth=1.5)
            
            # Annotations
            for i, product in enumerate(products):
                ax.annotate(product, (prices[i], satisfactions[i]),
                          xytext=(8, 8), textcoords='offset points',
                          fontsize=9, fontweight='bold')
            
            # Lignes de référence
            ax.axhline(y=np.mean(satisfactions), color='red', 
                      linestyle='--', alpha=0.4, linewidth=1, 
                      label='Satisfaction moyenne')
            ax.axvline(x=np.mean(prices), color='blue', 
                      linestyle='--', alpha=0.4, linewidth=1,
                      label='Prix moyen')
            
            ax.set_xlabel('Prix (€)', fontsize=12, fontweight='bold')
            ax.set_ylabel('Satisfaction Client (/5)', fontsize=12, fontweight='bold')
            ax.set_title('Positionnement Prix vs Satisfaction', 
                        fontsize=14, fontweight='bold', pad=15)
            ax.legend(loc='best')
            ax.grid(True, alpha=0.3)
            
            path = REPORTS_DIR / 'temp_scatter.png'
            plt.savefig(path, dpi=150, bbox_inches='tight')
            plt.close()
            
            return path
        except Exception as e:
            print(f"Erreur génération graphique scatter: {e}")
            return None
    
    def _generate_growth_chart(self, data: Dict) -> Optional[Path]:
        """Génère un graphique de croissance"""
        try:
            fig, ax = plt.subplots(figsize=(10, 7))
            
            products = [p.name for p in data['products']]
            growth = [p.growth for p in data['products']]
            colors_list = ['#10b981' if g > 0 else '#ef4444' for g in growth]
            
            bars = ax.barh(products, growth, color=colors_list, 
                          alpha=0.7, edgecolor='black', linewidth=1.2)
            
            # Ligne de référence zéro
            ax.axvline(x=0, color='black', linestyle='-', linewidth=1.5)
            
            # Valeurs sur les barres
            for bar, value in zip(bars, growth):
                width = bar.get_width()
                ax.text(width, bar.get_y() + bar.get_height()/2,
                       f' {value:+.1f}%',
                       ha='left' if value > 0 else 'right',
                       va='center', fontweight='bold', fontsize=10)
            
            ax.set_xlabel('Croissance Annuelle (%)', fontsize=12, fontweight='bold')
            ax.set_title('Taux de Croissance par Produit', 
                        fontsize=14, fontweight='bold', pad=15)
            ax.grid(True, alpha=0.3, axis='x')
            
            path = REPORTS_DIR / 'temp_bar.png'
            plt.savefig(path, dpi=150, bbox_inches='tight')
            plt.close()
            
            return path
        except Exception as e:
            print(f"Erreur génération graphique bar: {e}")
            return None

# ============================================================================
# ROUTES FLASK
# ============================================================================

@app.route('/')
def index():
    """Page d'accueil avec interface HTML"""
    html = """
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Étude de Marché - API</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 20px;
            }
            .container {
                background: white;
                border-radius: 20px;
                padding: 40px;
                max-width: 800px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            }
            h1 {
                color: #4f46e5;
                margin-bottom: 10px;
                font-size: 32px;
            }
            .subtitle {
                color: #6b7280;
                margin-bottom: 30px;
                font-size: 16px;
            }
            .status {
                background: #10b981;
                color: white;
                padding: 10px 20px;
                border-radius: 10px;
                display: inline-block;
                margin-bottom: 30px;
                font-weight: bold;
            }
            .endpoint {
                background: #f3f4f6;
                padding: 20px;
                border-radius: 10px;
                margin-bottom: 15px;
                border-left: 4px solid #4f46e5;
            }
            .endpoint h3 {
                color: #4f46e5;
                margin-bottom: 8px;
                font-size: 18px;
            }
            .method {
                display: inline-block;
                padding: 4px 12px;
                border-radius: 6px;
                font-size: 12px;
                font-weight: bold;
                margin-right: 10px;
            }
            .post { background: #10b981; color: white; }
            .get { background: #3b82f6; color: white; }
            code {
                background: #1f2937;
                color: #10b981;
                padding: 2px 8px;
                border-radius: 4px;
                font-family: 'Courier New', monospace;
            }
            .feature {
                display: flex;
                align-items: center;
                margin-bottom: 12px;
            }
            .feature::before {
                content: "✓";
                background: #10b981;
                color: white;
                width: 24px;
                height: 24px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                margin-right: 12px;
                font-weight: bold;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 API Étude de Marché</h1>
            <p class="subtitle">Génération automatique de rapports PDF professionnels</p>
            <div class="status">✓ Service Opérationnel</div>
            
            <h2 style="margin-bottom: 20px; color: #1f2937;">Fonctionnalités</h2>
            <div class="feature">Analyse comparative multi-produits</div>
            <div class="feature">Génération de graphiques professionnels</div>
            <div class="feature">Rapports PDF structurés et détaillés</div>
            <div class="feature">Analyse SWOT complète</div>
            
            <h2 style="margin: 30px 0 20px; color: #1f2937;">Endpoints Disponibles</h2>
            
            <div class="endpoint">
                <h3><span class="get">GET</span> /health</h3>
                <p>Vérification de l'état du service</p>
            </div>
            
            <div class="endpoint">
                <h3><span class="post">POST</span> /api/analyze</h3>
                <p>Génère une analyse de marché complète</p>
                <p style="margin-top: 10px;"><strong>Body JSON:</strong></p>
                <pre style="background: #1f2937; color: #10b981; padding: 15px; border-radius: 8px; overflow-x: auto; margin-top: 10px;">
{
  "products": ["Produit A", "Produit B", "Produit C"],
  "sector": "Votre Secteur"
}</pre>
            </div>
            
            <div class="endpoint">
                <h3><span class="get">GET</span> /api/download/&lt;filename&gt;</h3>
                <p>Télécharge un rapport PDF généré</p>
            </div>
            
            <div style="margin-top: 30px; padding: 20px; background: #fef3c7; border-radius: 10px; border-left: 4px solid #f59e0b;">
                <strong>📚 Documentation:</strong> Consultez le README pour des exemples détaillés
            </div>
        </div>
    </body>
    </html>
    """
    return html

@app.route('/health')
def health_check():
    """Vérification de santé du service"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0',
        'service': 'Market Study API'
    })

@app.route('/api/analyze', methods=['POST'])
def analyze_market():
    """
    Endpoint principal d'analyse de marché
    
    Expected JSON Body:
    {
        "products": ["Product 1", "Product 2", ...],
        "sector": "Sector Name"
    }
    """
    try:
        # Récupération des données
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Corps JSON requis'}), 400
        
        products = data.get('products', [])
        sector = data.get('sector', '')
        
        # Validation
        if not products or not isinstance(products, list):
            return jsonify({'error': 'Le champ "products" doit être une liste non vide'}), 400
        
        if len(products) < 2:
            return jsonify({'error': 'Au moins 2 produits sont requis'}), 400
        
        if len(products) > 10:
            return jsonify({'error': 'Maximum 10 produits autorisés'}), 400
        
        if not sector or not isinstance(sector, str):
            return jsonify({'error': 'Le champ "sector" est requis'}), 400
        
        # Nettoyer les données
        products = [p.strip() for p in products if p.strip()]
        sector = sector.strip()
        
        if len(products) < 2:
            return jsonify({'error': 'Au moins 2 produits valides requis après nettoyage'}), 400
        
        print(f"\n{'='*60}")
        print(f"📊 NOUVELLE ANALYSE DEMANDÉE")
        print(f"{'='*60}")
        print(f"Secteur: {sector}")
        print(f"Produits ({len(products)}): {', '.join(products)}")
        print(f"{'='*60}\n")
        
        # Analyse
        analyzer = MarketAnalyzer()
        analysis_data = analyzer.analyze_products(products, sector)
        
        # Génération PDF
        pdf_generator = PDFReportGenerator()
        filename = pdf_generator.generate_report(analysis_data)
        
        # Préparer la réponse
        response_data = {
            'success': True,
            'pdf_filename': filename,
            'pdf_url': f'/api/download/{filename}',
            'analysis': {
                'sector': analysis_data['sector'],
                'date': analysis_data['analysis_date'],
                'products_count': len(analysis_data['products']),
                'products': [
                    {
                        'name': p.name,
                        'market_share': p.market_share,
                        'price': p.price,
                        'satisfaction': p.satisfaction,
                        'growth': p.growth
                    }
                    for p in analysis_data['products']
                ],
                'summary': analysis_data['summary']
            }
        }
        
        print(f"✅ Analyse terminée avec succès!")
        print(f"📄 PDF: {filename}\n")
        
        return jsonify(response_data), 200
        
    except Exception as e:
        print(f"❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'error': 'Erreur lors de la génération du rapport',
            'details': str(e)
        }), 500

@app.route('/api/download/<filename>')
def download_pdf(filename):
    """Télécharge un rapport PDF"""
    try:
        filepath = REPORTS_DIR / filename
        
        if not filepath.exists():
            return jsonify({'error': 'Fichier non trouvé'}), 404
        
        # Sécurité: vérifier que le fichier est bien dans REPORTS_DIR
        if not str(filepath.resolve()).startswith(str(REPORTS_DIR.resolve())):
            return jsonify({'error': 'Accès non autorisé'}), 403
        
        return send_file(
            filepath,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        print(f"Erreur téléchargement: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/reports')
def list_reports():
    """Liste tous les rapports générés"""
    try:
        reports = []
        for filepath in REPORTS_DIR.glob('*.pdf'):
            stat = filepath.stat()
            reports.append({
                'filename': filepath.name,
                'size': stat.st_size,
                'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                'download_url': f'/api/download/{filepath.name}'
            })
        
        # Trier par date de création (plus récent en premier)
        reports.sort(key=lambda x: x['created'], reverse=True)
        
        return jsonify({
            'total': len(reports),
            'reports': reports
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================================
# DÉMARRAGE DE L'APPLICATION
# ============================================================================

if __name__ == '__main__':
    print("\n" + "="*70)
    print(" "*20 + "🚀 MARKET STUDY API")
    print("="*70)
    print(f"\n📁 Dossier des rapports: {REPORTS_DIR.absolute()}")
    print(f"📁 Dossier des logs: {LOGS_DIR.absolute()}")
    print(f"\n🌐 URL: http://localhost:5000")
    print(f"📊 Interface: http://localhost:5000/")
    print(f"❤️  Health Check: http://localhost:5000/health")
    print(f"\n{'='*70}\n")
    print("💡 Appuyez sur Ctrl+C pour arrêter le serveur\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)