"""
financial_agent/routing.py — Clasificación de empresa (Routing).

Router determinista: clasifica la empresa según métricas financieras.
No necesita LLM — las reglas son claras y reproducibles.

En producción, un router basado en LLM sería útil cuando las categorías
son semánticamente ambiguas o requieren contexto que las reglas no capturan.
"""

from .models import AnalysisContext


def route_company(ctx: AnalysisContext) -> str:
    """
    Clasifica la empresa en un tipo basado en métricas financieras.

    Routing: decide qué estrategia de análisis aplicar según el perfil
    de la empresa. Esto afecta los prompts en Prompt Chaining.

    Reglas:
    - Growth: revenue_growth > 20% → enfoque en escalabilidad y valoración
    - Risk: debt_ratio > 0.6 → enfoque en solvencia y liquidez
    - Stable: todo lo demás → enfoque en dividendos y estabilidad

    Returns:
        Tipo de empresa: "growth", "risk" o "stable".
    """
    financials = ctx.financials
    balance = ctx.balance

    revenue_growth = financials.get("revenue_growth", 0)
    debt = balance.get("debt", 0)
    equity = balance.get("equity", 1)

    debt_ratio = debt / equity if equity > 0 else 0

    if revenue_growth > 0.20:
        ctx.company_type = "growth"
    elif debt_ratio > 0.6:
        ctx.company_type = "risk"
    else:
        ctx.company_type = "stable"

    return ctx.company_type
