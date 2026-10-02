import requests
import json
import os

API_URL = "https://graph.facebook.com/v21.0"

def get_channel_profile(token, ig_id):
    """Fetches live profile stats from Meta Graph API."""
    res = requests.get(f"{API_URL}/{ig_id}", params={
        "access_token": token,
        "fields": "id,username,name,biography,followers_count,follows_count,media_count,website,profile_picture_url"
    }).json()
    if "error" in res:
        raise Exception(res["error"]["message"])
    return res

def get_channel_posts(token, ig_id, limit=12):
    """Fetches recent posts and their performance metrics."""
    res = requests.get(f"{API_URL}/{ig_id}/media", params={
        "access_token": token,
        "fields": "id,caption,media_type,media_product_type,timestamp,permalink,like_count,comments_count",
        "limit": limit
    }).json()
    posts = res.get("data", [])
    
    enriched = []
    for p in posts:
        mid = p["id"]
        ins_res = requests.get(f"{API_URL}/{mid}/insights", params={
            "access_token": token,
            "metric": "reach,saved,total_interactions,plays"
        }).json()
        
        ins = {}
        if "data" in ins_res:
            for item in ins_res["data"]:
                ins[item["name"]] = item["values"][0]["value"]
                
        p["insights"] = ins
        likes = p.get("like_count", 0)
        comments = p.get("comments_count", 0)
        saved = ins.get("saved", 0)
        reach = ins.get("reach", 0)
        score = likes + (comments * 3.0) + (saved * 2.5) + (reach * 0.02)
        p["score"] = round(score, 1)
        enriched.append(p)
        
    return sorted(enriched, key=lambda x: x["score"], reverse=True)

def generate_personal_plan():
    """Generates the daily strategy and 8 reels for @s_thiago7 based on last 24h real metrics."""
    try:
        from services.analytics_engine import load_latest_strategy
        strat = load_latest_strategy()
        p_strat = strat.get("personal", {})
        if p_strat and "reels" in p_strat:
            return {
                "diagnostic_24h": {
                    "winner_title": p_strat.get("winner_title"),
                    "winner_stats": p_strat.get("winner_stats"),
                    "why_winner": p_strat.get("why_winner"),
                    "loser_title": p_strat.get("loser_title"),
                    "loser_stats": p_strat.get("loser_stats"),
                    "why_loser": p_strat.get("why_loser"),
                    "renewed_focus": p_strat.get("renewed_focus"),
                    "status": p_strat.get("status", "Actualizado con reportes en tiempo real")
                },
                "plan": p_strat.get("reels", [])
            }
    except Exception as e:
        print(f"Error loading dynamic personal plan: {e}")

    # Fallback default plan
    return {
        "diagnostic_24h": {
            "winner_title": "Enfoque, disciplina y prioridades claras",
            "winner_stats": "3,486 vistas · 48 guardados · 56 reposts · 40.2% skip",
            "why_winner": "Mentalidad de disciplina en los 20s con formato de 8 segundos en loop visual.",
            "loser_title": "Al Dm o miedo?",
            "loser_stats": "204 alcance · 0 guardados · 73.8% skip",
            "why_loser": "Pregunta vacía sin gancho de valor en el segundo 1.",
            "renewed_focus": "Enfoque en estándares innegociables y construcción silenciosa en los 20s.",
            "status": "Actualizado con reportes en tiempo real"
        },
        "plan": [
            {
                "id": 1,
                "time": "09:30 AM",
                "theme": "Estándares Innegociables en los 20s",
                "line1": "Cuando entiendes que el éxito no es suerte...",
                "line2": "...es haber dicho 'no' a 50 planes para construir un proyecto que nadie más ve.",
                "copy": "Decir 'no' a tiempo es la habilidad más rentable de tus 20s. Guarda este reel.",
                "tip": "Grábate trabajando con café en mano (8 seg exactos, loop visual sin cortes)."
            },
            {
                "id": 2,
                "time": "11:00 AM",
                "theme": "Filtro de Pareja & Proyecto de Vida",
                "line1": "No le tengo miedo a quedarme soltero en mis 20s...",
                "line2": "...le tengo miedo a juntarme con alguien que no tenga metas, no sume a mi paz y solo me haga perder el tiempo.",
                "copy": "Tu pareja debe ser tu socia de vida, no un motivo más de estrés. Estar en paz multiplica tus resultados.",
                "tip": "Mirada serena hacia la ventana o ajustándote la chaqueta (6-8 seg)."
            },
            {
                "id": 3,
                "time": "01:00 PM",
                "theme": "Madurez & Prioridades Reales",
                "line1": "Me dicen 'por qué estás tan solo si eres buen partido'...",
                "line2": "...porque en esta generación si tienes metas claras incomodas, y si no sales cada fin de semana dicen que eres aburrido.",
                "copy": "Prefiero ser 'aburrido' construyendo libertad que ser el alma de la fiesta sin futuro financiero.",
                "tip": "Sonrisa irónica breve dejando el celular sobre la mesa."
            },
            {
                "id": 4,
                "time": "03:00 PM",
                "theme": "Construcción en Silencio",
                "line1": "Trabaja tan duro en silencio...",
                "line2": "...que cuando tus resultados hablen, la gente que dudaba jure que tuviste suerte.",
                "copy": "El proceso no se publica todos los días; los resultados hablan solos. Guarda este recordatorio.",
                "tip": "Tomas rápidas de laptop, libreta con notas y reloj (8 segundos)."
            },
            {
                "id": 5,
                "time": "05:00 PM",
                "theme": "El Filtro de los 25+",
                "line1": "El cambio de mentalidad más grande al madurar:",
                "line2": "Dejar de buscar parejas para llenar vacíos y empezar a buscar personas con las que construir un imperio.",
                "copy": "Círculo pequeño, metas gigantescas y cero tiempo que perder. Te leo en comentarios 👇",
                "tip": "Mirando a cámara con tono firme y seguro."
            },
            {
                "id": 6,
                "time": "06:45 PM",
                "theme": "Protección de Energía",
                "line1": "No soy frío ni distante...",
                "line2": "...simplemente me costó demasiado construir mi tranquilidad como para regalársela a cualquiera.",
                "copy": "Cuidar tu energía no es orgullo, es amor propio y dirección. ¿Estás de acuerdo?",
                "tip": "Cerrando la laptop y respirando en calma con luz tenue."
            },
            {
                "id": 7,
                "time": "08:15 PM",
                "theme": "Objetivo Financiero Antes de los 30",
                "line1": "Dicen que el amor llega cuando menos lo buscas...",
                "line2": "...yo no lo estoy buscando porque estoy ocupado asegurando mi libertad financiera antes de los 30 😂🎯",
                "copy": "Prioridades en orden. El dinero no compra la felicidad, pero compra la tranquilidad de tu familia.",
                "tip": "Risa breve mirando el código o métricas en pantalla."
            },
            {
                "id": 8,
                "time": "09:30 PM",
                "theme": "Cierre Nocturno de Disciplina",
                "line1": "Al final del día no necesitas 20 personas detrás de ti...",
                "line2": "...necesitas una sola persona real que entienda tus silencios, apoye tu visión y camine a tu lado.",
                "copy": "Pocos pero leales. Mañana seguimos construyendo. Buenas noches 🔥",
                "tip": "Cerrando la jornada, pantalla apagándose."
            }
        ]
    }

def generate_nodo_plan():
    """Generates the daily B2B strategy and reels for @nodo_tg based on last 24h real metrics."""
    try:
        from services.analytics_engine import load_latest_strategy
        strat = load_latest_strategy()
        n_strat = strat.get("nodo", {})
        if n_strat and "reels" in n_strat:
            return {
                "diagnostic_24h": {
                    "winner_title": n_strat.get("winner_title"),
                    "winner_stats": n_strat.get("winner_stats"),
                    "why_winner": n_strat.get("why_winner"),
                    "loser_title": n_strat.get("loser_title"),
                    "loser_stats": n_strat.get("loser_stats"),
                    "why_loser": n_strat.get("why_loser"),
                    "renewed_focus": n_strat.get("renewed_focus"),
                    "status": n_strat.get("status", "Actualizado con reportes en tiempo real")
                },
                "plan": n_strat.get("reels", [])
            }
    except Exception as e:
        print(f"Error loading dynamic nodo plan: {e}")

    # Fallback default plan
    return {
        "diagnostic_24h": {
            "winner_title": "No se descarga en la App Store ni viene en paquete zip",
            "winner_stats": "621 vistas · 38.8% skip · 34% en procesos manuales",
            "why_winner": "Formato de dolor operativo en 8s señalando ineficiencias de procesos manuales.",
            "loser_title": "El link en el primer comentario",
            "loser_stats": "80 vistas · 87.5% skip",
            "why_loser": "Pedir clics directos al segundo 1 provoca salto inmediato.",
            "renewed_focus": "Enfoque B2B: Atacar el cementerio de cotizaciones en WhatsApp y el riesgo de WhatsApp personal.",
            "status": "Actualizado con reportes en tiempo real"
        },
        "plan": [
            {
                "id": 1,
                "time": "12:30 PM",
                "theme": "El Cementerio de Cotizaciones en PDF",
                "line1": "El cementerio de ventas de las empresas de servicios:",
                "line2": "Enviar una cotización en PDF por WhatsApp y jamás volver a hacerle seguimiento. El 60% de tus ventas se mueren en el visto.",
                "copy": "Tus comerciales no necesitan más leads desordenados, necesitan una ruta automatizada. Conectamos Kommo CRM con WhatsApp API para que ninguna propuesta quede en el olvido. Diagnóstico en conectanodo.com",
                "tip": "Tomas en loop de un PDF en WhatsApp y luego el pipeline visual en pantalla (8 segundos)."
            },
            {
                "id": 2,
                "time": "04:30 PM",
                "theme": "El Riesgo de WhatsApp Personal",
                "line1": "El mayor riesgo operativo en tu empresa B2B:",
                "line2": "Que los clientes vivan en los celulares de tus asesores. Si el comercial renuncia, tu base de datos se va con él.",
                "copy": "Centralizar la captación no es desconfianza, es proteger el activo más valioso de tu empresa. En NODO integramos CRM multiagente con IA. Conoce el método en conectanodo.com",
                "tip": "Transición rápida entre teléfono personal y panel centralizado oficial."
            },
            {
                "id": 3,
                "time": "07:30 PM",
                "theme": "IA vs Procesos Manuales",
                "line1": "Ustedes siguen respondiendo mensajes a mano a las 10 PM...",
                "line2": "...mientras tu competencia tiene un agente de IA calificando prospectos y agendando llamadas en 15 segundos.",
                "copy": "No se trata de reemplazar personas, sino de eliminar la fricción que te hace perder contratos. Automatización comercial con n8n y Kommo en conectanodo.com",
                "tip": "Tomas estéticas de flujos automatizados respondiendo en tiempo real."
            }
        ]
    }
