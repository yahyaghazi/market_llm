"""
Application Flask - Market Study Generator avec Ollama
API REST pour génération d'études de marché avec LLM local
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
from ollama_analyzer import OllamaMarketAnalyzer, OllamaConfig
from pdf_generator import PDFReportGenerator


# ============================================================================
# INITIALISATION DE L'APPLICATION
# ============================================================================

app = Flask(__name__)
CORS(app)

# Configuration Flask
app.config['MAX_CONTENT_LENGTH'] = config.MAX_CONTENT_LENGTH
app.debug = config.DEBUG

# Instances des services (Ollama par défaut avec fallback simulation)
pdf_generator = PDFReportGenerator()


# ============================================================================
# GESTION ANALYSEUR (Ollama ou Simulation)
# ============================================================================

def get_analyzer(
    use_ollama: bool = True,
    model: str = None,
    temperature: float = None,
    top_p: float = None,
    max_tokens: int = None,
    **kwargs
) -> OllamaMarketAnalyzer:
    """
    Crée un analyseur avec la configuration demandée
    
    Args:
        use_ollama: Utiliser Ollama (sinon fallback simulation)
        model: Nom du modèle Ollama
        temperature: Température (0-2)
        top_p: Top-P (0-1)
        max_tokens: Nombre max de tokens
        **kwargs: Autres paramètres Ollama
        
    Returns:
        OllamaMarketAnalyzer configuré
    """
    if not use_ollama:
        # Mode simulation pure
        ollama_config = OllamaConfig()
        return OllamaMarketAnalyzer(
            ollama_config=ollama_config,
            fallback_to_simulation=True
        )
    
    # Configuration Ollama personnalisée
    ollama_config = OllamaConfig(
        model=model or "gemma3:4b",
        temperature=temperature if temperature is not None else 0.7,
        top_p=top_p if top_p is not None else 0.9,
        max_tokens=max_tokens or 2000,
        **kwargs
    )
    
    return OllamaMarketAnalyzer(
        ollama_config=ollama_config,
        fallback_to_simulation=True  # Toujours avec fallback pour robustesse
    )


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
        <title>Market Study API - Ollama Edition</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            .container {
                background: white;
                border-radius: 20px;
                padding: 40px;
                max-width: 1000px;
                margin: 0 auto;
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
            .badge {
                display: inline-block;
                padding: 8px 16px;
                border-radius: 20px;
                font-size: 14px;
                font-weight: bold;
                margin-bottom: 20px;
            }
            .badge-ollama {
                background: linear-gradient(135deg, #10b981, #059669);
                color: white;
            }
            .badge-status {
                background: linear-gradient(135deg, #3b82f6, #2563eb);
                color: white;
            }
            .endpoint {
                background: #f9fafb;
                padding: 20px;
                border-radius: 10px;
                margin-bottom: 15px;
                border-left: 4px solid #4f46e5;
            }
            .endpoint h3 {
                color: #4f46e5;
                margin-bottom: 8px;
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
            pre {
                background: #1f2937;
                color: #10b981;
                padding: 15px;
                border-radius: 8px;
                overflow-x: auto;
                margin-top: 10px;
                font-size: 13px;
            }
            .config-section {
                background: #fef3c7;
                padding: 20px;
                border-radius: 10px;
                margin: 20px 0;
                border-left: 4px solid #f59e0b;
            }
            .config-section h3 {
                color: #92400e;
                margin-bottom: 10px;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 10px;
            }
            th, td {
                padding: 10px;
                text-align: left;
                border-bottom: 1px solid #e5e7eb;
            }
            th {
                background: #f3f4f6;
                font-weight: bold;
                color: #374151;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 Market Study API - Ollama Edition</h1>
            <p class="subtitle">Études de marché avec DeepSeek-R1 (ou autre LLM local)</p>
            
            <span class="badge badge-ollama">✓ Ollama Ready</span>
            <span class="badge badge-status">✓ Service Actif</span>
            
            <h2 style="margin-top: 30px; color: #1f2937;">🚀 Nouveautés v2.1</h2>
            <ul style="margin: 15px 0 15px 30px; line-height: 1.8;">
                <li><strong>LLM Local:</strong> DeepSeek-R1, Llama 3, Mistral, etc.</li>
                <li><strong>Hyperparamètres:</strong> temperature, top_p, max_tokens configurables</li>
                <li><strong>Fallback automatique:</strong> Simulation si Ollama indisponible</li>
                <li><strong>Analyses réelles:</strong> Basées sur le LLM (plus de simulation !)</li>
            </ul>
            
            <div class="config-section">
                <h3>⚙️ Configuration Ollama</h3>
                <table>
                    <tr>
                        <th>Paramètre</th>
                        <th>Valeur par défaut</th>
                        <th>Description</th>
                    </tr>
                    <tr>
                        <td><code>model</code></td>
                        <td>gemma3:4b</td>
                        <td>Modèle Ollama à utiliser</td>
                    </tr>
                    <tr>
                        <td><code>temperature</code></td>
                        <td>0.7</td>
                        <td>Créativité (0-2). Plus élevé = plus créatif</td>
                    </tr>
                    <tr>
                        <td><code>top_p</code></td>
                        <td>0.9</td>
                        <td>Nucleus sampling (0-1)</td>
                    </tr>
                    <tr>
                        <td><code>max_tokens</code></td>
                        <td>2000</td>
                        <td>Nombre max de tokens générés</td>
                    </tr>
                    <tr>
                        <td><code>top_k</code></td>
                        <td>40</td>
                        <td>Top-K sampling</td>
                    </tr>
                    <tr>
                        <td><code>repeat_penalty</code></td>
                        <td>1.1</td>
                        <td>Pénalité répétition</td>
                    </tr>
                </table>
            </div>
            
            <h2 style="margin: 30px 0 20px; color: #1f2937;">📡 Endpoints API</h2>
            
            <div class="endpoint">
                <h3><span class="get">GET</span> /health</h3>
                <p>Vérification de l'état du service et d'Ollama</p>
            </div>
            
            <div class="endpoint">
                <h3><span class="get">GET</span> /ollama/models</h3>
                <p>Liste les modèles Ollama disponibles</p>
            </div>
            
            <div class="endpoint">
                <h3><span class="post">POST</span> /api/analyze</h3>
                <p>Génère une analyse avec Ollama (paramètres configurables)</p>
                <p style="margin-top: 10px;"><strong>Body JSON:</strong></p>
                <pre>{
  "products": ["iPhone 15", "Galaxy S24"],
  "sector": "Smartphones Premium",
  
  // Configuration Ollama (optionnel)
  "ollama": {
    "use_ollama": true,
    "model": "gemma3:4b",
    "temperature": 0.7,
    "top_p": 0.9,
    "max_tokens": 2000
  }
}</pre>
            </div>
            
            <div class="endpoint">
                <h3><span class="get">GET</span> /api/download/&lt;filename&gt;</h3>
                <p>Télécharge un rapport PDF généré</p>
            </div>
            
            <div class="endpoint">
                <h3><span class="get">GET</span> /api/reports</h3>
                <p>Liste tous les rapports disponibles</p>
            </div>
            
            <div style="margin-top: 30px; padding: 20px; background: #dbeafe; border-radius: 10px; border-left: 4px solid #3b82f6;">
                <strong>📚 Documentation:</strong> Consultez README.md et OLLAMA_GUIDE.md pour plus de détails
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
    """Page d'accueil"""
    return render_template_string(get_homepage_html())


@app.route('/health')
def health_check():
    """Health check avec vérification Ollama"""
    from ollama_analyzer import OllamaClient, OllamaConfig
    
    # Vérifier Ollama
    client = OllamaClient(OllamaConfig())
    ollama_status = client.check_connection()
    
    response = HealthCheckResponse(
        status='healthy' if ollama_status else 'degraded',
        timestamp=datetime.now().isoformat(),
        version='2.1.0-ollama',
        service='Market Study API with Ollama'
    )
    
    response_dict = response.dict()
    response_dict['ollama'] = {
        'available': ollama_status,
        'default_model': 'gemma3:4b'
    }
    
    return jsonify(response_dict), 200


@app.route('/ollama/models')
def list_ollama_models():
    """Liste les modèles Ollama disponibles"""
    from ollama_analyzer import OllamaClient, OllamaConfig
    
    try:
        client = OllamaClient(OllamaConfig())
        
        if not client.check_connection():
            return jsonify({
                'error': 'Ollama non accessible',
                'details': 'Assurez-vous qu\'Ollama est démarré (ollama serve)'
            }), 503
        
        models = client.list_models()
        
        return jsonify({
            'success': True,
            'models': models,
            'count': len(models),
            'default': 'gemma3:4b'
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Erreur lors du listing des modèles',
            'details': str(e)
        }), 500


@app.route('/api/analyze', methods=['POST'])
def analyze_market():
    """
    Endpoint principal d'analyse avec Ollama
    
    Body JSON:
    {
        "products": ["Product 1", "Product 2"],
        "sector": "Sector Name",
        "ollama": {
            "use_ollama": true,
            "model": "gemma3:4b",
            "temperature": 0.7,
            "top_p": 0.9,
            "max_tokens": 2000
        }
    }
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
        
        # Extraire la configuration Ollama
        ollama_config = data.get('ollama', {})
        use_ollama = ollama_config.get('use_ollama', True)
        
        # Logging de la requête
        print(f"\n{'='*70}")
        print(f"📊 NOUVELLE ANALYSE {'OLLAMA' if use_ollama else 'SIMULATION'}")
        print(f"{'='*70}")
        print(f"Secteur: {request_data.sector}")
        print(f"Produits ({len(request_data.products)}): {', '.join(request_data.products)}")
        
        if use_ollama:
            print(f"\n🤖 Configuration Ollama:")
            print(f"   Modèle: {ollama_config.get('model', 'gemma3:4b')}")
            print(f"   Temperature: {ollama_config.get('temperature', 0.7)}")
            print(f"   Top-P: {ollama_config.get('top_p', 0.9)}")
            print(f"   Max Tokens: {ollama_config.get('max_tokens', 2000)}")
        
        print(f"{'='*70}\n")
        
        # Créer l'analyseur avec la config demandée
        analyzer = get_analyzer(
            use_ollama=use_ollama,
            model=ollama_config.get('model'),
            temperature=ollama_config.get('temperature'),
            top_p=ollama_config.get('top_p'),
            max_tokens=ollama_config.get('max_tokens'),
            top_k=ollama_config.get('top_k', 40),
            repeat_penalty=ollama_config.get('repeat_penalty', 1.1),
            seed=ollama_config.get('seed')
        )
        
        # Analyse des produits
        print("🔬 Phase 1: Analyse des produits avec LLM...")
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
                'ollama_used': use_ollama,
                'model': ollama_config.get('model', 'simulation'),
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
    """Télécharge un rapport PDF"""
    try:
        filepath = config.REPORTS_DIR / filename
        
        if not filepath.exists():
            error = ErrorResponse(
                error='Fichier non trouvé',
                details=f'Le fichier {filename} n\'existe pas',
                status_code=404
            )
            return jsonify(error.dict()), 404
        
        # Sécurité: Path Traversal Protection
        if not str(filepath.resolve()).startswith(str(config.REPORTS_DIR.resolve())):
            error = ErrorResponse(
                error='Accès non autorisé',
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
    """Liste tous les rapports disponibles"""
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
        
        # Trier par date
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
# DÉMARRAGE
# ============================================================================

def print_startup_banner():
    """Affiche la bannière de démarrage"""
    print("\n" + "="*70)
    print(" "*15 + "🤖 MARKET STUDY API - OLLAMA EDITION")
    print("="*70)
    print(f"\n📦 Version: 2.1.0-ollama")
    print(f"📁 Dossier rapports: {config.REPORTS_DIR.absolute()}")
    print(f"🤖 LLM: DeepSeek-R1 (ou autre modèle Ollama)")
    print(f"\n🌐 URL: http://localhost:{config.PORT}")
    print(f"📊 Interface: http://localhost:{config.PORT}/")
    print(f"❤️  Health Check: http://localhost:{config.PORT}/health")
    print(f"🤖 Modèles Ollama: http://localhost:{config.PORT}/ollama/models")
    print(f"\n{'='*70}\n")
    print("💡 Assurez-vous qu'Ollama est démarré: ollama serve")
    print("📥 Télécharger DeepSeek: ollama pull gemma3:4b")
    print("⏸️  Appuyez sur Ctrl+C pour arrêter\n")


if __name__ == '__main__':
    print_startup_banner()
    
    app.run(
        debug=config.DEBUG, 
        host=config.HOST, 
        port=config.PORT
    )