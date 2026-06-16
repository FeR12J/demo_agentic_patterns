"""
financial_agent/tools.py — Herramientas de datos (Tool Use).

Cada herramienta devuelve datos estructurados. Usamos mock data para
mantener el foco en los patrones, no en integraciones externas.

En producción, esto sería:
- Yahoo Finance API, AlphaVantage, Finnhub, o endpoints propios.
- Con rate limiting, retries, y manejo de errores real.
"""

import random

# Mock data para demostración. En producción, esto viene de APIs reales.
MOCK_FINANCIALS = {
    "NVIDIA": {
        "revenue": 60922000000,
        "revenue_growth": 0.94,
        "net_income": 29760000000,
        "eps": 11.93,
        "gross_margin": 0.72,
        "operating_margin": 0.62,
        "pe_ratio": 52.3,
        "market_cap": 1250000000000,
    },
    "AAPL": {
        "revenue": 383285000000,
        "revenue_growth": 0.03,
        "net_income": 93736000000,
        "eps": 6.13,
        "gross_margin": 0.45,
        "operating_margin": 0.30,
        "pe_ratio": 29.8,
        "market_cap": 3400000000000,
    },
    "TSLA": {
        "revenue": 96773000000,
        "revenue_growth": 0.19,
        "net_income": 14997000000,
        "eps": 4.31,
        "gross_margin": 0.18,
        "operating_margin": 0.08,
        "pe_ratio": 112.5,
        "market_cap": 850000000000,
    },
}

MOCK_BALANCE = {
    "NVIDIA": {
        "cash": 25984000000,
        "debt": 9703000000,
        "assets": 65728000000,
        "liabilities": 22752000000,
        "equity": 42976000000,
    },
    "AAPL": {
        "cash": 61555000000,
        "debt": 106629000000,
        "assets": 364980000000,
        "liabilities": 290437000000,
        "equity": 74543000000,
    },
    "TSLA": {
        "cash": 29092000000,
        "debt": 9566000000,
        "assets": 106618000000,
        "liabilities": 43009000000,
        "equity": 63609000000,
    },
}

MOCK_NEWS = {
    "NVIDIA": [
        "NVIDIA anuncia nueva arquitectura Blackwell para data centers",
        "La demanda de chips AI supera la capacidad de producción de TSMC",
        "Analistas elevan precio objetivo de NVIDIA a $200",
        "Competencia de AMD con MI300 gana cuota en mercado enterprise",
        "NVIDIA invierte $500M en fund de startups de computación cuántica",
    ],
    "AAPL": [
        "Apple supera expectativas de ventas de iPhone en Q4",
        "Nuevas regulaciones de la UE afectan servicios de App Store",
        "Apple Vision Pro enfrenta desafíos de adopción en mercado masivo",
        "Servicios de Apple crecen 12% interanual",
        "Apple anuncia programa de reciclaje de dispositivos más ambicioso",
    ],
    "TSLA": [
        "Tesla entrega 484,507 vehículos en Q4, por debajo de expectativas",
        "FSD v12 muestra mejoras significativas en conducción autónoma",
        "Tesla reduce precios de Model 3 y Model Y en mercado europeo",
        "Competencia china de BYD presiona márgenes de Tesla",
        "Tesla abre nueva fábrica de baterías en Texas",
    ],
}


def get_financials(company: str) -> dict:
    """Obtiene datos financieros de una empresa.

    Tool Use: esta es una herramienta que el agente puede invocar.
    En producción, sería una llamada a Yahoo Finance, AlphaVantage,
    o un endpoint REST interno con manejo de errores.
    """
    ticker = company.upper()
    if ticker in MOCK_FINANCIALS:
        data = MOCK_FINANCIALS[ticker].copy()
        # Simular variación pequeña para que no sea estático
        data["revenue"] = int(data["revenue"] * random.uniform(0.98, 1.02))
        return data
    # Fallback genérico
    return {
        "revenue": random.randint(10000000000, 500000000000),
        "revenue_growth": round(random.uniform(-0.1, 0.5), 2),
        "net_income": random.randint(1000000000, 100000000000),
        "eps": round(random.uniform(1.0, 15.0), 2),
        "gross_margin": round(random.uniform(0.1, 0.6), 2),
        "operating_margin": round(random.uniform(0.05, 0.4), 2),
        "pe_ratio": round(random.uniform(10.0, 120.0), 1),
        "market_cap": random.randint(50000000000, 2000000000000),
    }


def get_balance(company: str) -> dict:
    """Obtiene el balance de una empresa.

    Tool Use: segunda herramienta independiente.
    La independencia es clave para Parallelization: estas dos
    herramientas no dependen una de la otra.
    """
    ticker = company.upper()
    if ticker in MOCK_BALANCE:
        return MOCK_BALANCE[ticker].copy()
    return {
        "cash": random.randint(5000000000, 100000000000),
        "debt": random.randint(1000000000, 200000000000),
        "assets": random.randint(20000000000, 500000000000),
        "liabilities": random.randint(10000000000, 300000000000),
        "equity": random.randint(5000000000, 200000000000),
    }


def get_news(company: str) -> list:
    """Obtiene noticias recientes sobre una empresa.

    Tool Use: tercera herramienta independiente.
    Tres herramientas independientes = candidato ideal para Parallelization.
    """
    ticker = company.upper()
    if ticker in MOCK_NEWS:
        return MOCK_NEWS[ticker].copy()
    return [
        f"{company} reporta resultados trimestrales dentro de expectativas",
        f"Analistas mantienen recomendación de compra para {company}",
        f"{company} anuncia expansión en mercados internacionales",
        f"Competencia en sector de {company} se intensifica",
        f"{company} invierte en desarrollo de nuevas tecnologías",
    ]
