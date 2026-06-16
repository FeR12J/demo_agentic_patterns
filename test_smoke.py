"""
financial_agent/test_smoke.py — Prueba básica sin modelo real.

Verifica que la estructura del proyecto funciona:
- Tools devuelven datos
- Routing clasifica correctamente
- Contexto se comparte entre módulos

No requiere conexión al modelo local.
"""

import asyncio
import sys
import os

# Permitir ejecutar directamente: python test_smoke.py
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from financial_agent.models import AnalysisContext
from financial_agent.tools import get_financials, get_balance, get_news
from financial_agent.routing import route_company


def test_tools():
    """Verificar que las herramientas devuelven datos."""
    fin = get_financials("NVIDIA")
    assert "revenue" in fin, "financials debe incluir revenue"
    assert "revenue_growth" in fin, "financials debe incluir revenue_growth"

    bal = get_balance("NVIDIA")
    assert "cash" in bal, "balance debe incluir cash"
    assert "debt" in bal, "balance debe incluir debt"

    news = get_news("NVIDIA")
    assert isinstance(news, list), "news debe ser una lista"
    assert len(news) > 0, "news debe tener al menos un elemento"

    print("✅ Tools: OK")


def test_routing():
    """Verificar que el router clasifica correctamente."""
    # Growth: NVIDIA tiene revenue_growth > 20%
    ctx = AnalysisContext(
        company="NVIDIA",
        financials={"revenue_growth": 0.94},
        balance={"debt": 9703000000, "equity": 42976000000},
    )
    assert route_company(ctx) == "growth", "NVIDIA debe ser 'growth'"

    # Risk: deuda alta
    ctx2 = AnalysisContext(
        company="TEST",
        financials={"revenue_growth": 0.05},
        balance={"debt": 100000000, "equity": 100000000},
    )
    assert route_company(ctx2) == "risk", "Empresa con deuda alta debe ser 'risk'"

    # Stable: todo lo demás
    ctx3 = AnalysisContext(
        company="STABLE",
        financials={"revenue_growth": 0.10},
        balance={"debt": 10000000, "equity": 50000000},
    )
    assert route_company(ctx3) == "stable", "Empresa normal debe ser 'stable'"

    print("✅ Routing: OK")


def test_context():
    #Verificar que el contexto se comparte correctamente.
    ctx = AnalysisContext(company="NVIDIA")

    # Simular fetch_data
    ctx.financials = get_financials("NVIDIA")
    ctx.balance = get_balance("NVIDIA")
    ctx.news = get_news("NVIDIA")

    # Simular routing
    route_company(ctx)

    assert ctx.company == "NVIDIA", "company debe ser NVIDIA"
    assert ctx.financials, "financials debe tener datos"
    assert ctx.balance, "balance debe tener datos"
    assert ctx.news, "news debe tener datos"
    assert ctx.company_type in ["growth", "risk", "stable"], "company_type debe estar clasificado"

    print("✅ Context: OK")


def test_parallelization():
    #Verificar que parallelization funciona.

    async def _run():
        ctx = AnalysisContext(company="NVIDIA")

        # Simular fetch_data con asyncio.gather
        financials, balance, news = await asyncio.gather(
            asyncio.to_thread(get_financials, ctx.company),
            asyncio.to_thread(get_balance, ctx.company),
            asyncio.to_thread(get_news, ctx.company),
        )

        ctx.financials = financials
        ctx.balance = balance
        ctx.news = news

        assert ctx.financials, "financials debe tener datos"
        assert ctx.balance, "balance debe tener datos"
        assert ctx.news, "news debe tener datos"

    asyncio.run(_run())
    print("✅ Parallelization: OK")


def main():
    #Ejecutar todas las pruebas.
    print("Ejecutando pruebas básicas...\n")

    test_tools()
    test_routing()
    test_context()
    test_parallelization()

    print("\n✅ Todas las pruebas pasaron.")


if __name__ == "__main__":
    main()
