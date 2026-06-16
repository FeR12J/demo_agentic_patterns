"""
financial_agent/reflection.py — Reflection (Generator-Critic).

El Generator ya produjo un draft del informe. El Critic lo revisa
contra los datos originales y proporciona feedback. Si hay problemas,
el Generator corrige. Loop hasta OUTPUT_ACCEPTABLE o max iteraciones.

Patrones clave:
- Separación de roles: Generator vs Critic
- Criterios de evaluación explícitos
- Max iteraciones para prevenir bucles infinitos
- Feedback estructurado para correcciones
"""

import httpx
from .models import AnalysisContext
from .chaining import call_llm
from .prompts import build_critic_prompt, build_correction_prompt

MAX_ITERATIONS = 3


async def critic_review(ctx: AnalysisContext) -> tuple[bool, str]:
    """
    El Critic evalúa el draft del informe.

    Input: ctx.report_draft + datos originales
    Output: (is_acceptable, feedback)

    Si el informe es correcto, devuelve (True, "").
    Si hay problemas, devuelve (False, feedback_especifico).

    Usamos temperatura baja para consistencia en la evaluación.
    """
    prompt = build_critic_prompt(ctx)
    system = (
        "Eres un revisor de informes financieros. Sé estricto pero justo. "
        "Escribe en español. Si el informe es correcto, responde SOLO "
        "OUTPUT_ACCEPTABLE. Si hay problemas, proporciona feedback específico."
    )

    response = await call_llm(prompt, system=system, temperature=0.1)

    if "OUTPUT_ACCEPTABLE" in response:
        return True, ""

    return False, response


async def correct_report(ctx: AnalysisContext) -> str:
    """
    El Generator corrige el informe basado en el feedback del Critic.

    Input: ctx.report_draft + ctx.critic_feedback
    Output: nuevo draft corregido

    Usamos temperatura ligeramente más alta para permitir creatividad
    en la corrección, pero no tanto que se desvíe de los datos.
    """
    prompt = build_correction_prompt(ctx)
    system = (
        "Eres un analista financiero que corrige su informe basado en feedback. "
        "Escribe en español. Incorpora las correcciones sin inventar datos nuevos."
    )

    ctx.report_draft = await call_llm(prompt, system=system, temperature=0.2)
    return ctx.report_draft


async def reflect(ctx: AnalysisContext) -> str:
    """
    Ejecuta el loop de Reflection.

    Proceso:
    1. Critic revisa el draft
    2. Si es aceptable → termina
    3. Si no → Generator corrige, vuelve al paso 1
    4. Max 3 iteraciones para prevenir bucles infinitos

    Returns:
        Informe final corregido.
    """
    for iteration in range(MAX_ITERATIONS):
        ctx.reflection_iterations = iteration + 1

        is_acceptable, feedback = await critic_review(ctx)

        if is_acceptable:
            ctx.final_report = ctx.report_draft
            return ctx.final_report

        # Feedback no aceptable → corregir
        ctx.critic_feedback = feedback
        await correct_report(ctx)

    # Si llegamos aquí, se agotaron las iteraciones
    # Guardamos el último draft como final
    ctx.final_report = ctx.report_draft
    return ctx.final_report
