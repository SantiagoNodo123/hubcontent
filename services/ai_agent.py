import os
import sys
import json
import requests

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(BASE_DIR, "data", "config.json")
STRATEGY_PATH = os.path.join(BASE_DIR, "data", "analytics", "strategies", "latest_strategy.json")
SCORES_PATH = os.path.join(BASE_DIR, "data", "analytics", "scores", "latest_scores.json")

ENV_PATH = os.path.join(BASE_DIR, ".env")

def get_gemini_api_key():
    """Retrieve Gemini API Key from environment, .env file, or data/config.json."""
    env_key = os.environ.get("GEMINI_API_KEY")
    if env_key and env_key.strip():
        return env_key.strip()
        
    if os.path.exists(ENV_PATH):
        try:
            with open(ENV_PATH, "r", encoding="utf-8") as f:
                for line in f:
                    if line.startswith("GEMINI_API_KEY="):
                        val = line.split("=", 1)[1].strip().strip('"').strip("'")
                        if val:
                            return val
        except Exception as e:
            print(f"[AI Agent] Error reading .env: {e}")
    
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                gemini_cfg = cfg.get("gemini", {})
                key = gemini_cfg.get("api_key", "").strip()
                if key:
                    return key
        except Exception as e:
            print(f"[AI Agent] Error reading config for Gemini key: {e}")
            
    return None

def save_gemini_api_key(api_key: str):
    """Save Gemini API Key to gitignored .env file and data/config.json."""
    clean_key = api_key.strip()
    
    # Save to .env (secure, not pushed to git)
    try:
        with open(ENV_PATH, "w", encoding="utf-8") as f:
            f.write(f"GEMINI_API_KEY={clean_key}\n")
    except Exception as e:
        print(f"[AI Agent] Error writing .env: {e}")

    # Update config.json metadata without exposing secret
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            if "gemini" not in cfg:
                cfg["gemini"] = {}
            cfg["gemini"]["api_key"] = ""
            cfg["gemini"]["model"] = "gemini-3.8-flash"
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(cfg, f, indent=2)
        except Exception:
            pass
        
    return True
        
    return True

def _call_gemini_api(prompt: str, system_instruction: str = "", model: str = "gemini-3.8-flash", api_key: str = None):
    """
    Call Google AI Studio Gemini API with fallback cascade:
    gemini-3.8-flash -> gemini-2.5-flash -> gemini-2.0-flash -> gemini-1.5-flash
    """
    key = api_key or get_gemini_api_key()
    if not key:
        raise ValueError("No se ha configurado ninguna API Key de Google Studio (Gemini).")

    candidate_models = [model]
    for fallback in ["gemini-3.8-flash", "gemini-3.5-flash", "gemini-3.7-flash", "gemini-flash-latest"]:
        if fallback not in candidate_models:
            candidate_models.append(fallback)

    last_error = None
    for current_model in candidate_models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{current_model}:generateContent?key={key}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": prompt}]
                }
            ],
            "generationConfig": {
                "temperature": 0.75,
                "responseMimeType": "application/json"
            }
        }
        
        if system_instruction:
            payload["systemInstruction"] = {
                "parts": [{"text": system_instruction}]
            }

        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=30)
            if resp.status_code == 200:
                data = resp.json()
                text_content = data["candidates"][0]["content"]["parts"][0]["text"]
                return json.loads(text_content), current_model
            else:
                # If error (400, 404, 429, 503 etc.), record and try next candidate model
                last_error = f"Model {current_model} returned {resp.status_code}: {resp.text[:200]}"
                continue
        except requests.exceptions.Timeout:
            last_error = "Timeout al conectar con la API de Gemini (30s)."
            continue
        except Exception as e:
            last_error = str(e)
            continue

    raise RuntimeError(f"Error al invocar Gemini API: {last_error}")

def get_virality_context(account: str = "personal"):
    """Extract context metrics from latest strategy and scored posts."""
    context = {
        "winner_title": "Enfoque, disciplina y prioridades claras en los 20s",
        "winner_stats": "47,473 vistas · 805 guardados · 1,025 reposts · 41.2% skip",
        "top_keywords": ["disciplina", "carácter", "enfoque", "prioridades", "pareja", "piso cero", "proceso"],
        "account": account
    }
    
    if os.path.exists(STRATEGY_PATH):
        try:
            with open(STRATEGY_PATH, "r", encoding="utf-8") as f:
                strat = json.load(f)
                acc_strat = strat.get(account, {})
                if acc_strat:
                    context["winner_title"] = acc_strat.get("winner_title", context["winner_title"])
                    context["winner_stats"] = acc_strat.get("winner_stats", context["winner_stats"])
                    context["why_winner"] = acc_strat.get("why_winner", "")
                    context["renewed_focus"] = acc_strat.get("renewed_focus", "")
        except Exception:
            pass

    return context

def generate_reels_with_ai(account: str = "personal", angle: str = "record", tone: str = "santiago", 
                           custom_prompt: str = "", count: int = 8, model: str = "gemini-3.8-flash", 
                           api_key: str = None):
    """
    Generate 8 custom Reels scripts using Gemini AI trained on Santiago Quevedo / Nodo voice tone
    and proven 8-second visual loop formats.
    """
    context = get_virality_context(account)
    
    # Define angle descriptors
    angle_descriptions = {
        "record": "Viralidad Récord (48K vistas): Enfoque absoluto, disciplina en los 20s, alejarse del ruido, lealtad y construir en silencio.",
        "piso_cero": "Construir desde el Piso Cero (4K vistas): El valor del carácter vs el saldo bancario. Encontrar a quien camine a tu lado cuando no hay reflectores.",
        "compromiso": "Compromiso Real (36% skip rate): Madurez de cerrar puertas secundarias para honrar a quien elegiste. Relaciones con propósito vs amores desechables.",
        "mixer": "Angle Mixer (Negocios & Tech x Pareja de Alto Valor): Fusionar la mentalidad empresarial con tener una compañera de vida que multiplique la visión.",
        "silencio": "Ejecución Silenciosa: No avisar metas. Trabajar 14 horas al día en silencio y dejar que los números y el estilo de vida hablen.",
        "custom": custom_prompt if custom_prompt else "Ángulo libre optimizado para retención y viralidad orgánica."
    }
    selected_angle_desc = angle_descriptions.get(angle, angle_descriptions["record"])
    
    # Define tone descriptors
    tone_descriptions = {
        "santiago": "Tono oficial Santiago Quevedo: Maduro, sobrio, contundente, sin humo ni frases cliché, directo al pecho, habla desde el proceso real de un hombre en sus 20s construyendo.",
        "debate": "Tono Controversial & Polarizante: Rompe consensos tibios de la sociedad moderna, cuestiona la falta de lealtad, la inmadurez y las excusas de forma implacable.",
        "educativo": "Tono Estratégico & Mentalidad: Estructura clara, principios inquebrantables de crecimiento personal, enfoque de negocio y ejecución táctica."
    }
    selected_tone_desc = tone_descriptions.get(tone, tone_descriptions["santiago"])
    
    system_instruction = f"""
Eres el Director de Contenido y Guionista de Inteligencia Artificial para Santiago Quevedo (@s_thiago7) y NODO Tech Growth.
Tu objetivo es redactar exactamente {count} guiones virales de Instagram Reels con la estructura de Retención Máxima (8 Segundos Loop).

REGLAS INFALIBLES DEL FORMATO DE 8 SEGUNDOS:
1. DURACIÓN: 8 segundos exactos en video de fondo (video estético en bucle continuo).
2. LÍNEA 1 (0 a 3 segundos): Gancho visual y auditivo en texto en pantalla. Corto, demoledor, detiene el scroll de inmediato. Quiebra una creencia o plantea una verdad incómoda.
3. LÍNEA 2 (4 a 8 segundos): Remate / Conclusión. Es la justificación o el giro de valor profundo que hace que la persona quiera leer la descripción y guardar el reel.
4. COPY / CAPTION: Descripción de 3 a 5 líneas con reflexión madura, valor condensado y un llamado a la acción (CTA) claro a GUARDAR o COMPARTIR.
5. TIP DE GRABACIÓN (VISUAL LOOP): Instrucción de toma estética cinemática (ej: tomando café con mirada firme, cerrando laptop en penumbra, ajustándose el reloj, caminando con postura decidida).
6. 3 ALTERNATIVE HOOKS: 3 ganchos alternativos para probar en A/B testing (uno directo, uno de pregunta incómoda, uno de contraste/polaridad).

TONO DE VOZ OBLIGATORIO:
{selected_tone_desc}

ÁNGULO ELEGIDO:
{selected_angle_desc}
    """

    user_prompt = f"""
Genera exactamente {count} guiones en formato JSON para la cuenta '{account}'.
Contexto de métricas ganadoras recientes:
- Post Ganador previo: "{context['winner_title']}" ({context['winner_stats']})
- Enfoque temático: {selected_angle_desc}
{f"- Instrucción adicional del usuario: {custom_prompt}" if custom_prompt else ""}

El JSON de salida DEBE ser una lista de {count} objetos con las siguientes claves exactas:
[
  {{
    "id": 1,
    "time": "09:30 AM",
    "theme": "Nombre o concepto del reel",
    "line1": "Texto en pantalla Línea 1 (0-3s)",
    "line2": "Texto en pantalla Línea 2 (4-8s)",
    "copy": "Texto completo para el pie de foto de Instagram con llamado a guardar",
    "tip": "Instrucción de grabación estética para bucle de 8s",
    "alternative_hooks": [
      "Gancho A (Directo y contundente)",
      "Gancho B (Pregunta incómoda)",
      "Gancho C (Contraste o paradoja)"
    ]
  }},
  ...
]
Devuelve ÚNICAMENTE el array JSON válido sin texto adicional.
    """

    try:
        data, used_model = _call_gemini_api(user_prompt, system_instruction, model=model, api_key=api_key)
        
        # Validate structure
        reels_list = data if isinstance(data, list) else data.get("reels", data.get("plan", []))
        if not reels_list:
            raise ValueError("Respuesta de Gemini no contiene una lista de guiones.")
            
        times = ["09:30 AM", "11:00 AM", "01:00 PM", "03:00 PM", "05:00 PM", "06:45 PM", "08:15 PM", "09:30 PM"]
        for idx, item in enumerate(reels_list):
            item["id"] = idx + 1
            if "time" not in item or not item["time"]:
                item["time"] = times[idx % len(times)]
                
        return {
            "success": True,
            "engine": f"Gemini ({used_model})",
            "model": used_model,
            "angle": angle,
            "tone": tone,
            "reels": reels_list
        }
    except Exception as e:
        print(f"[AI Agent] Fallback to internal engine due to: {e}")
        # Graceful fallback: generate customized reels using our rich analytics engine templates
        fallback_reels = _generate_algorithmic_reels(angle, tone, custom_prompt, count)
        return {
            "success": True,
            "engine": "Algorithmic Virality Engine (Offline/Fallback)",
            "model": "internal-pattern-generator",
            "warning": f"Generado con motor interno (Motivo: {str(e)})",
            "angle": angle,
            "tone": tone,
            "reels": fallback_reels
        }

def generate_hook_variations(hook: str, theme: str = "", tone: str = "santiago", 
                             model: str = "gemini-3.8-flash", api_key: str = None):
    """
    Generate 3 alternative high-retention hooks for A/B testing a specific reel.
    """
    system_instruction = """
Eres un especialista en retención de video corto (Instagram Reels y TikTok).
Tu especialidad es redactar ganchos visuales/textuales de 0 a 3 segundos que detienen el scroll al 100%.
Debes generar exactamente 3 ganchos alternativos para el concepto dado.
    """
    
    prompt = f"""
Gancho actual: "{hook}"
Tema / Concepto: "{theme}"
Tono: {tone}

Genera un JSON con exactamente 3 variantes de gancho:
1. Directo y contundente (afirmación cruda)
2. Pregunta incómoda (apunta a una inseguridad o dilema real)
3. Contraste o paradoja (A vs B)

Devuelve JSON con la estructura:
{{
  "variations": [
    {{"type": "Directo", "hook": "..."}},
    {{"type": "Pregunta Incómoda", "hook": "..."}},
    {{"type": "Contraste / Paradoja", "hook": "..."}}
  ]
}}
    """
    try:
        data, used_model = _call_gemini_api(prompt, system_instruction, model=model, api_key=api_key)
        return {
            "success": True,
            "model": used_model,
            "variations": data.get("variations", [])
        }
    except Exception as e:
        # Algorithmic variations fallback
        return {
            "success": True,
            "model": "internal-fallback",
            "variations": [
                {"type": "Directo", "hook": f"La verdad incómoda sobre {theme.lower() or 'esto'} que nadie te dice a los 20s:"},
                {"type": "Pregunta Incómoda", "hook": f"¿Estás construyendo en serio o solo publicando que vas a construir?"},
                {"type": "Contraste / Paradoja", "hook": f"Muchos quieren los resultados, pero huyen del proceso de estar en silencio."}
            ]
        }

def _generate_algorithmic_reels(angle: str, tone: str, custom_prompt: str = "", count: int = 8):
    """Internal backup generator when API key is not yet set or offline."""
    templates = [
        {
            "theme": "Cero Tolerancia a Perder el Tiempo en los 20s",
            "line1": "A los 20s no pierdes amigos por cambiar de actitud...",
            "line2": "...los pierdes porque cuando tu prioridad es construir libertad, ya no encajas en conversaciones de fiesta y chisme.",
            "copy": "Incomodar con tu disciplina es la señal más clara de que vas por el camino correcto. Menos ruido, más enfoque. ¿Quién más en esta misma sintonía? Guarda este reel.",
            "tip": "Grábate caminando con café o sentado frente a la laptop con postura firme (8 seg loop sin cortes).",
            "alternative_hooks": [
                "Tu círculo de amigos se reduce cuando tus metas se multiplican.",
                "¿Por qué te da miedo quedarte solo un viernes por la noche?",
                "Fiesta cada fin de semana vs 3 años de enfoque absoluto."
            ]
        },
        {
            "theme": "El Valor de Construir desde el Piso Cero",
            "line1": "La mujer correcta no te exige una vida resuelta a los 26...",
            "line2": "...lo que le da paz es ver a un hombre con carácter, hambre de superación y la lealtad innegociable de no rendirse.",
            "copy": "Cualquiera aplaude en la cima; el mérito real está en quien camina a tu lado cuando todavía no hay reflectores. Comparte este reel con quien entienda el valor del proceso.",
            "tip": "Mirada reflexiva hacia la ventana o ajustándote el reloj con luz natural suave (8 seg loop).",
            "alternative_hooks": [
                "El saldo bancario sube y baja; el carácter se forja en el proceso.",
                "¿Prefieres una relación fácil hoy o un equipo indestructible a largo plazo?",
                "Quien no te quiso en el piso cero, no tiene boleto para el penthouse."
            ]
        },
        {
            "theme": "Cerrar Puertas Secundarias al Comprometerse",
            "line1": "Estar con alguien no es 'ver qué pasa'...",
            "line2": "...es tener la madurez de cerrar todas las puertas secundarias para honrar y construir con la persona que elegiste.",
            "copy": "En una generación de opciones infinitas y amores desechables, ser leal y tener dirección es un superpoder. ¿Estás de acuerdo? Te leo en comentarios.",
            "tip": "Gesto sereno dejando el teléfono bocabajo sobre la mesa (8 segundos exactos).",
            "alternative_hooks": [
                "Tener opciones abiertas no es poder, es falta de madurez.",
                "¿Por qué le temen tanto al compromiso en nuestra generación?",
                "Amor desechable vs la decisión consciente de construir un imperio juntos."
            ]
        },
        {
            "theme": "El Poder de Construir sin Avisar",
            "line1": "Hay dos tipos de personas en sus 20s:",
            "line2": "Los que publican cada meta que planean hacer, y los que callan, trabajan 14 horas al día y dejan que sus números hablen por ellos.",
            "copy": "El progreso que más pesa es el que nadie aplaude en redes mientras lo estás construyendo. Sigue en silencio. Guarda este recordatorio.",
            "tip": "Tomas rápidas de libreta con apuntes, código/pantalla y reloj de fondo (8 seg loop).",
            "alternative_hooks": [
                "Deja de pedir aplausos por cosas que apenas estás planeando.",
                "¿Cuánto tiempo pierdes intentando impresionar a gente que no suma?",
                "Hablar de éxito en redes vs construirlo en silencio a las 11 PM."
            ]
        },
        {
            "theme": "El Mito del Éxito Instantáneo & Carácter",
            "line1": "Nos vendieron que a los 25 ya teníamos que ser millonarios...",
            "line2": "...y se les olvidó decir que los imperios sólidos tardan años en poner los cimientos. No te compares con el highlight reel de nadie.",
            "copy": "La constancia silenciosa vence al brillo pasajero todos los días. Mantén el ritmo y confía en el proceso. ¿En qué nivel de construcción estás hoy?",
            "tip": "Mirando a cámara con tono seguro, cerrando un cuaderno de notas (8 seg).",
            "alternative_hooks": [
                "Compararte con extraños en internet está destruyendo tu enfoque.",
                "¿Por qué quieres la recompensa del año 10 en tu mes número 3?",
                "Fama rápida de 15 minutos vs solidez patrimonial de por vida."
            ]
        },
        {
            "theme": "El Filtro de Paz Mental en los 20s",
            "line1": "Mi mayor logro este año no fue monetario...",
            "line2": "...fue aprender a alejarme en silencio de cualquier persona o situación que amenazara mi tranquilidad mental.",
            "copy": "Tu paz no es negociable por dinero, ni por aprobación ni por compañía vacía. Quien te quita paz, te cuesta demasiado. Guarda este reel.",
            "tip": "Cerrando la laptop y respirando en calma con luz tenue al atardecer (8 seg loop).",
            "alternative_hooks": [
                "Lo que te roba la paz mental te está saliendo demasiado caro.",
                "¿Hasta cuándo vas a tolerar círculos que drenan tu energía?",
                "Tener dinero sin tranquilidad vs construir libertad con paz absoluta."
            ]
        },
        {
            "theme": "Equipo de Vida vs Distracción Superficial",
            "line1": "No busco a alguien que solo quiera planes de fin de semana...",
            "line2": "...busco a alguien con quien hablar de proyectos a las 11 PM y despertarnos al día siguiente con hambre de conquistar el mundo.",
            "copy": "Tener metas individuales y un proyecto de vida compartido multiplica los resultados. Círculo pequeño, visión gigantesca. 🔥",
            "tip": "Medio perfil sonriendo con serenidad, revisando métricas en la pantalla (8 seg).",
            "alternative_hooks": [
                "La pareja que eliges es la decisión financiera y mental más importante.",
                "¿Tu relación actual te impulsa o te frena?",
                "Planes superficiales de discoteca vs noches planeando el futuro juntos."
            ]
        },
        {
            "theme": "La Disciplina que Nadie Ve a Medianoche",
            "line1": "Cuando todos duermen o están de fiesta...",
            "line2": "...tú estás poniendo el ladrillo que en 3 años te va a dar la libertad con la que otros solo sueñan. Mañana seguimos.",
            "copy": "La recompensa tardía es el único camino que genera libertad real. Duerme en paz sabiendo que diste tu 100%. Mañana sumamos otro día.",
            "tip": "Luz de escritorio tenue apagándose, pantalla en modo descanso (8 seg loop).",
            "alternative_hooks": [
                "La soledad del proceso es el peaje que pagas por la libertad.",
                "¿Tienes la disciplina de trabajar cuando nadie te está mirando?",
                "Diversión inmediata hoy vs libertad financiera mañana."
            ]
        }
    ]
    
    times = ["09:30 AM", "11:00 AM", "01:00 PM", "03:00 PM", "05:00 PM", "06:45 PM", "08:15 PM", "09:30 PM"]
    for idx, item in enumerate(templates):
        item["id"] = idx + 1
        item["time"] = times[idx]
        
    return templates[:count]


def generate_b2b_custom_reels(angulo="Dolor Operativo", tono="Controversial", instruccion=""):
    """Genera exactamente los 3 Reels B2B del dia en formato JSON ultrarrapido (2-3 segundos)"""
    prompt = f"""Eres el director de contenido de NODO (conectanodo.com), especialistas en automatizacion comercial con WhatsApp API, agentes de IA y Kommo CRM.
Tu tarea es redactar exactamente los 3 guiones de Reels B2B de hoy (formato 8s ganador de alta retencion para compartir).

PARAMETROS DEL CLIENTE:
- Angulo B2B: {angulo}
- Tono de voz: {tono}
- Enfoque o instruccion extra: {instruccion if instruccion else 'Friccion en ventas y WhatsApp'}

Responde UNICAMENTE con un arreglo JSON valido con esta estructura exacta (sin texto previo ni explicaciones):
[
  {{
    "slot": "Reel B2B #1",
    "time": "12:30 PM",
    "title": "Titulo contundente del Reel 1",
    "hook": "Frase gancho para loop de 8 segundos entre comillas",
    "copy": "Copy B2B persuasivo con llamado a la accion a conectanodo.com",
    "visual": "Tomas en loop de WhatsApp y pipeline de ventas (8 segundos)"
  }},
  {{
    "slot": "Reel B2B #2",
    "time": "04:30 PM",
    "title": "Titulo contundente del Reel 2",
    "hook": "Frase gancho para loop de 8 segundos entre comillas",
    "copy": "Copy B2B persuasivo con llamado a la accion a conectanodo.com",
    "visual": "Tomas de flujo automatizado respondiendo en tiempo real"
  }},
  {{
    "slot": "Reel B2B #3",
    "time": "07:30 PM",
    "title": "Titulo contundente del Reel 3",
    "hook": "Frase gancho para loop de 8 segundos entre comillas",
    "copy": "Copy B2B persuasivo con llamado a la accion a conectanodo.com",
    "visual": "Tomas de notificaciones de cierres de venta en CRM"
  }}
]
"""
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt)
        text = response.text.strip()
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()
        return json.loads(text)
    except Exception as e:
        print(f"Error generando reels B2B: {e}")
        # Fallback de seguridad
        return [
            {
                "slot": "Reel B2B #1", "time": "12:30 PM",
                "title": f"El Error en {angulo}",
                "hook": f"\"El 80% de las empresas fallan en {instruccion if instruccion else 'su proceso comercial'}: responden tarde y pierden el cliente en 5 minutos.\"",
                "copy": "Automatiza la captacion y califica prospectos con WhatsApp API y Kommo CRM. Diagnostico en conectanodo.com",
                "visual": "Loop de pantalla con chats desatendidos vs calificados por IA."
            },
            {
                "slot": "Reel B2B #2", "time": "04:30 PM",
                "title": f"Rompiendo el Mito: {tono}",
                "hook": "\"Tu problema no es de trafico, es que no tienes un pipeline que convierta leads en citas de venta en menos de 60 segundos.\"",
                "copy": "No dejes que tus ventas dependan de respuestas manuales. Visita conectanodo.com",
                "visual": "Transicion rapida de leads entrando a reuniones agendadas."
            },
            {
                "slot": "Reel B2B #3", "time": "07:30 PM",
                "title": "IA vs Procesos Manuales",
                "hook": "\"Mientras tu equipo sigue pegado al celular respondiendo a las 10 PM, tu competencia cierra negocios con agentes de IA.\"",
                "copy": "Integra agentes de IA conectados a tu CRM en conectanodo.com",
                "visual": "Panel de Kommo CRM actualizandose solo."
            }
        ]
