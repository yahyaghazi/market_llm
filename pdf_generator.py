"""
Module de génération de rapports PDF professionnels
"""
from reportlab.lib import colors as rl_colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, 
    Paragraph, Spacer, PageBreak, Image
)
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from datetime import datetime
from pathlib import Path
from typing import List, Optional
import numpy as np

from models import MarketAnalysisResult, ProductAnalysis
from config import config, colors
from charts import ChartGenerator


class PDFStyleManager:
    """Gestionnaire de styles pour les documents PDF"""
    
    def __init__(self):
        """Initialiser les styles"""
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()
    
    def _create_custom_styles(self):
        """Créer les styles personnalisés"""
        
        # Titre principal
        self.styles.add(ParagraphStyle(
            name='MainTitle',
            parent=self.styles['Heading1'],
            fontSize=28,
            textColor=rl_colors.HexColor(colors.PRIMARY),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # En-tête de section
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=18,
            textColor=rl_colors.HexColor(colors.PRIMARY),
            spaceAfter=15,
            spaceBefore=20,
            fontName='Helvetica-Bold'
        ))
        
        # Sous-section
        self.styles.add(ParagraphStyle(
            name='SubSection',
            parent=self.styles['Heading3'],
            fontSize=14,
            textColor=rl_colors.HexColor('#6366f1'),
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
            spaceAfter=12,
            leading=16
        ))
        
        # Corps de texte normal
        self.styles.add(ParagraphStyle(
            name='BodyNormal',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=10,
            leading=14
        ))
    
    def get_style(self, name: str) -> ParagraphStyle:
        """Récupérer un style par nom"""
        return self.styles[name]


class TableStyleFactory:
    """Factory pour créer des styles de tableaux cohérents"""
    
    @staticmethod
    def create_header_style(bg_color: str = None) -> TableStyle:
        """Créer un style pour en-tête de tableau"""
        bg_color = bg_color or colors.PRIMARY
        
        return TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), rl_colors.HexColor(bg_color)),
            ('TEXTCOLOR', (0, 0), (-1, 0), rl_colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, rl_colors.black),
        ])
    
    @staticmethod
    def create_data_table_style() -> TableStyle:
        """Créer un style pour tableau de données"""
        base_style = TableStyleFactory.create_header_style()
        base_style.add('BACKGROUND', (0, 1), (-1, -1), rl_colors.HexColor('#f3f4f6'))
        base_style.add('ROWBACKGROUNDS', (0, 1), (-1, -1), 
                      [rl_colors.white, rl_colors.HexColor('#f9fafb')])
        base_style.add('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
        return base_style
    
    @staticmethod
    def create_swot_table_style() -> TableStyle:
        """Créer un style pour tableau SWOT"""
        return TableStyle([
            # En-têtes Forces/Faiblesses
            ('BACKGROUND', (0, 0), (0, 0), rl_colors.HexColor(colors.SUCCESS)),
            ('BACKGROUND', (1, 0), (1, 0), rl_colors.HexColor(colors.DANGER)),
            # En-têtes Opportunités/Menaces
            ('BACKGROUND', (0, 2), (0, 2), rl_colors.HexColor(colors.INFO)),
            ('BACKGROUND', (1, 2), (1, 2), rl_colors.HexColor(colors.WARNING)),
            # Texte des en-têtes en blanc
            ('TEXTCOLOR', (0, 0), (-1, 0), rl_colors.white),
            ('TEXTCOLOR', (0, 2), (-1, 2), rl_colors.white),
            # Alignement et police
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 2), (-1, 2), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            # Bordures
            ('GRID', (0, 0), (-1, -1), 1, rl_colors.black),
            # Arrière-plans des cellules de contenu
            ('BACKGROUND', (0, 1), (-1, 1), rl_colors.HexColor('#f0fdf4')),
            ('BACKGROUND', (0, 3), (-1, 3), rl_colors.HexColor('#fef3c7')),
            # Padding
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ])


class PDFReportGenerator:
    """
    Générateur de rapports PDF professionnels
    
    Crée des documents structurés avec:
    - Page de garde
    - Résumé exécutif
    - Tableaux comparatifs
    - Graphiques
    - Analyses détaillées
    - Recommandations
    """
    
    def __init__(self, output_dir: Path = None):
        """
        Initialiser le générateur
        
        Args:
            output_dir: Dossier de sortie pour les PDFs
        """
        self.output_dir = output_dir or config.REPORTS_DIR
        self.style_manager = PDFStyleManager()
        self.chart_generator = ChartGenerator(self.output_dir)
        self.table_factory = TableStyleFactory()
    
    def generate_report(self, data: MarketAnalysisResult) -> str:
        """
        Génère un rapport PDF complet
        
        Args:
            data: Données d'analyse de marché
            
        Returns:
            str: Nom du fichier PDF généré
        """
        # Générer le nom de fichier
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"etude_marche_{timestamp}.pdf"
        filepath = self.output_dir / filename
        
        print(f"\n{'='*60}")
        print(f"📄 Génération du PDF: {filename}")
        print(f"{'='*60}")
        
        # Générer les graphiques
        print("📊 Génération des graphiques...")
        charts = self.chart_generator.generate_all_charts(data)
        
        # Créer le document
        print("📝 Construction du document...")
        doc = SimpleDocTemplate(
            str(filepath),
            pagesize=A4,
            rightMargin=config.PDF_MARGIN,
            leftMargin=config.PDF_MARGIN,
            topMargin=config.PDF_MARGIN,
            bottomMargin=40
        )
        
        # Construire le contenu
        story = []
        
        print("  ✓ Page de garde")
        story.extend(self._create_cover_page(data))
        story.append(PageBreak())
        
        print("  ✓ Résumé exécutif")
        story.extend(self._create_executive_summary(data))
        story.append(PageBreak())
        
        print("  ✓ Analyse comparative")
        story.extend(self._create_comparison_section(data))
        story.append(PageBreak())
        
        print("  ✓ Graphiques")
        story.extend(self._create_charts_section(data, charts))
        story.append(PageBreak())
        
        print("  ✓ Analyses détaillées")
        story.extend(self._create_detailed_analyses(data))
        
        print("  ✓ Conclusion")
        story.extend(self._create_conclusion(data))
        
        # Générer le PDF
        print("🔨 Build du PDF...")
        doc.build(story)
        
        print(f"{'='*60}")
        print(f"✅ PDF généré avec succès!")
        print(f"📁 Fichier: {filepath}")
        print(f"📊 Taille: {filepath.stat().st_size / 1024:.1f} KB")
        print(f"{'='*60}\n")
        
        return filename
    
    def _create_cover_page(self, data: MarketAnalysisResult) -> List:
        """Créer la page de garde"""
        story = []
        
        story.append(Spacer(1, 2.5*inch))
        
        # Titre principal
        story.append(Paragraph(
            "ÉTUDE DE MARCHÉ COMPLÈTE",
            self.style_manager.get_style('MainTitle')
        ))
        story.append(Spacer(1, 0.3*inch))
        
        story.append(Paragraph(
            data.sector.upper(),
            self.style_manager.get_style('MainTitle')
        ))
        story.append(Spacer(1, 0.8*inch))
        
        # Sous-titre
        story.append(Paragraph(
            f"Analyse Comparative de {len(data.products)} Produits",
            self.style_manager.get_style('SectionHeader')
        ))
        story.append(Spacer(1, 0.2*inch))
        
        story.append(Paragraph(
            f"Rapport généré le {data.analysis_date}",
            self.style_manager.get_style('SubSection')
        ))
        story.append(Spacer(1, 1.5*inch))
        
        # Informations du rapport
        info = f"""
        <b>Secteur analysé:</b> {data.sector}<br/>
        <b>Nombre de produits:</b> {len(data.products)}<br/>
        <b>Date d'analyse:</b> {data.analysis_date}<br/>
        <b>Type de rapport:</b> Analyse Comparative Complète<br/>
        <b>Version:</b> 1.0.0
        """
        story.append(Paragraph(info, self.style_manager.get_style('BodyNormal')))
        
        return story
    
    def _create_executive_summary(self, data: MarketAnalysisResult) -> List:
        """Créer le résumé exécutif"""
        story = []
        
        story.append(Paragraph(
            "RÉSUMÉ EXÉCUTIF", 
            self.style_manager.get_style('SectionHeader')
        ))
        story.append(Spacer(1, 0.2*inch))
        
        story.append(Paragraph(
            data.summary, 
            self.style_manager.get_style('BodyJustified')
        ))
        story.append(Spacer(1, 0.3*inch))
        
        # Statistiques clés
        story.append(Paragraph(
            "Statistiques Clés", 
            self.style_manager.get_style('SubSection')
        ))
        
        avg_satisfaction = np.mean([p.satisfaction for p in data.products])
        avg_growth = np.mean([p.growth for p in data.products])
        total_share = sum([p.market_share for p in data.products])
        
        stats_data = [
            ['Indicateur', 'Valeur'],
            ['Produits analysés', str(len(data.products))],
            ['Satisfaction moyenne', f"{avg_satisfaction:.2f}/5"],
            ['Croissance moyenne', f"{avg_growth:+.1f}%"],
            ['Parts de marché totales', f"{total_share:.1f}%"]
        ]
        
        stats_table = Table(stats_data, colWidths=[3*inch, 2*inch])
        stats_table.setStyle(self.table_factory.create_data_table_style())
        
        story.append(stats_table)
        
        return story
    
    def _create_comparison_section(self, data: MarketAnalysisResult) -> List:
        """Créer la section comparative"""
        story = []
        
        story.append(Paragraph(
            "ANALYSE COMPARATIVE", 
            self.style_manager.get_style('SectionHeader')
        ))
        story.append(Spacer(1, 0.2*inch))
        
        # Tableau comparatif
        table_data = [
            ['Produit', 'Part de\nmarché', 'Prix\nmoyen', 'Satisf.\nclient', 'Crois.\nannuelle']
        ]
        
        for product in data.products:
            table_data.append([
                product.name,
                f"{product.market_share:.1f}%",
                f"{product.price:.0f}€",
                f"{product.satisfaction:.1f}/5",
                f"{product.growth:+.1f}%"
            ])
        
        table = Table(
            table_data, 
            colWidths=[2.2*inch, 1.1*inch, 1.1*inch, 1.1*inch, 1.1*inch]
        )
        table.setStyle(self.table_factory.create_data_table_style())
        
        story.append(table)
        story.append(Spacer(1, 0.3*inch))
        
        # Analyse des résultats
        leader = max(data.products, key=lambda x: x.market_share)
        best_satisfaction = max(data.products, key=lambda x: x.satisfaction)
        best_growth = max(data.products, key=lambda x: x.growth)
        
        analysis_text = f"""
        <b>Points clés de l'analyse comparative:</b><br/>
        • <b>Leader de marché:</b> {leader.name} avec {leader.market_share:.1f}% de parts<br/>
        • <b>Meilleure satisfaction:</b> {best_satisfaction.name} ({best_satisfaction.satisfaction:.1f}/5)<br/>
        • <b>Croissance la plus forte:</b> {best_growth.name} ({best_growth.growth:+.1f}%)<br/>
        • Le tableau révèle une forte hétérogénéité des positionnements prix et performances,
          témoignant de stratégies de marché diversifiées.
        """
        
        story.append(Paragraph(
            analysis_text, 
            self.style_manager.get_style('BodyNormal')
        ))
        
        return story
    
    def _create_charts_section(self, data: MarketAnalysisResult, charts: dict) -> List:
        """Créer la section avec graphiques"""
        story = []
        
        story.append(Paragraph(
            "VISUALISATIONS GRAPHIQUES", 
            self.style_manager.get_style('SectionHeader')
        ))
        story.append(Spacer(1, 0.2*inch))
        
        # Graphique 1: Parts de marché
        if charts['market_share']:
            story.append(Paragraph(
                "Parts de Marché", 
                self.style_manager.get_style('SubSection')
            ))
            story.append(Image(
                str(charts['market_share']), 
                width=5*inch, 
                height=3.5*inch
            ))
            story.append(Spacer(1, 0.3*inch))
        
        # Graphique 2: Prix vs Satisfaction
        if charts['scatter']:
            story.append(Paragraph(
                "Positionnement Prix-Satisfaction", 
                self.style_manager.get_style('SubSection')
            ))
            story.append(Image(
                str(charts['scatter']), 
                width=5*inch, 
                height=3.5*inch
            ))
            story.append(Spacer(1, 0.3*inch))
        
        # Graphique 3: Croissance
        if charts['growth']:
            story.append(Paragraph(
                "Taux de Croissance Annuels", 
                self.style_manager.get_style('SubSection')
            ))
            story.append(Image(
                str(charts['growth']), 
                width=5*inch, 
                height=3.5*inch
            ))
        
        return story
    
    def _create_detailed_analyses(self, data: MarketAnalysisResult) -> List:
        """Créer les analyses détaillées par produit"""
        story = []
        
        for i, product in enumerate(data.products):
            if i > 0:
                story.append(PageBreak())
            
            story.append(Paragraph(
                f"ANALYSE DÉTAILLÉE: {product.name}",
                self.style_manager.get_style('SectionHeader')
            ))
            story.append(Spacer(1, 0.2*inch))
            
            # Indicateurs clés
            metrics_text = f"""
            <b>Part de marché:</b> {product.market_share:.1f}% | 
            <b>Prix moyen:</b> {product.price:.0f}€ | 
            <b>Satisfaction:</b> {product.satisfaction:.1f}/5 | 
            <b>Croissance:</b> {product.growth:+.1f}%
            """
            story.append(Paragraph(
                metrics_text, 
                self.style_manager.get_style('BodyNormal')
            ))
            story.append(Spacer(1, 0.2*inch))
            
            # Tableau SWOT
            story.append(Paragraph(
                "Analyse SWOT", 
                self.style_manager.get_style('SubSection')
            ))
            
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
            swot_table.setStyle(self.table_factory.create_swot_table_style())
            
            story.append(swot_table)
            story.append(Spacer(1, 0.3*inch))
            
            # Positionnement et cible
            story.append(Paragraph(
                "Positionnement et Public Cible", 
                self.style_manager.get_style('SubSection')
            ))
            
            positioning_text = f"""
            <b>Positionnement stratégique:</b><br/>
            {product.positioning}<br/><br/>
            <b>Public cible:</b><br/>
            {product.target_audience}
            """
            story.append(Paragraph(
                positioning_text, 
                self.style_manager.get_style('BodyNormal')
            ))
            story.append(Spacer(1, 0.2*inch))
        
        return story
    
    def _create_conclusion(self, data: MarketAnalysisResult) -> List:
        """Créer la conclusion et les recommandations"""
        story = []
        
        story.append(PageBreak())
        story.append(Paragraph(
            "CONCLUSION ET RECOMMANDATIONS", 
            self.style_manager.get_style('SectionHeader')
        ))
        story.append(Spacer(1, 0.2*inch))
        
        conclusion_text = f"""
        Cette étude de marché comparative du secteur {data.sector} révèle des dynamiques 
        concurrentielles complexes et des opportunités stratégiques significatives. L'analyse 
        détaillée de {len(data.products)} produits majeurs permet d'identifier précisément les forces, 
        faiblesses et positionnements relatifs de chaque acteur. Les insights dégagés constituent 
        une base solide pour l'élaboration de stratégies marketing et commerciales ciblées.
        """
        story.append(Paragraph(
            conclusion_text, 
            self.style_manager.get_style('BodyJustified')
        ))
        story.append(Spacer(1, 0.3*inch))
        
        # Recommandations stratégiques
        story.append(Paragraph(
            "Recommandations Stratégiques", 
            self.style_manager.get_style('SubSection')
        ))
        story.append(Spacer(1, 0.1*inch))
        
        for i, rec in enumerate(data.recommendations, 1):
            rec_text = f"<b>{i}.</b> {rec}"
            story.append(Paragraph(
                rec_text, 
                self.style_manager.get_style('BodyNormal')
            ))
            story.append(Spacer(1, 0.1*inch))
        
        # Note de fin
        story.append(Spacer(1, 0.3*inch))
        footer_text = """
        <i>Note: Cette analyse est basée sur des données de marché actuelles et des projections.
        Les recommandations doivent être adaptées au contexte spécifique de chaque organisation.</i>
        """
        story.append(Paragraph(
            footer_text, 
            self.style_manager.get_style('BodyNormal')
        ))
        
        return story