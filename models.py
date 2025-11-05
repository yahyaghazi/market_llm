"""
Modèles de données pour l'application Market Study
"""
from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime


class ProductAnalysis(BaseModel):
    """Modèle d'analyse d'un produit avec validation"""
    
    name: str = Field(..., min_length=1, max_length=200)
    market_share: float = Field(..., ge=0, le=100)
    price: float = Field(..., ge=0)
    satisfaction: float = Field(..., ge=0, le=5)
    growth: float = Field(..., ge=-100, le=1000)
    strengths: List[str] = Field(..., min_items=3, max_items=8)
    weaknesses: List[str] = Field(..., min_items=2, max_items=7)
    opportunities: List[str] = Field(..., min_items=3, max_items=8)
    threats: List[str] = Field(..., min_items=2, max_items=7)
    positioning: str = Field(..., min_length=10, max_length=500)
    target_audience: str = Field(..., min_length=10, max_length=500)
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "iPhone 15 Pro",
                "market_share": 28.5,
                "price": 1179.0,
                "satisfaction": 4.5,
                "growth": 12.3,
                "strengths": ["Innovation constante", "Forte marque"],
                "weaknesses": ["Prix élevé"],
                "opportunities": ["Marchés émergents"],
                "threats": ["Concurrence intense"],
                "positioning": "Leader premium",
                "target_audience": "Professionnels exigeants"
            }
        }


class AnalyzeRequest(BaseModel):
    """Modèle de requête pour l'analyse de marché"""
    
    products: List[str] = Field(..., min_items=2, max_items=10)
    sector: str = Field(..., min_length=1, max_length=200)
    
    @validator('products')
    def validate_products(cls, v):
        """Valider la liste de produits"""
        # Nettoyer et valider
        cleaned = [p.strip() for p in v if p.strip()]
        
        if len(cleaned) < 2:
            raise ValueError("Au moins 2 produits valides sont requis")
        
        if len(cleaned) > 10:
            raise ValueError("Maximum 10 produits autorisés")
        
        # Vérifier les doublons
        if len(cleaned) != len(set(cleaned)):
            raise ValueError("Les produits doivent être uniques")
        
        return cleaned
    
    @validator('sector')
    def validate_sector(cls, v):
        """Valider le secteur"""
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Le secteur ne peut pas être vide")
        return cleaned
    
    class Config:
        json_schema_extra = {
            "example": {
                "products": ["iPhone 15", "Samsung Galaxy S24", "Google Pixel 8"],
                "sector": "Smartphones Premium"
            }
        }


class MarketAnalysisResult(BaseModel):
    """Modèle de résultat d'analyse de marché"""
    
    sector: str
    analysis_date: str
    products: List[ProductAnalysis]
    summary: str
    recommendations: List[str]
    
    @validator('analysis_date')
    def validate_date(cls, v):
        """Valider le format de date"""
        try:
            datetime.strptime(v, '%d/%m/%Y')
            return v
        except ValueError:
            raise ValueError("Format de date invalide, attendu: JJ/MM/AAAA")


class AnalyzeResponse(BaseModel):
    """Modèle de réponse pour l'endpoint d'analyse"""
    
    success: bool
    pdf_filename: str
    pdf_url: str
    analysis: dict
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "pdf_filename": "etude_marche_20251105_103045.pdf",
                "pdf_url": "/api/download/etude_marche_20251105_103045.pdf",
                "analysis": {
                    "sector": "Smartphones Premium",
                    "date": "05/11/2025",
                    "products_count": 3
                }
            }
        }


class ErrorResponse(BaseModel):
    """Modèle de réponse d'erreur"""
    
    error: str
    details: Optional[str] = None
    status_code: int = 500
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "Erreur lors de la génération du rapport",
                "details": "Invalid data format",
                "status_code": 400
            }
        }


class HealthCheckResponse(BaseModel):
    """Modèle de réponse pour le health check"""
    
    status: str
    timestamp: str
    version: str
    service: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "timestamp": "2025-11-05T10:30:00",
                "version": "1.0.0",
                "service": "Market Study API"
            }
        }


class ReportInfo(BaseModel):
    """Modèle d'information sur un rapport"""
    
    filename: str
    size: int
    created: str
    download_url: str


class ReportsListResponse(BaseModel):
    """Modèle de réponse pour la liste des rapports"""
    
    total: int
    reports: List[ReportInfo]