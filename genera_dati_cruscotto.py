"""
Genera i due dataset del cruscotto direzionale (dati INVENTATI di una banca immaginaria).

  consuntivo_trimestrale_per_paese.csv   i risultati effettivi: una riga per paese e per trimestre
  obiettivi_annuali_per_paese.csv        i traguardi fissati per ogni paese

I file vengono scritti nella cartella da cui lanciamo il programma:
    python genera_dati_cruscotto.py

Formato dei file: intestazione a 3 righe, come la vuole Orange Data Mining
  riga 1 = nomi delle colonne
  riga 2 = tipo della colonna (discrete = a categorie, continuous = numerica)
  riga 3 = ruolo della colonna (qui sempre vuoto)
In pandas i file si leggono con: pd.read_csv(percorso, skiprows=[1, 2])

I dati sono costruiti in modo deterministico: a ogni esecuzione i file sono identici.
Per cambiare la storia raccontata dal cruscotto basta ritoccare le tabelle PAESI e OBIETTIVI.
Unità di misura: "mln" = milioni di euro, "mld" = miliardi di euro.
"""
import random

TRIMESTRI = ["2024-T4", "2025-T1", "2025-T2", "2025-T3", "2025-T4", "2026-T1", "2026-T2", "2026-T3"]
ALIQUOTA_IMPOSTE = 0.28

# Per ogni paese: area, proventi del primo trimestre (mln), crescita annua dei proventi,
# quota del margine di interesse sui proventi, cost/income iniziale e finale (%),
# impieghi iniziali (mld), crescita annua degli impieghi,
# costo del rischio iniziale e finale (punti base annui sugli impieghi),
# quota di crediti deteriorati iniziale e finale (%).
PAESI = [
    ("Italia",      "Europa occidentale",      2400,  0.030, 0.64, 52.5, 51.5, 420,  0.02,  38,  36, 2.7, 2.5),
    ("Germania",    "Europa occidentale",      1500,  0.010, 0.60, 65.0, 67.5, 280,  0.01,  22,  24, 1.8, 1.9),
    ("Francia",     "Europa occidentale",       950,  0.025, 0.58, 59.5, 58.5, 160,  0.02,  26,  26, 2.2, 2.1),
    ("Spagna",      "Europa occidentale",       700,  0.040, 0.68, 50.0, 49.5, 115,  0.03,  55,  60, 4.1, 4.5),
    ("Polonia",     "Europa centro-orientale",  420,  0.090, 0.72, 44.0, 42.5,  46,  0.08,  60,  60, 3.5, 3.3),
    ("Romania",     "Europa centro-orientale",  210,  0.110, 0.74, 47.0, 46.0,  19,  0.10,  85,  95, 4.9, 5.6),
    ("Ungheria",    "Europa centro-orientale",  170,  0.070, 0.70, 49.0, 48.0,  15,  0.06,  70,  70, 3.9, 3.7),
    ("Stati Uniti", "Americhe",                 620, -0.050, 0.55, 66.0, 70.0,  72, -0.02,  45,  65, 2.0, 3.1),
    ("Brasile",     "Americhe",                 380,  0.060, 0.76, 44.0, 44.5,  26,  0.07, 210, 260, 5.6, 6.6),
]

# Obiettivi annuali per paese: utile netto minimo (mln), cost/income massimo (%), NPL ratio massimo (%).
OBIETTIVI = {
    "Italia":      (2300, 53.0, 3.0),
    "Germania":    (900,  63.0, 2.5),
    "Francia":     (820,  60.0, 2.5),
    "Spagna":      (540,  51.0, 4.0),
    "Polonia":     (500,  45.0, 4.0),
    "Romania":     (210,  48.0, 5.0),
    "Ungheria":    (180,  50.0, 4.5),
    "Stati Uniti": (330,  64.0, 3.5),
    "Brasile":     (210,  46.0, 6.0),
}

COLONNE_CONSUNTIVO = ["paese", "area", "trimestre", "margine_interesse_mln", "commissioni_nette_mln",
                      "costi_operativi_mln", "rettifiche_su_crediti_mln", "utile_netto_mln",
                      "impieghi_mld", "crediti_deteriorati_mld"]
COLONNE_OBIETTIVI = ["paese", "obiettivo_utile_netto_mln", "obiettivo_cost_income_pct", "soglia_npl_ratio_pct"]
A_CATEGORIE = {"paese", "area", "trimestre"}


def genera_consuntivo():
    caso = random.Random(2026)

    def rumore(ampiezza):
        """Numero casuale tra -ampiezza e +ampiezza: rende i dati meno regolari, quindi più verosimili."""
        return (caso.random() * 2 - 1) * ampiezza

    righe = []
    for (paese, area, proventi0, crescita, quota_margine, ci0, ci7,
         impieghi0, crescita_impieghi, rischio0, rischio7, npl0, npl7) in PAESI:
        for t, trimestre in enumerate(TRIMESTRI):
            avanzamento = t / (len(TRIMESTRI) - 1)          # da 0 (primo trimestre) a 1 (ultimo)
            # Nessuna stagionalità: così l'andamento nel tempo resta facile da leggere.
            proventi = proventi0 * (1 + crescita) ** (t / 4) * (1 + rumore(0.006))
            margine = proventi * (quota_margine + rumore(0.005))
            commissioni = proventi - margine
            cost_income = ci0 + (ci7 - ci0) * avanzamento + rumore(0.3)
            costi = proventi * cost_income / 100
            impieghi = impieghi0 * (1 + crescita_impieghi) ** (t / 4)
            costo_rischio = (rischio0 + (rischio7 - rischio0) * avanzamento) * (1 + rumore(0.04))
            rettifiche = impieghi * 1000 * costo_rischio / 10000 / 4
            utile = (proventi - costi - rettifiche) * (1 - ALIQUOTA_IMPOSTE)
            npl_ratio = npl0 + (npl7 - npl0) * avanzamento + rumore(0.03)
            deteriorati = impieghi * npl_ratio / 100
            righe.append({
                "paese": paese, "area": area, "trimestre": trimestre,
                "margine_interesse_mln": round(margine, 1),
                "commissioni_nette_mln": round(commissioni, 1),
                "costi_operativi_mln": round(costi, 1),
                "rettifiche_su_crediti_mln": round(rettifiche, 1),
                "utile_netto_mln": round(utile, 1),
                "impieghi_mld": round(impieghi, 2),
                "crediti_deteriorati_mld": round(deteriorati, 2),
            })
    return righe


def genera_obiettivi():
    return [{"paese": paese, "obiettivo_utile_netto_mln": utile, "obiettivo_cost_income_pct": ci,
             "soglia_npl_ratio_pct": npl} for paese, (utile, ci, npl) in OBIETTIVI.items()]


def scrivi_csv_orange(righe, colonne, percorso):
    """CSV con intestazione a 3 righe (nomi / tipi / ruoli): Orange lo legge senza configurazione."""
    with open(percorso, "w", newline="", encoding="utf-8") as f:
        f.write(",".join(colonne) + "\n")
        f.write(",".join("discrete" if c in A_CATEGORIE else "continuous" for c in colonne) + "\n")
        f.write(",".join("" for _ in colonne) + "\n")
        for riga in righe:
            f.write(",".join(str(riga[c]) for c in colonne) + "\n")


if __name__ == "__main__":
    consuntivo = genera_consuntivo()
    obiettivi = genera_obiettivi()
    scrivi_csv_orange(consuntivo, COLONNE_CONSUNTIVO, "consuntivo_trimestrale_per_paese.csv")
    scrivi_csv_orange(obiettivi, COLONNE_OBIETTIVI, "obiettivi_annuali_per_paese.csv")
    print("consuntivo:", len(consuntivo), "righe | obiettivi:", len(obiettivi), "righe")
