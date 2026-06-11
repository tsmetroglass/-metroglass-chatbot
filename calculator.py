"""
Calculator preturi tamplarie PVC — METGLASS
Logica de business extrasa din PDD v1.0

Toate preturile sunt orientative, fara TVA, fara montaj.
"""

# ===========================================================
# CATALOGUL DE PROFILE SI PRETURI DE BAZA (RON/mp)
# Cheie: (furnizor, camere) → (pret_min, pret_max)
# ===========================================================
PROFILE = {
    # Schtruber — segment economic
    ("Schtruber", 4): {"min": 200, "max": 300, "segment": "Economic"},
    ("Schtruber", 5): {"min": 250, "max": 350, "segment": "Economic"},

    # Teraplast — economic la premium
    ("Teraplast", 4): {"min": 250, "max": 350, "segment": "Economic", "profil": "TP 4000"},
    ("Teraplast", 6): {"min": 400, "max": 500, "segment": "Premium", "profil": "TP 6000"},
    ("Teraplast", 7): {"min": 600, "max": 700, "segment": "Premium+", "profil": "TP 7000"},

    # Rauch
    ("Rauch", 5): {"min": 300, "max": 400, "segment": "Mediu", "profil": "Capela 70"},
    ("Rauch", 7): {"min": 450, "max": 550, "segment": "Mediu-superior", "profil": "Artic 85"},

    # Ramplast
    ("Ramplast", 4): {"min": 300, "max": 400, "segment": "Mediu-superior", "profil": "Solid 400"},
    ("Ramplast", 5): {"min": 400, "max": 500, "segment": "Premium", "profil": "Solid 500"},
    ("Ramplast", 6): {"min": 400, "max": 500, "segment": "Premium", "profil": "Solid 700/800"},

    # Profilink
    ("Profilink", 4): {"min": 300, "max": 400, "segment": "Premium", "profil": "Clasic 60"},
    ("Profilink", 5): {"min": 400, "max": 500, "segment": "Premium", "profil": "Premium 70"},
    ("Profilink", 7): {"min": 560, "max": 660, "segment": "Premium+", "profil": "Nolix 82"},

    # Salamander
    ("Salamander", 5): {"min": 450, "max": 550, "segment": "Premium", "profil": "Streamline 76"},
    ("Salamander", 6): {"min": 500, "max": 600, "segment": "Premium", "profil": "BluEvolution 82"},
    ("Salamander", 7): {"min": 650, "max": 750, "segment": "Premium+", "profil": "BluEvolution 92"},

    # Aluminiu Profilink Termo
    ("Profilink Aluminiu", 7): {"min": 900, "max": 1100, "segment": "Premium+", "profil": "Orbis 71"},
}


# ===========================================================
# COEFICIENTI
# ===========================================================
COEF_DESCHIDERE = {
    "fix":    1.00,
    "batant": 1.15,
    "oscilobatant": 1.20,
    "oscilant": 1.10,
}

COEF_CANATE = {
    "1_canat":           1.00,
    "2_canate_1fix_1ob": 1.80,
    "2_canate_2ob":      2.00,
    "3_canate_1fix_2ob": 2.70,
    "3_canate_3ob":      3.00,
}

COEF_CULOARE = {
    "alb":              1.00,
    "stejar_auriu":     1.15,
    "stejar_inchis":    1.15,
    "nuc":              1.15,
    "mahon":            1.15,
    "gri_antracit":     1.20,
    "interior_alb_exterior_color": 1.25,
    "ral_personalizat": 1.30,
}

COEF_STICLA = {
    "float_standard":       1.00,
    "low_e":                1.12,
    "4_anotimpuri":         1.17,
    "tripan_standard":      1.40,
    "tripan_4_anotimpuri":  1.60,
    "securizata":           1.22,
}

ACCESORII = {
    "grila_ventilatie":       {"pret": 80,  "per": "bucata"},
    "sticla_ornamentala":     {"pret": 80,  "per": "bucata"},
    "feronerie_roto_premium": {"pret": 120, "per": "canat_mobil"},
    "feronerie_antiefractie": {"pret": 180, "per": "canat_mobil"},
    "glaf_interior_pvc":      {"pret": 40,  "per": "ml"},
    "glaf_exterior_aluminiu": {"pret": 80,  "per": "ml"},
    "plasa_antiinsecte":      {"pret": 90,  "per": "canat"},
    "rulou_exterior":         {"pret_min": 350, "pret_max": 500, "per": "mp"},
    "plasa_plise":            {"pret": 180, "per": "mp"},
}

# Preturi fixe usi speciale (RON)
USI_SPECIALE = {
    "usa_balcon_ob":         {"min": 1200, "max": 1900, "dim_ref": "900x2100"},
    "usa_exterior_geam":     {"min": 1800, "max": 2800, "dim_ref": "900x2100"},
    "usa_exterior_panou":    {"min": 2200, "max": 3800, "dim_ref": "900x2100"},
    "usa_glisanta_2_canate": {"min": 3500, "max": 5500, "dim_ref": "1800x2100"},
    "usa_glisanta_3_canate": {"min": 5000, "max": 8000, "dim_ref": "2700x2100"},
    "usa_oscilo_culisanta":  {"min": 5500, "max": 9000, "dim_ref": "2000x2200"},
    "usa_armonica_4_panouri":{"min": 4500, "max": 7000, "dim_ref": "2000x2100"},
}


def valideaza_dimensiuni(latime_mm: float, inaltime_mm: float) -> dict:
    """Valideaza dimensiunile golului din perete."""
    if latime_mm < 300 or inaltime_mm < 300:
        return {"valid": False, "eroare": "Dimensiunile sunt prea mici (minim 300 mm). Verificati masuratorile."}
    if latime_mm > 4000:
        return {"valid": False, "eroare": "Latimea depaseste 4000 mm. Redirectionez catre specialist."}
    if inaltime_mm > 3000:
        return {"valid": False, "eroare": "Inaltimea depaseste 3000 mm. Redirectionez catre specialist."}

    suprafata = (latime_mm / 1000) * (inaltime_mm / 1000)
    avertisment = None
    if suprafata > 6:
        avertisment = "Suprafata depaseste 6 mp. Recomandam consultare tehnica."

    return {"valid": True, "suprafata_mp": round(suprafata, 2), "avertisment": avertisment}


def calculeaza_pret(
    latime_mm: float,
    inaltime_mm: float,
    furnizor: str,
    camere: int,
    deschidere: str = "oscilobatant",
    canate: str = "1_canat",
    culoare: str = "alb",
    sticla: str = "low_e",
    accesorii_lista: list = None,
    cantitate_accesorii: dict = None,
) -> dict:
    """
    Calculeaza pretul orientativ pentru o fereastra PVC.

    Returneaza un dict cu:
      - pret_min, pret_max (RON)
      - detalii_calcul (breakdown)
      - avertismente (lista)
    """
    avertismente = []

    # 1. Validare dimensiuni
    validare = valideaza_dimensiuni(latime_mm, inaltime_mm)
    if not validare["valid"]:
        return {"eroare": validare["eroare"]}
    if validare.get("avertisment"):
        avertismente.append(validare["avertisment"])

    suprafata = validare["suprafata_mp"]
    # Suprafata minima facturabila
    if suprafata < 0.40:
        suprafata = 0.40
        avertismente.append("Suprafata sub 0.40 mp — se factureaza minim 0.40 mp.")

    # 2. Gaseste profilul
    cheie_profil = (furnizor, camere)
    if cheie_profil not in PROFILE:
        return {"eroare": f"Profilul {furnizor} cu {camere} camere nu exista in catalog. Profile disponibile: {list(PROFILE.keys())}"}
    profil = PROFILE[cheie_profil]

    # 3. Verifica coeficientii
    if deschidere not in COEF_DESCHIDERE:
        return {"eroare": f"Tip deschidere necunoscut: {deschidere}. Optiuni: {list(COEF_DESCHIDERE.keys())}"}
    if canate not in COEF_CANATE:
        return {"eroare": f"Configuratie canate necunoscuta: {canate}. Optiuni: {list(COEF_CANATE.keys())}"}
    if culoare not in COEF_CULOARE:
        return {"eroare": f"Culoare necunoscuta: {culoare}. Optiuni: {list(COEF_CULOARE.keys())}"}
    if sticla not in COEF_STICLA:
        return {"eroare": f"Tip sticla necunoscut: {sticla}. Optiuni: {list(COEF_STICLA.keys())}"}

    # 4. Calcul
    c_deschidere = COEF_DESCHIDERE[deschidere]
    c_canate     = COEF_CANATE[canate]
    c_culoare    = COEF_CULOARE[culoare]
    c_sticla     = COEF_STICLA[sticla]

    pret_baza_min = suprafata * profil["min"]
    pret_baza_max = suprafata * profil["max"]

    subtotal_min = pret_baza_min * c_deschidere * c_canate * c_culoare * c_sticla
    subtotal_max = pret_baza_max * c_deschidere * c_canate * c_culoare * c_sticla

    # 5. Accesorii
    total_accesorii = 0
    detalii_accesorii = []
    if accesorii_lista:
        if cantitate_accesorii is None:
            cantitate_accesorii = {}
        for acc in accesorii_lista:
            if acc in ACCESORII:
                info = ACCESORII[acc]
                cant = cantitate_accesorii.get(acc, 1)
                if "pret" in info:
                    cost = info["pret"] * cant
                else:
                    cost = ((info["pret_min"] + info["pret_max"]) / 2) * cant
                total_accesorii += cost
                detalii_accesorii.append(f"{acc}: {cost:.0f} RON")

    pret_final_min = round(subtotal_min + total_accesorii)
    pret_final_max = round(subtotal_max + total_accesorii)

    return {
        "pret_min": pret_final_min,
        "pret_max": pret_final_max,
        "moneda": "RON",
        "include_tva": False,
        "include_montaj": False,
        "detalii": {
            "dimensiuni": f"{latime_mm:.0f} x {inaltime_mm:.0f} mm",
            "suprafata_mp": suprafata,
            "furnizor": furnizor,
            "camere": camere,
            "profil": profil.get("profil", ""),
            "segment": profil["segment"],
            "pret_baza_mp": f"{profil['min']}–{profil['max']} RON/mp",
            "deschidere": f"{deschidere} (x{c_deschidere})",
            "canate": f"{canate} (x{c_canate})",
            "culoare": f"{culoare} (x{c_culoare})",
            "sticla": f"{sticla} (x{c_sticla})",
            "accesorii": detalii_accesorii if detalii_accesorii else "fara",
        },
        "avertismente": avertismente,
        "nota": "Preturile sunt orientative ±15-20%. Pretul final se stabileste dupa masurare gratuita la fata locului."
    }


# Test rapid — exemplul din PDD
if __name__ == "__main__":
    rezultat = calculeaza_pret(
        latime_mm=1200,
        inaltime_mm=1400,
        furnizor="Profilink",
        camere=7,
        deschidere="oscilobatant",
        canate="2_canate_1fix_1ob",
        culoare="stejar_auriu",
        sticla="low_e",
        accesorii_lista=["plasa_antiinsecte", "glaf_interior_pvc"],
        cantitate_accesorii={"plasa_antiinsecte": 1, "glaf_interior_pvc": 1.2}
    )
    print("=== TEST CALCULATOR ===")
    if "eroare" in rezultat:
        print(f"EROARE: {rezultat['eroare']}")
    else:
        print(f"Pret: {rezultat['pret_min']} - {rezultat['pret_max']} RON")
        print(f"Detalii: {rezultat['detalii']}")
        print(f"Nota: {rezultat['nota']}")
