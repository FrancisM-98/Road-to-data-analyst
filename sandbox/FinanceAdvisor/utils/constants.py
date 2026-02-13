"""
Constantes financières suisses — Valeurs 2025
Ces valeurs sont fournies à titre indicatif et doivent être mises à jour annuellement.
"""

# ─── 3ème Pilier ───────────────────────────────────────────
PILIER_3A_SALARIE = 7_056        # Plafond annuel 3a (salarié avec 2e pilier)
PILIER_3A_INDEPENDANT = 35_280   # Plafond annuel 3a (indépendant sans 2e pilier)

# ─── AVS / AI / APG (1er Pilier) ──────────────────────────
TAUX_AVS_TOTAL = 0.087           # 8.7% (4.35% employeur + 4.35% employé)
TAUX_AVS_EMPLOYE = 0.0435
TAUX_AI = 0.014                  # 1.4%
TAUX_APG = 0.005                 # 0.5%
RENTE_AVS_MAX_MENSUELLE = 2_450  # Rente AVS maximale mensuelle (simple)
RENTE_AVS_MIN_MENSUELLE = 1_225  # Rente AVS minimale mensuelle
SALAIRE_AVS_MAX_POUR_RENTE = 88_200  # Revenu annuel moyen pour rente max

# ─── LPP (2ème Pilier) ────────────────────────────────────
SEUIL_ENTREE_LPP = 22_050       # Seuil d'entrée LPP
DEDUCTION_COORDINATION = 25_725  # Déduction de coordination
SALAIRE_MAX_LPP = 88_200        # Salaire maximum assuré
TAUX_CONVERSION_LPP = 0.068     # Taux de conversion (6.8%)

# Taux de cotisation LPP par tranche d'âge (part employé, minimum légal)
TAUX_LPP_PAR_AGE = {
    (25, 34): 0.035,   # 7% total, 3.5% employé
    (35, 44): 0.05,    # 10% total, 5% employé
    (45, 54): 0.075,   # 15% total, 7.5% employé
    (55, 65): 0.09,    # 18% total, 9% employé
}

# ─── Taux de rendement estimés ─────────────────────────────
TAUX_INTERET_LPP = 0.01         # Taux d'intérêt minimal LPP (1%)
TAUX_INTERET_3A_MOYEN = 0.015   # Rendement moyen 3a compte bancaire
TAUX_INTERET_3A_FONDS = 0.045   # Rendement moyen 3a fonds de placement

# ─── Impôts fédéraux — Barème 2025 (personnes seules) ─────
BAREME_FEDERAL_SEUL = [
    (14_500, 0.0),
    (31_600, 0.0077),
    (41_400, 0.0088),
    (55_200, 0.026),
    (72_500, 0.0291),
    (78_100, 0.051),
    (103_600, 0.068),
    (134_600, 0.088),
    (176_000, 0.11),
    (755_200, 0.13),
    (float('inf'), 0.115),
]

# Barème fédéral (personnes mariées)
BAREME_FEDERAL_MARIE = [
    (28_300, 0.0),
    (50_900, 0.01),
    (58_400, 0.02),
    (75_300, 0.03),
    (90_300, 0.04),
    (103_400, 0.05),
    (114_700, 0.06),
    (124_200, 0.07),
    (131_700, 0.08),
    (137_200, 0.09),
    (141_200, 0.10),
    (143_700, 0.11),
    (145_200, 0.12),
    (895_900, 0.13),
    (float('inf'), 0.115),
]

# ─── Coefficients fiscaux cantonaux (estimation simplifiée) ─
# Multiplicateur appliqué à l'impôt cantonal de base
CANTONS_ROMANDS = {
    "Vaud (VD)": {
        "coefficient_cantonal": 1.545,
        "coefficient_communal_moyen": 0.785,  # Moyenne des communes
        "taux_impot_fortune": 0.005,           # Taux moyen sur la fortune
        "communes": {
            "Lausanne": 0.79,
            "Montreux": 0.81,
            "Nyon": 0.73,
            "Vevey": 0.82,
            "Yverdon-les-Bains": 0.81,
            "Morges": 0.72,
            "Renens": 0.80,
            "Pully": 0.70,
        }
    },
    "Genève (GE)": {
        "coefficient_cantonal": 1.78,
        "coefficient_communal_moyen": 0.455,
        "taux_impot_fortune": 0.006,
        "communes": {
            "Genève": 0.455,
            "Carouge": 0.46,
            "Lancy": 0.47,
            "Vernier": 0.48,
            "Meyrin": 0.46,
            "Onex": 0.48,
        }
    },
    "Valais (VS)": {
        "coefficient_cantonal": 1.0,
        "coefficient_communal_moyen": 1.30,
        "taux_impot_fortune": 0.004,
        "communes": {
            "Sion": 1.30,
            "Sierre": 1.35,
            "Martigny": 1.35,
            "Monthey": 1.40,
        }
    },
    "Fribourg (FR)": {
        "coefficient_cantonal": 1.0,
        "coefficient_communal_moyen": 0.85,
        "taux_impot_fortune": 0.005,
        "communes": {
            "Fribourg": 0.84,
            "Bulle": 0.80,
            "Villars-sur-Glâne": 0.78,
        }
    },
    "Neuchâtel (NE)": {
        "coefficient_cantonal": 1.30,
        "coefficient_communal_moyen": 0.85,
        "taux_impot_fortune": 0.005,
        "communes": {
            "Neuchâtel": 0.86,
            "La Chaux-de-Fonds": 0.90,
            "Le Locle": 0.92,
        }
    },
    "Jura (JU)": {
        "coefficient_cantonal": 1.0,
        "coefficient_communal_moyen": 1.90,
        "taux_impot_fortune": 0.005,
        "communes": {
            "Delémont": 1.85,
            "Porrentruy": 1.95,
        }
    },
    "Berne (BE) — partie francophone": {
        "coefficient_cantonal": 1.0,
        "coefficient_communal_moyen": 1.54,
        "taux_impot_fortune": 0.004,
        "communes": {
            "Bienne": 1.58,
            "Moutier": 1.80,
            "Saint-Imier": 1.95,
        }
    },
}

# ─── Catégories budgétaires (moyennes suisses OFS) ────────
CATEGORIES_BUDGET = {
    "Logement": {"moyenne_pct": 0.33, "emoji": "🏠"},
    "Assurance maladie": {"moyenne_pct": 0.07, "emoji": "🏥"},
    "Alimentation": {"moyenne_pct": 0.11, "emoji": "🍽️"},
    "Transport": {"moyenne_pct": 0.08, "emoji": "🚗"},
    "Impôts": {"moyenne_pct": 0.12, "emoji": "🏛️"},
    "Loisirs & Culture": {"moyenne_pct": 0.06, "emoji": "🎭"},
    "Communication": {"moyenne_pct": 0.03, "emoji": "📱"},
    "Habillement": {"moyenne_pct": 0.03, "emoji": "👔"},
    "Épargne & Prévoyance": {"moyenne_pct": 0.12, "emoji": "💰"},
    "Autres": {"moyenne_pct": 0.05, "emoji": "📦"},
}

# ─── Profils d'investissement ─────────────────────────────
PROFILS_INVESTISSEMENT = {
    "Conservateur": {
        "description": "Priorité à la sécurité du capital",
        "rendement_moyen": 0.03,
        "volatilite": 0.04,
        "allocation": {"Obligations": 60, "Actions": 15, "Immobilier": 15, "Liquidités": 10},
        "emoji": "🛡️",
    },
    "Équilibré": {
        "description": "Bon équilibre risque/rendement",
        "rendement_moyen": 0.055,
        "volatilite": 0.08,
        "allocation": {"Obligations": 35, "Actions": 35, "Immobilier": 20, "Liquidités": 10},
        "emoji": "⚖️",
    },
    "Dynamique": {
        "description": "Recherche de rendement à long terme",
        "rendement_moyen": 0.07,
        "volatilite": 0.12,
        "allocation": {"Obligations": 15, "Actions": 55, "Immobilier": 20, "Liquidités": 10},
        "emoji": "🚀",
    },
    "Agressif": {
        "description": "Rendement maximal, haute volatilité",
        "rendement_moyen": 0.09,
        "volatilite": 0.18,
        "allocation": {"Obligations": 5, "Actions": 70, "Immobilier": 15, "Crypto": 5, "Liquidités": 5},
        "emoji": "🔥",
    },
}

# ─── Âge de retraite ──────────────────────────────────────
AGE_RETRAITE_HOMMES = 65
AGE_RETRAITE_FEMMES = 65  # Harmonisé avec AVS 21
