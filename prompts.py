"""
financial_agent/prompts.py — Templates de prompts para Prompt Chaining.

Cada prompt tiene un propósito específico y recibe datos del contexto.
El patrón Prompt Chaining se basa en que cada paso del pipeline
recibe el output del paso anterior como input.
"""


def build_summary_prompt(ctx) -> str:
    """
    Prompt para generar resumen ejecutivo.

    Input: financials + balance
    Output: ctx.summary
    """
    fin = ctx.financials
    bal = ctx.balance

    return f"""Analiza estos datos financieros de {ctx.company} y genera un resumen ejecutivo conciso:

Datos financieros:
- Ingresos: ${fin.get('revenue', 0):,.0f}
- Crecimiento de ingresos: {fin.get('revenue_growth', 0)*100:.1f}%
- Beneficio neto: ${fin.get('net_income', 0):,.0f}
- EPS: ${fin.get('eps', 0):.2f}
- Margen bruto: {fin.get('gross_margin', 0)*100:.1f}%
- Margen operativo: {fin.get('operating_margin', 0)*100:.1f}%
- P/E Ratio: {fin.get('pe_ratio', 0):.1f}
- Market Cap: ${fin.get('market_cap', 0):,.0f}

Balance:
- Efectivo: ${bal.get('cash', 0):,.0f}
- Deuda: ${bal.get('debt', 0):,.0f}
- Activos: ${bal.get('assets', 0):,.0f}
- Pasivos: ${bal.get('liabilities', 0):,.0f}
- Patrimonio: ${bal.get('equity', 0):,.0f}

Genera un párrafo de 3-4 oraciones con los puntos clave."""


def build_risks_prompt(ctx) -> str:
    """
    Prompt para identificar riesgos.

    Input: summary + news
    Output: ctx.risks
    """
    news_text = "\n".join(f"- {n}" for n in ctx.news)

    return f"""Basado en este resumen financiero y las noticias recientes de {ctx.company},
identifica los principales riesgos:

Resumen financiero:
{ctx.summary}

Noticias recientes:
{news_text}

Genera una lista de 3-5 riesgos específicos, cada uno con una oración de explicación.
Enfócate en riesgos financieros, operativos y de mercado."""


def build_outlook_prompt(ctx) -> str:
    """
    Prompt para generar perspectivas futuras.

    Input: summary + risks + company_type
    Output: ctx.outlook
    """
    type_guidance = {
        "growth": "Enfócate en escalabilidad, valoración y sostenibilidad del crecimiento.",
        "risk": "Enfócate en solvencia, liquidez y gestión de deuda.",
        "stable": "Enfócate en estabilidad, dividendos y resiliencia a ciclos económicos.",
    }

    return f"""Genera perspectivas futuras para {ctx.company} basadas en:

Resumen financiero:
{ctx.summary}

Riesgos identificados:
{ctx.risks}

Tipo de empresa: {ctx.company_type}
{type_guidance.get(ctx.company_type, '')}

Genera 3-4 párrafos cortos con perspectivas a corto y largo plazo."""


def build_report_prompt(ctx) -> str:
    """
    Prompt para generar informe completo.

    Input: summary + risks + outlook
    Output: ctx.report_draft
    """
    return f"""Genera un informe financiero profesional para {ctx.company} con esta estructura:

# Informe Financiero: {ctx.company}

## Resumen Ejecutivo
{ctx.summary}

## Situación Financiera
[Desarrolla el resumen con análisis de métricas clave]

## Riesgos
{ctx.risks}

## Perspectivas
{ctx.outlook}

## Conclusión
[Conclusión breve basada en el análisis completo]

Usa formato Markdown. Mantén un tono profesional y objetivo.
No inventes datos — usa solo la información proporcionada."""


def build_critic_prompt(ctx) -> str:
    """
    Prompt para el Critic en Reflection.

    Input: report_draft + financials + balance + news
    Output: feedback o OUTPUT_ACCEPTABLE
    """
    fin = ctx.financials
    bal = ctx.balance
    news_text = "\n".join(f"- {n}" for n in ctx.news)

    return f"""Revisa este informe financiero de {ctx.company}.

INFORME:
{ctx.report_draft}

DATOS ORIGINALES:
- Ingresos: ${fin.get('revenue', 0):,.0f}
- Crecimiento: {fin.get('revenue_growth', 0)*100:.1f}%
- Beneficio neto: ${fin.get('net_income', 0):,.0f}
- Margen bruto: {fin.get('gross_margin', 0)*100:.1f}%
- Efectivo: ${bal.get('cash', 0):,.0f}
- Deuda: ${bal.get('debt', 0):,.0f}

NOTICIAS:
{news_text}

COMPRUEBA:
1. Coherencia financiera: ¿los números mencionados coinciden con los datos originales?
2. Riesgos omitidos: ¿hay riesgos evidentes que el informe no menciona?
3. Afirmaciones sin soporte: ¿hay conclusiones que no se derivan de los datos?
4. Contradicciones: ¿hay afirmaciones contradictorias dentro del informe?

Si el informe es correcto y completo, responde SOLO:
OUTPUT_ACCEPTABLE

Si hay problemas, proporciona feedback específico con:
- Qué está mal
- Por qué está mal
- Cómo corregirlo"""


def build_correction_prompt(ctx) -> str:
    """
    Prompt para corregir el informe basado en feedback del Critic.

    Input: report_draft + critic_feedback
    Output: nuevo draft corregido
    """
    return f"""Corrige este informe financiero utilizando el feedback del revisor:

INFORME ACTUAL:
{ctx.report_draft}

FEEDBACK DEL CRITIC:
{ctx.critic_feedback}

Genera el informe corregido. Mantén la estructura original pero
incorpora las correcciones sugeridas. No inventes datos nuevos."""
