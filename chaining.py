"""
financial_agent/chaining.py — Prompt Chaining.

Cada paso del pipeline recibe el output del paso anterior como input.
El patrón Prompt Chaining descompone una tarea compleja (generar un
informe financiero) en etapas secuenciales más simples y controlables.

Flujo:
    Datos → Resumen → Riesgos → Perspectivas → Informe completo
"""

import httpx
from .models import AnalysisContext
from .prompts import (
    build_summary_prompt,
    build_risks_prompt,
    build_outlook_prompt,
    build_report_prompt,
)

# Configuración del modelo local
LLM_BASE_URL = "http://10.0.1.5:1234/v1"
LLM_MODEL = "google/gemma-4-12b"  


async def call_llm(prompt: str, system: str = "", temperature: float = 0.3) -> str:
    """Llama al modelo local vía API OpenAI-compatible.

    En producción, incluiríamos:
    - Retry con backoff exponencial
    - Timeout configurable
    - Logging de la llamada y respuesta
    - Manejo de errores de conexión
    """
    headers = {"Content-Type": "application/json"}
    messages = []

    if system:
        messages.append({"role": "system", "content": system})

    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": LLM_MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": 2048,
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{LLM_BASE_URL}/chat/completions",
            json=payload,
            headers=headers,
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]


async def generate_summary(ctx: AnalysisContext) -> str:
    """Paso 1: Generar resumen ejecutivo.

    Input: ctx.financials + ctx.balance
    Output: ctx.summary
    """
    prompt = build_summary_prompt(ctx)
    system = "Eres un analista financiero senior. Escribe en español, tono profesional."

    ctx.summary = await call_llm(prompt, system=system, temperature=0.3)
    return ctx.summary


async def generate_risks(ctx: AnalysisContext) -> str:
    """Paso 2: Identificar riesgos.

    Input: ctx.summary + ctx.news
    Output: ctx.risks

    Nota: este paso depende del output del paso anterior (summary).
    Eso es Prompt Chaining: cada etapa alimenta la siguiente.
    """
    prompt = build_risks_prompt(ctx)
    system = "Eres un analista de riesgos financieros. Escribe en español."

    ctx.risks = await call_llm(prompt, system=system, temperature=0.3)
    return ctx.risks


async def generate_outlook(ctx: AnalysisContext) -> str:
    """Paso 3: Generar perspectivas futuras.

    Input: ctx.summary + ctx.risks + ctx.company_type
    Output: ctx.outlook

    Nota: usa company_type del router para personalizar el enfoque.
    """
    prompt = build_outlook_prompt(ctx)
    system = "Eres un estratega financiero. Escribe en español."

    ctx.outlook = await call_llm(prompt, system=system, temperature=0.3)
    return ctx.outlook


async def generate_report(ctx: AnalysisContext) -> str:
    """Paso 4: Generar informe completo.

    Input: ctx.summary + ctx.risks + ctx.outlook
    Output: ctx.report_draft

    Este es el paso final del chaining. Recoge todos los outputs
    anteriores y los integra en un documento coherente.
    """
    prompt = build_report_prompt(ctx)
    system = "Eres un analista financiero que escribe informes profesionales. Escribe en español."

    ctx.report_draft = await call_llm(prompt, system=system, temperature=0.2)
    return ctx.report_draft


async def run_chaining(ctx: AnalysisContext) -> str:
    """
    Ejecuta la cadena completa de prompts.

    Pipeline secuencial:
    1. Resumen ejecutivo (financials + balance)
    2. Análisis de riesgos (summary + news)
    3. Perspectivas (summary + risks + company_type)
    4. Informe completo (summary + risks + outlook)

    Returns:
        Draft del informe completo.
    """
    await generate_summary(ctx)
    await generate_risks(ctx)
    await generate_outlook(ctx)
    await generate_report(ctx)

    return ctx.report_draft
