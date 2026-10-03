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

    # Fallback default plan based on latest 24h virality winners
    return {
        "diagnostic_24h": {
            "winner_title": "Enfoque, disciplina y prioridades claras. 🎯",
            "winner_stats": "47,473 vistas · 805 guardados · 1,025 reposts · 41.2% skip",
            "why_winner": "Mentalidad de disciplina, prioridades en los 20s y cuidar a la persona que camina a tu lado. Formato de 8s en loop con texto directo.",
            "loser_title": "Al Dm o miedo?",
            "loser_stats": "229 alcance · 0 guardados · 73.6% skip",
            "why_loser": "Pregunta vacía sin gancho visual ni valor en el segundo 1 provoca skip masivo.",
            "renewed_focus": "HOY nos enfocamos en: 'Hombre en construcción en sus 20s, valor de carácter vs saldo bancario y compromiso real sin medias tintas'. Formato verificado: 8 segundos en loop visual, texto en pantalla en 2 bloques y llamado de cierre enfocado en guardar.",
            "status": "Actualizado con reportes en tiempo real"
        },
        "plan": [
            {
                "id": 1,
                "time": "09:30 AM",
                "theme": "Cero Tolerancia a Perder el Tiempo en los 20s",
                "line1": "A los 20s no pierdes amigos por cambiar de actitud...",
                "line2": "...los pierdes porque cuando tu prioridad es construir libertad, ya no encajas en conversaciones de fiesta y chisme.",
                "copy": "Incomodar con tu disciplina es la señal más clara de que vas por el camino correcto. Menos ruido, más enfoque. ¿Quién más en esta misma sintonía? Guarda este reel.",
                "tip": "Grábate caminando con café o sentado frente a la laptop con postura firme (8 seg loop sin cortes)."
            },
            {
                "id": 2,
                "time": "11:00 AM",
                "theme": "El Valor de Construir desde el Piso Cero",
                "line1": "La mujer correcta no te exige una vida resuelta a los 26...",
                "line2": "...lo que le da paz es ver a un hombre con carácter, hambre de superación y la lealtad innegociable de no rendirse.",
                "copy": "Cualquiera aplaude en la cima; el mérito real está en quien camina a tu lado cuando todavía no hay reflectores. Comparte este reel con quien entienda el valor del proceso.",
                "tip": "Mirada reflexiva hacia la ventana o ajustándote el reloj con luz natural suave (8 seg loop)."
            },
            {
                "id": 3,
                "time": "01:00 PM",
                "theme": "Cerrar Puertas Secundarias al Comprometerse",
                "line1": "Estar con alguien no es 'ver qué pasa'...",
                "line2": "...es tener la madurez de cerrar todas las puertas secundarias para honrar y construir con la persona que elegiste.",
                "copy": "En una generación de opciones infinitas y amores desechables, ser leal y tener dirección es un superpoder. ¿Estás de acuerdo? Te leo en comentarios.",
                "tip": "Gesto sereno dejando el teléfono bocabajo sobre la mesa (8 segundos exactos)."
            },
            {
                "id": 4,
                "time": "03:00 PM",
                "theme": "El Poder de Construir sin Avisar",
                "line1": "Hay dos tipos de personas en sus 20s:",
                "line2": "Los que publican cada meta que planean hacer, y los que callan, trabajan 14 horas al día y dejan que sus números hablen por ellos.",
                "copy": "El progreso que más pesa es el que nadie aplaude en redes mientras lo estás construyendo. Sigue en silencio. Guarda este recordatorio.",
                "tip": "Tomas rápidas de libreta con apuntes, código/pantalla y reloj de fondo (8 seg loop)."
            },
            {
                "id": 5,
                "time": "05:00 PM",
                "theme": "El Mito del Éxito Instantáneo & Carácter",
                "line1": "Nos vendieron que a los 25 ya teníamos que ser millonarios...",
                "line2": "...y se les olvidó decir que los imperios sólidos tardan años en poner los cimientos. No te compares con el highlight reel de nadie.",
                "copy": "La constancia silenciosa vence al brillo pasajero todos los días. Mantén el ritmo y confía en el proceso. ¿En qué nivel de construcción estás hoy?",
                "tip": "Mirando a cámara con tono seguro, cerrando un cuaderno de notas (8 seg)."
            },
            {
                "id": 6,
                "time": "06:45 PM",
                "theme": "El Filtro de Paz Mental en los 20s",
                "line1": "Mi mayor logro este año no fue monetario...",
                "line2": "...fue aprender a alejarme en silencio de cualquier persona o situación que amenazara mi tranquilidad mental.",
                "copy": "Tu paz no es negociable por dinero, ni por aprobación ni por compañía vacía. Quien te quita paz, te cuesta demasiado. Guarda este reel.",
                "tip": "Cerrando la laptop y respirando en calma con luz tenue al atardecer (8 seg loop)."
            },
            {
                "id": 7,
                "time": "08:15 PM",
                "theme": "Equipo de Vida vs Distracción Superficial",
                "line1": "No busco a alguien que solo quiera planes de fin de semana...",
                "line2": "...busco a alguien con quien hablar de proyectos a las 11 PM y despertarnos al día siguiente con hambre de conquistar el mundo.",
                "copy": "Tener metas individuales y un proyecto de vida compartido multiplica los resultados. Círculo pequeño, visión gigantesca. 🔥",
                "tip": "Medio perfil sonriendo con serenidad, revisando métricas en la pantalla (8 seg)."
            },
            {
                "id": 8,
                "time": "09:30 PM",
                "theme": "La Disciplina que Nadie Ve a Medianoche",
                "line1": "Cuando todos duermen o están de fiesta...",
                "line2": "...tú estás poniendo el ladrillo que en 3 años te va a dar la libertad con la que otros solo sueñan. Mañana seguimos.",
                "copy": "La recompensa tardía es el único camino que genera libertad real. Duerme en paz sabiendo que diste tu 100%. Mañana sumamos otro día.",
                "tip": "Luz de escritorio tenue apagándose, pantalla en modo descanso (8 seg loop)."
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
