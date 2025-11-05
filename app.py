"""
Application Flask - Market Study Generator
API REST pour génération d'études de marché professionnelles
"""
from flask import Flask, request, jsonify, send_file, render_template_string
from flask_cors import CORS
from pydantic import ValidationError
from datetime import datetime
from pathlib import Path
import traceback
from typing import Dict, Any

from config import config
from models import (
    AnalyzeRequest, AnalyzeResponse, ErrorResponse, 
    HealthCheckResponse, ReportsListResponse, ReportInfo
)
from analyzer import MarketAnalyzer
from pdf_generator import PDFReportGenerator


# ============================================================================
# INITIALISATION DE L'APPLICATION
# ============================================================================

app = Flask(__name__)
CORS(app)

# Configuration Flask
app.config['MAX_CONTENT_LENGTH'] = config.MAX_CONTENT_LENGTH
app.debug = config.DEBUG

# Instances des services
analyzer = MarketAnalyzer()
pdf_generator = PDFReportGenerator()


# ============================================================================
# TEMPLATES HTML
# ============================================================================

def get_homepage_html() -> str:
    """Retourne le HTML de la page d'accueil"""
    return """
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Market Study API - Générateur d'Études de Marché</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
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
                max-width: 900px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                animation: fadeIn 0.5s ease-in;
            }
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(20px); }
                to { opacity: 1; transform: translateY(0); }
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
                background: linear-gradient(135deg, #10b981, #059669);
                color: white;
                padding: 10px 20px;
                border-radius: 10px;
                display: inline-block;
                margin-bottom: 30px;
                font-weight: bold;
                box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
            }
            .endpoint {
                background: #f9fafb;
                padding: 20px;
                border-radius: 10px;
                margin-bottom: 15px;
                border-left: 4px solid #4f46e5;
                transition: all 0.3s ease;
            }
            .endpoint:hover {
                background: #f3f4f6;
                transform: translateX(5px);
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
                font-size: 14px;
            }
            .feature {
                display: flex;
                align-items: center;
                margin-bottom: 12px;
                padding: 10px;
                border-radius: 8px;
                transition: background 0.2s;
            }
            .feature:hover {
                background: #f3f4f6;
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
                flex-shrink: 0;
            }
            pre {
                background: #1f2937;
                color: #10b981;
                padding: 15px;
                border-radius: 8px;
                overflow-x: auto;
                margin-top: 10px;
                font-size: 13px;
            }
            .info-box {
                margin-top: 30px;
                padding: 20px;
                background: linear-gradient(135deg, #fef3c7, #fde68a);
                border-radius: 10px;
                border-left: 4px solid #f59e0b;
            }
            .info-box strong {
                color: #92400e;
            }
            h2 {
                margin: 30px 0 20px;
                color: #1f2937;
                font-size: 24px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 Market Study API</h1>
            <p class="subtitle">Génération automatique d'études de marché professionnelles au format PDF</p>
            <div class="status">✓ Service Opérationnel</div>
            
            <h2>✨ Fonctionnalités</h2>
            <div class="feature">Analyse comparative de 2 à 10 produits</div>
            <div class="feature">Génération de rapports PDF structurés</div>
            <div class="feature">3 types de graphiques (parts de marché, prix/satisfaction, croissance)</div>
            <div class="feature">Analyse SWOT complète pour chaque produit</div>
            <div class="feature">Recommandations stratégiques personnalisées</div>
            
            <h2>📡 Endpoints Disponibles</h2>
            
            <div class="endpoint">
                <h3><span class="get">GET</span> /health</h3>
                <p>Vérification de l'état du service (health check)</p>
            </div>
            
            <div class="endpoint">
                <h3><span class="post">POST</span> /api/analyze</h3>
                <p>Génère une analyse de marché complète avec rapport PDF</p>
                <p style="margin-top: 10px;"><strong>Body JSON requis:</strong></p>
                <pre>{
  "products": ["Produit A", "Produit B", "Produit C"],
  "sector": "Nom du Secteur"
}</pre>
                <p style="margin-top: 10px;"><strong>Contraintes:</strong> Min 2 produits, Max 10 produits</p>
            </div>
            
            <div class="endpoint">
                <h3><span class="get">GET</span> /api/download/&lt;filename&gt;</h3>
                <p>Télécharge un rapport PDF spécifique</p>
            </div>
            
            <div class="endpoint">
                <h3><span class="get">GET</span> /api/reports</h3>
                <p>Liste tous les rapports générés disponibles</p>
            </div>
            
            <div class="info-box">
                <strong>📚 Documentation complète:</strong> Consultez le fichier README.md pour des exemples détaillés et le guide d'utilisation complet.
            </div>
        </div>
    </body>
    </html>
    """


# ============================================================================
# ROUTES
# ============================================================================

@app.route('/')
def index():
    """Page d'accueil avec interface HTML"""
    return render_template_string(get_homepage_html())


@app.route('/health')
def health_check():
    """Endpoint de health check"""
    response = HealthCheckResponse(
        status='healthy',
        timestamp=datetime.now().isoformat(),
        version='1.0.0',
        service='Market Study API'
    )
    return jsonify(response.dict()), 200


@app.route('/api/analyze', methods=['POST'])
def analyze_market():
    """
    Endpoint principal d'analyse de marché
    
    Body JSON attendu:
    {
        "products": ["Product 1", "Product 2", ...],
        "sector": "Sector Name"
    }
    
    Returns:
        JSON: Résultat de l'analyse avec lien vers le PDF généré
    """
    try:
        # Récupération et validation des données
        data = request.get_json()
        
        if not data:
            error = ErrorResponse(
                error='Corps JSON requis',
                status_code=400
            )
            return jsonify(error.dict()), 400
        
        try:
            # Validation avec Pydantic
            request_data = AnalyzeRequest(**data)
        except ValidationError as e:
            error = ErrorResponse(
                error='Données invalides',
                details=str(e),
                status_code=400
            )
            return jsonify(error.dict()), 400
        
        # Logging de la requête
        print(f"\n{'='*70}")
        print(f"📊 NOUVELLE ANALYSE DEMANDÉE")
        print(f"{'='*70}")
        print(f"Secteur: {request_data.sector}")
        print(f"Produits ({len(request_data.products)}): {', '.join(request_data.products)}")
        print(f"{'='*70}\n")
        
        # Analyse des produits
        print("🔬 Phase 1: Analyse des produits...")
        analysis_result = analyzer.analyze_products(
            request_data.products, 
            request_data.sector
        )
        
        # Génération du PDF
        print("\n📄 Phase 2: Génération du rapport PDF...")
        pdf_filename = pdf_generator.generate_report(analysis_result)
        
        # Préparer la réponse
        response = AnalyzeResponse(
            success=True,
            pdf_filename=pdf_filename,
            pdf_url=f'/api/download/{pdf_filename}',
            analysis={
                'sector': analysis_result.sector,
                'date': analysis_result.analysis_date,
                'products_count': len(analysis_result.products),
                'products': [
                    {
                        'name': p.name,
                        'market_share': p.market_share,
                        'price': p.price,
                        'satisfaction': p.satisfaction,
                        'growth': p.growth
                    }
                    for p in analysis_result.products
                ],
                'summary': analysis_result.summary
            }
        )
        
        print(f"✅ Analyse terminée avec succès!")
        print(f"📄 PDF disponible: {pdf_filename}")
        print(f"🔗 URL: http://localhost:{config.PORT}{response.pdf_url}\n")
        
        return jsonify(response.dict()), 200
        
    except ValidationError as e:
        print(f"❌ Erreur de validation: {e}")
        error = ErrorResponse(
            error='Erreur de validation des données',
            details=str(e),
            status_code=400
        )
        return jsonify(error.dict()), 400
        
    except Exception as e:
        print(f"❌ ERREUR CRITIQUE: {e}")
        traceback.print_exc()
        
        error = ErrorResponse(
            error='Erreur lors de la génération du rapport',
            details=str(e),
            status_code=500
        )
        return jsonify(error.dict()), 500


@app.route('/api/download/<filename>')
def download_pdf(filename: str):
    """
    Télécharge un rapport PDF
    
    Args:
        filename: Nom du fichier PDF
        
    Returns:
        File: Fichier PDF
    """
    try:
        filepath = config.REPORTS_DIR / filename
        
        # Vérifier l'existence
        if not filepath.exists():
            error = ErrorResponse(
                error='Fichier non trouvé',
                details=f'Le fichier {filename} n\'existe pas',
                status_code=404
            )
            return jsonify(error.dict()), 404
        
        # Sécurité: vérifier que le fichier est bien dans REPORTS_DIR
        if not str(filepath.resolve()).startswith(str(config.REPORTS_DIR.resolve())):
            error = ErrorResponse(
                error='Accès non autorisé',
                details='Tentative d\'accès à un fichier en dehors du dossier autorisé',
                status_code=403
            )
            return jsonify(error.dict()), 403
        
        print(f"📥 Téléchargement: {filename}")
        
        return send_file(
            filepath,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        print(f"❌ Erreur téléchargement: {e}")
        error = ErrorResponse(
            error='Erreur lors du téléchargement',
            details=str(e),
            status_code=500
        )
        return jsonify(error.dict()), 500


@app.route('/api/reports')
def list_reports():
    """
    Liste tous les rapports disponibles
    
    Returns:
        JSON: Liste des rapports avec métadonnées
    """
    try:
        reports = []
        
        for filepath in config.REPORTS_DIR.glob('*.pdf'):
            stat = filepath.stat()
            
            report_info = ReportInfo(
                filename=filepath.name,
                size=stat.st_size,
                created=datetime.fromtimestamp(stat.st_ctime).isoformat(),
                download_url=f'/api/download/{filepath.name}'
            )
            reports.append(report_info)
        
        # Trier par date de création (plus récent en premier)
        reports.sort(key=lambda x: x.created, reverse=True)
        
        response = ReportsListResponse(
            total=len(reports),
            reports=reports
        )
        
        return jsonify(response.dict()), 200
        
    except Exception as e:
        print(f"❌ Erreur liste rapports: {e}")
        error = ErrorResponse(
            error='Erreur lors de la récupération de la liste',
            details=str(e),
            status_code=500
        )
        return jsonify(error.dict()), 500


# ============================================================================
# GESTION D'ERREURS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    """Gestion erreur 404"""
    response = ErrorResponse(
        error='Route non trouvée',
        details=str(error),
        status_code=404
    )
    return jsonify(response.dict()), 404


@app.errorhandler(500)
def internal_error(error):
    """Gestion erreur 500"""
    response = ErrorResponse(
        error='Erreur interne du serveur',
        details=str(error),
        status_code=500
    )
    return jsonify(response.dict()), 500


# ============================================================================
# DÉMARRAGE
# ============================================================================

def print_startup_banner():
    """Affiche la bannière de démarrage"""
    print("\n" + "="*70)
    print(" "*25 + "🚀 MARKET STUDY API")
    print("="*70)
    print(f"\n📦 Version: 1.0.0")
    print(f"📁 Dossier rapports: {config.REPORTS_DIR.absolute()}")
    print(f"📁 Dossier logs: {config.LOGS_DIR.absolute()}")
    print(f"\n🌐 URL: http://localhost:{config.PORT}")
    print(f"📊 Interface: http://localhost:{config.PORT}/")
    print(f"❤️  Health Check: http://localhost:{config.PORT}/health")
    print(f"📚 API Documentation: http://localhost:{config.PORT}/")
    print(f"\n{'='*70}\n")
    print("💡 Appuyez sur Ctrl+C pour arrêter le serveur")
    print("📝 Logs disponibles dans le dossier: logs/\n")


if __name__ == '__main__':
    print_startup_banner()
    
    app.run(
        debug=config.DEBUG, 
        host=config.HOST, 
        port=config.PORT
    )