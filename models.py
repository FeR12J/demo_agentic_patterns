"""
financial_agent/models.py — Contexto central compartido entre patrones.

Cada patrón lee y escribe en el mismo objeto. Evita pasar 15 variables
entre funciones y mantiene el flujo visible.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class AnalysisContext:
    """Contexto compartido entre todos los patrones del pipeline."""

    # Entrada
    company: str

    # Datos crudos (Tool Use + Parallelization)
    financials: dict = field(default_factory=dict)
    balance: dict = field(default_factory=dict)
    news: list = field(default_factory=list)

    # Clasificación (Routing)
    company_type: Optional[str] = None

    # Generación (Prompt Chaining)
    summary: str = ""
    risks: str = ""
    outlook: str = ""
    report_draft: str = ""

    # Revision (Reflection)
    final_report: str = ""
    reflection_iterations: int = 0
    critic_feedback: str = ""
