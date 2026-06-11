"""
METROGLASS Chatbot — Server principal
Porneste cu: uvicorn main:app --reload
"""
import os
import json
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from dotenv import load_dotenv
from calculator import calculeaza_pret, PROFILE, USI_SPECIALE

load_dotenv()

app = FastAPI()

# Permite conexiuni din orice origine (pentru widget pe alt site)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ===========================================================
# SYSTEM PROMPT — Regulile agentului din PDD
# ===========================================================
SYSTEM_PROMPT = """Ești SEPTO, agentul AI al companiei METROGLASS — un chatbot conversațional care ajută vizitatorii site-ului să obțină prețuri orientative pentru ferestre și uși PVC.

## CE FACI:
- Ajuți clienții să înțeleagă diferențele dintre profile, sticle și configurații
- Calculezi prețuri orientative folosind funcția calculeaza_pret (OBLIGATORIU — nu calcula manual)
- Recomanzi varianta optimă raport calitate-preț
- Colectezi datele pentru o cerere de ofertă

## CE NU FACI:
- NU emiți oferte ferme sau contractuale
- NU procesezi comenzi sau plăți
- NU calculezi prețuri pentru forme atipice (arce, trapeze, triunghiuri) — redirecționezi la agent uman
- NU compari prețurile METROGLASS cu concurența numită

## FLUXUL CONVERSAȚIEI:
1. Salut → te prezinți ca SEPTO de la METROGLASS
2. Identifică produsul (fereastră, ușă balcon, ușă exterior, glisantă, etc.)
3. Colectează dimensiuni (lățime × înălțime, în mm sau cm — convertește în mm)
4. Alege profil (sau recomandă pe baza bugetului)
5. Alege sticlă (implicit Low-E dacă nu specifică)
6. Alege culoare (implicit alb)
7. Accesorii opționale
8. CALCULEAZĂ PREȚUL cu funcția calculeaza_pret
9. Propune cerere de ofertă cu vizită de măsurare gratuită

## REGULI ABSOLUTE:
🔴 Comunică ÎNTOTDEAUNA un interval de preț (ex: 1.500–2.000 RON), NICIODATĂ o valoare unică
🔴 La final adaugă: "Prețurile sunt orientative ±15–20%. Prețul final se stabilește după măsurare gratuită la fața locului."
🔴 NU compara prețurile cu concurența numită
🔴 REFUZĂ forme atipice → "Vă redirecționez către un consultant METROGLASS"

## LOGICA DE RECOMANDARE PE BUGET:
- Sub 300 RON/mp → Schtruber 4 camere sau Teraplast TP 4000
- 300–400 RON/mp → Ramplast Solid 400/500 sau Profilink Clasic 60
- 400–550 RON/mp → Profilink Premium 70, Ramplast Solid 700, Teraplast TP 6000
- 550–650 RON/mp → Profilink Nolix 82, Salamander Streamline 76
- Peste 650 RON/mp → Salamander BluEvolution 92 sau Aluminiu Profilink Termo

## GHIDARE CONVERSAȚIE:
- Client menționează condens → recomandă grilă ventilație + sticlă Low-E/4 Anotimpuri
- Client menționează zgomot → recomandă 6+ camere + tripan
- Client menționează eficiență energetică → recomandă 7 camere + tripan 4 Anotimpuri
- Client menționează efracție → recomandă feronerie antiefracție + sticlă securizată
- Client are 3+ produse → sugerează cerere de ofertă completă

## FURNIZORI DISPONIBILI:
Schtruber (Turcia, economic), Teraplast (România), Rauch (Turcia), Ramplast (România),
Profilink (Bulgaria), Salamander (Germania, premium), Profilink Aluminiu Termo (Bulgaria, top)

## TIPURI STICLĂ:
Float clar (basic), Low-E (standard implicit), 4 Anotimpuri (selectiv),
Tripan standard, Tripan 4 Anotimpuri (pasiv), Securizată

## CULORI:
Alb (standard), Stejar auriu, Stejar închis/Nuc, Mahon, Gri antracit,
Interior alb + exterior colorat, RAL personalizat

## ACCESORII:
Grilă ventilație (80 RON/buc), Feronerie Roto premium (120 RON/canat),
Feronerie antiefracție cls.2 (180 RON/canat), Glaf interior PVC (40 RON/ml),
Glaf exterior aluminiu (80 RON/ml), Plasă antiinsecte (90 RON/canat),
Rulou exterior (350–500 RON/mp), Plasă plise (180 RON/mp)

## TON:
Vorbești în română, prietenos și profesional. Eviți jargonul tehnic cu clienți normali,
dar îl folosești corect când interlocutorul arată expertiză.
Dacă clientul nu menționează un profil, recomandă activ varianta cu cel mai bun raport calitate-preț.

## CÂND FOLOSEȘTI FUNCȚIA calculeaza_pret:
- De FIECARE DATĂ când ai suficiente date pentru un calcul (minim: dimensiuni + furnizor + camere)
- Dacă clientul nu specifică sticla → folosește "low_e"
- Dacă nu specifică culoarea → folosește "alb"
- Dacă nu specifică deschiderea → folosește "oscilobatant"
- Dacă nu specifică canate → folosește "1_canat"
- Convertește ÎNTOTDEAUNA cm în mm (ex: 120 cm = 1200 mm)
"""

# ===========================================================
# DEFINITIA TOOL-ULUI PENTRU OPENAI
# ===========================================================
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "calculeaza_pret",
            "description": "Calculeaza pretul orientativ pentru o fereastra sau usa PVC. Apeleaza INTOTDEAUNA aceasta functie cand ai dimensiuni si profil. NU calcula manual.",
            "parameters": {
                "type": "object",
                "properties": {
                    "latime_mm": {
                        "type": "number",
                        "description": "Latimea golului din perete in milimetri (ex: 1200)"
                    },
                    "inaltime_mm": {
                        "type": "number",
                        "description": "Inaltimea golului in milimetri (ex: 1400)"
                    },
                    "furnizor": {
                        "type": "string",
                        "enum": ["Schtruber", "Teraplast", "Rauch", "Ramplast", "Profilink", "Salamander", "Profilink Aluminiu"],
                        "description": "Furnizorul de profil PVC"
                    },
                    "camere": {
                        "type": "integer",
                        "enum": [4, 5, 6, 7],
                        "description": "Numarul de camere al profilului"
                    },
                    "deschidere": {
                        "type": "string",
                        "enum": ["fix", "batant", "oscilobatant", "oscilant"],
                        "description": "Tipul de deschidere. Default: oscilobatant"
                    },
                    "canate": {
                        "type": "string",
                        "enum": ["1_canat", "2_canate_1fix_1ob", "2_canate_2ob", "3_canate_1fix_2ob", "3_canate_3ob"],
                        "description": "Configuratia de canate. Default: 1_canat"
                    },
                    "culoare": {
                        "type": "string",
                        "enum": ["alb", "stejar_auriu", "stejar_inchis", "nuc", "mahon", "gri_antracit", "interior_alb_exterior_color", "ral_personalizat"],
                        "description": "Culoarea profilului. Default: alb"
                    },
                    "sticla": {
                        "type": "string",
                        "enum": ["float_standard", "low_e", "4_anotimpuri", "tripan_standard", "tripan_4_anotimpuri", "securizata"],
                        "description": "Tipul de sticla. Default: low_e"
                    },
                    "accesorii_lista": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": ["grila_ventilatie", "sticla_ornamentala", "feronerie_roto_premium", "feronerie_antiefractie", "glaf_interior_pvc", "glaf_exterior_aluminiu", "plasa_antiinsecte", "rulou_exterior", "plasa_plise"]
                        },
                        "description": "Lista de accesorii optionale"
                    },
                    "cantitate_accesorii": {
                        "type": "object",
                        "description": "Cantitati per accesoriu (ex: {glaf_interior_pvc: 1.2} pentru 1.2 ml). Default: 1 per accesoriu."
                    }
                },
                "required": ["latime_mm", "inaltime_mm", "furnizor", "camere"]
            }
        }
    }
]


# ===========================================================
# ENDPOINT-URI
# ===========================================================

@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    """Serveste pagina de chat."""
    return FileResponse("index.html")


@app.get("/widget.js")
async def serve_widget():
    """Serveste scriptul widget pentru integrare pe site-uri externe."""
    return FileResponse("widget.js", media_type="application/javascript")


@app.post("/chat")
async def chat(request: Request):
    """
    Primeste mesajul utilizatorului + istoricul conversatiei.
    Returneaza raspunsul agentului.
    """
    body = await request.json()
    user_message = body.get("message", "")
    history = body.get("history", [])

    # Construieste mesajele pentru OpenAI
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(history)
    messages.append({"role": "user", "content": user_message})

    # Apel OpenAI cu tool calling
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # Ieftin si rapid. Schimba cu "gpt-4o" daca vrei mai bun.
        messages=messages,
        tools=TOOLS,
        tool_choice="auto",
        temperature=0.7,
    )

    assistant_msg = response.choices[0].message

    # Daca agentul vrea sa apeleze functia de calcul
    if assistant_msg.tool_calls:
        tool_call = assistant_msg.tool_calls[0]
        args = json.loads(tool_call.function.arguments)

        # Apeleaza calculatorul nostru Python
        rezultat = calculeaza_pret(**args)

        # Trimite rezultatul inapoi la OpenAI ca sa formuleze raspunsul
        messages.append(assistant_msg.model_dump())
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": json.dumps(rezultat, ensure_ascii=False)
        })

        # OpenAI formuleaza raspunsul final in romana
        response2 = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7,
        )
        final_text = response2.choices[0].message.content

        return {
            "response": final_text,
            "calcul": rezultat,
        }

    # Raspuns fara tool call (intrebari generale, salut, etc.)
    return {
        "response": assistant_msg.content,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
