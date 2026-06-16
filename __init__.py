"""
financial_agent — Demostración de patrones agénticos.

Integra Tool Use, Parallelization, Routing, Prompt Chaining y Reflection
en un analizador financiero funcional.

Uso:
    from financial_agent.main import analyze_company

    report = await analyze_company("NVIDIA")
"""

from .main import analyze_company
from .models import AnalysisContext

__all__ = ["analyze_company", "AnalysisContext"]
