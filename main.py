"""
financial_agent/main.py — Orquestador principal.

Este módulo integra todos los patrones en un flujo coherente:

    analyze_company()
    ├── Tool Use + Parallelization  (fetch_data)
    ├── Routing                     (route_company)
    ├── Prompt Chaining             (run_chaining)
    └── Reflection                  (reflect)

Cada patrón tiene una responsabilidad clara y no se solapan.
El objetivo es pedagógico: Que alguien pueda señalar cualquier
bloque y decir "esto es X patrón".
"""

import asyncio
import json
import os
from datetime import datetime

from .models import AnalysisContext
from .tools import get_financials, get_balance, get_news
from .routing import route_company
from .chaining import run_chaining
from .reflection import reflect


async def fetch_data(ctx: AnalysisContext) -> None:
    """Tool Use + Parallelization.

    Tres herramientas independientes se ejecutan concurrentemente.
    Esto demuestra Parallelization: En lugar de llamar secuencialmente
    a cada herramienta, las ejecutamos en paralelo porque no dependen
    una de la otra.
    """
    financials, balance, news = await asyncio.gather(
        asyncio.to_thread(get_financials, ctx.company),
        asyncio.to_thread(get_balance, ctx.company),
        asyncio.to_thread(get_news, ctx.company),
    )

    ctx.financials = financials
    ctx.balance = balance
    ctx.news = news


async def analyze_company(company: str) -> str:
    """Orquestador principal.

    Integra todos los patrones en un flujo coherente:

    1. Tool Use: obtener datos de herramientas externas
    2. Parallelization: ejecutar herramientas concurrentemente
    3. Routing: clasificar la empresa según métricas
    4. Prompt Chaining: generar informe paso a paso
    5. Reflection: revisar y corregir el informe

    Args:
        company: Ticker o nombre de la empresa (ej: "NVIDIA", "AAPL").

    Returns:
        Informe final en formato Markdown.
    """
    # Paso 1: Crear contexto compartido
    ctx = AnalysisContext(company=company)

    # Paso 2: Tool Use + Parallelization
    # Tres herramientas independientes ejecutadas concurrentemente
    await fetch_data(ctx)

    # Paso 3: Routing
    # Clasificar la empresa para personalizar el análisis
    company_type = route_company(ctx)

    # Paso 4: Prompt Chaining
    # Generar informe paso a paso: resumen → riesgos → perspectivas → informe
    await run_chaining(ctx)

    # Paso 5: Reflection
    # Revisar y corregir el informe
    final_report = await reflect(ctx)

    # Paso 6: Guardar informe
    save_report(ctx, final_report)

    return final_report


def save_report(ctx: AnalysisContext, report: str) -> str:
    """
    Guarda el informe en un archivo Markdown.

    Args:
        ctx: Contexto de análisis con metadatos.
        report: Contenido del informe.

    Returns:
        Ruta del archivo guardado.
    """
    reports_dir = os.path.join(os.path.dirname(__file__), "reports")
    os.makedirs(reports_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{ctx.company.lower()}_{timestamp}.md"
    filepath = os.path.join(reports_dir, filename)

    # Agregar metadatos al inicio
    metadata = {
        "company": ctx.company,
        "company_type": ctx.company_type,
        "reflection_iterations": ctx.reflection_iterations,
        "generated_at": datetime.now().isoformat(),
    }

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"<!-- {json.dumps(metadata, indent=2)} -->\n\n")
        f.write(report)

    return filepath


async def main():
    """Entry point para pruebas locales."""
    company = "NVIDIA"

    print(f"Analizando {company}...")
    report = await analyze_company(company)

    print("\n" + "=" * 60)
    print(report)
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
