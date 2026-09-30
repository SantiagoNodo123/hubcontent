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
    """Generates the 8 daily scripts for @s_thiago7."""
    return [
        {
            "id": 1,
            "time": "09:30 AM",
            "theme": "Percepción vs. Realidad",
            "line1": "La gente jura que uno tiene 10 opciones y no le falta nada...",
            "line2": "...cuando la realidad es que llego a mi casa cansado, le pido a Dios por mi futuro y me duermo con la mente en 100 proyectos.",
            "copy": "Las apariencias engañan demasiado. ¿A quién más le pasa?",
            "tip": "Grábate mirando la laptop o tomando café en silencio (6 a 8 seg)."
        },
        {
            "id": 2,
            "time": "11:00 AM",
            "theme": "Citas & Generación",
            "line1": "¿Cómo que 'por qué estás tan solo si eres buen partido'?",
            "line2": "...porque en esta generación si muestras interés se aburren, y si eres sincero creen que estás mintiendo JAJAJA.",
            "copy": "Nadie sabe qué quiere en estos tiempos 🥲. Confirmar aquí abajo 👇",
            "tip": "Sonrisa irónica breve mirando el celular y dejándolo a un lado."
        },
        {
            "id": 3,
            "time": "01:00 PM",
            "theme": "Conexión Real",
            "line1": "Qué difícil es conectar con alguien hoy en día...",
            "line2": "...cuando no te interesa la fiesta de cada fin de semana y tus temas de conversación son metas, negocios y paz mental.",
            "copy": "Ojalá existieran más personas con ganas de construir en vez de solo aparentar.",
            "tip": "Caminando de espaldas o en cafetería tranquila."
        },
        {
            "id": 4,
            "time": "03:00 PM",
            "theme": "Madurez & Filtro",
            "line1": "No le tengo miedo a quedarme soltero en mis 20s...",
            "line2": "...le tengo miedo a juntarme con alguien que no tenga metas, no sume a mi paz y solo me haga perder el tiempo.",
            "copy": "Estar solo es mil veces mejor que estar con alguien sin dirección.",
            "tip": "Mirada reflexiva por una ventana o auto."
        },
        {
            "id": 5,
            "time": "05:00 PM",
            "theme": "Tranquilidad",
            "line1": "Me dicen 'eres muy frío para el amor'...",
            "line2": "...no soy frío, simplemente me costó mucho construir mi tranquilidad como para regalársela a cualquiera.",
            "copy": "Cuidar la paz no es orgullo, es madurar.",
            "tip": "Cerrando la laptop o acomodándote la chaqueta."
        },
        {
            "id": 6,
            "time": "06:45 PM",
            "theme": "Formato 'Empiezo yo'",
            "line1": "Cosas de las que nadie habla al madurar:\nEmpiezo yo:",
            "line2": "Dejar de buscar parejas para llenar vacíos y empezar a buscar socios de vida con los que construir un imperio.",
            "copy": "¿Cuál ha sido tu mayor cambio de mentalidad? Te leo 👇",
            "tip": "Mirando a cámara con tono sincero."
        },
        {
            "id": 7,
            "time": "08:15 PM",
            "theme": "Enfoque Financiero",
            "line1": "Dicen que el amor llega cuando menos lo buscas...",
            "line2": "...yo no lo estoy buscando porque estoy ocupado buscando la libertad financiera antes de los 30 😂",
            "copy": "Prioridades claras. ¿Quién más en el mismo enfoque?",
            "tip": "Risa breve o tecleando de noche."
        },
        {
            "id": 8,
            "time": "09:30 PM",
            "theme": "Cierre Nocturno",
            "line1": "Al final del día no necesitas a 20 personas detrás de ti...",
            "line2": "...necesitas una sola que entienda tus silencios, apoye tus metas y camine a tu lado en las buenas y en las malas.",
            "copy": "Pocos pero reales. Buenas noches 🔥",
            "tip": "Cerrando la jornada, luz tenue."
        }
    ]

def generate_nodo_plan():
    """Generates the 2 B2B scripts for @nodo_tg (conectanodo.com)."""
    return [
        {
            "id": 1,
            "time": "12:30 PM",
            "theme": "El Cementerio de Ventas B2B",
            "line1": "El cementerio de ventas de las empresas de servicios:",
            "line2": "Enviar una cotización en PDF por WhatsApp y jamás volver a hacerle un seguimiento estructurado. El 60% de tus ventas se pierden en el silencio.",
            "copy": "Tus comerciales no necesitan más prospectos desordenados, necesitan una ruta de seguimiento medible. En NODO integramos Kommo CRM y WhatsApp API para que ninguna propuesta se quede en el olvido. Conoce el Método NODO RUTA en conectanodo.com",
            "tip": "Tomas estéticas de un correo con un archivo PDF y luego un dashboard de CRM en pantalla."
        },
        {
            "id": 2,
            "time": "07:30 PM",
            "theme": "El Riesgo de WhatsApp Personal",
            "line1": "El mayor riesgo operativo en una empresa B2B:",
            "line2": "Que tus clientes vivan en los WhatsApps personales de tus asesores. Si el asesor se va, tu base de datos se va con él.",
            "copy": "Centralizar la captación no es microgestión, es proteger la infraestructura de tu negocio. Diseñamos sistemas donde cada mensaje y cotización queda en tu CRM oficial. Diagnóstico en conectanodo.com",
            "tip": "Tomas de flujos en pantalla (n8n, Kommo CRM) y teclado en oficina."
        }
    ]
