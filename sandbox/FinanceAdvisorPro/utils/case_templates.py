"""
Bibliothèque de cas types — Profils clients pré-configurés.
Permet au conseiller de charger rapidement un profil type en rendez-vous.
"""

CASE_TEMPLATES = {
    "jeune_diplome": {
        "titre": "Jeune diplômé",
        "description": "25 ans, premier emploi, célibataire, débute sa vie financière",
        "profil": {
            "prenom": "Léa",
            "nom": "Martin",
            "age": 25,
            "situation_familiale": "Célibataire",
            "enfants": 0,
            "canton": "Genève (GE)",
            "commune": "Genève",
            "salaire_annuel": 55_000,
            "capital_lpp": 5_000,
            "capital_3a": 0,
        },
        "budget": {
            "salaire_net": 3_900,
            "loyer": 1_400,
            "assurance_maladie": 350,
            "transport": 80,
            "impots_mensuels": 450,
            "alimentation": 450,
            "loisirs": 200,
            "prevoyance_3a": 0,
        },
        "recommandations": [
            "Ouvrir un 3ème pilier dès maintenant (effet des intérêts composés)",
            "Constituer un fonds d'urgence de 3 mois de dépenses",
            "Envisager un placement en fonds indiciel (ETF) pour le long terme",
        ],
    },
    "famille_classe_moyenne": {
        "titre": "Famille classe moyenne",
        "description": "38 ans, marié, 2 enfants, propriétaire aspirant",
        "profil": {
            "prenom": "Marc",
            "nom": "Favre",
            "age": 38,
            "situation_familiale": "Marié·e",
            "enfants": 2,
            "canton": "Vaud (VD)",
            "commune": "Lausanne",
            "salaire_annuel": 95_000,
            "capital_lpp": 80_000,
            "capital_3a": 25_000,
        },
        "budget": {
            "salaire_net": 6_500,
            "loyer": 2_200,
            "assurance_maladie": 780,
            "transport": 350,
            "impots_mensuels": 900,
            "alimentation": 750,
            "loisirs": 200,
            "prevoyance_3a": 588,
        },
        "recommandations": [
            "Maximiser le 3ème pilier pour les deux conjoints (2x CHF 7'056)",
            "Évaluer la faisabilité d'un achat immobilier (retrait 2ème pilier)",
            "Vérifier les assurances-vie pour la protection de la famille",
            "Optimiser la déclaration fiscale conjointe vs séparée",
        ],
    },
    "cadre_superieur": {
        "titre": "Cadre supérieur",
        "description": "45 ans, haut revenu, marié, 1 enfant, patrimoine à structurer",
        "profil": {
            "prenom": "Sophie",
            "nom": "Rochat",
            "age": 45,
            "situation_familiale": "Marié·e",
            "enfants": 1,
            "canton": "Genève (GE)",
            "commune": "Carouge",
            "salaire_annuel": 160_000,
            "capital_lpp": 250_000,
            "capital_3a": 80_000,
        },
        "budget": {
            "salaire_net": 10_000,
            "loyer": 3_000,
            "assurance_maladie": 750,
            "transport": 500,
            "impots_mensuels": 2_200,
            "alimentation": 800,
            "loisirs": 400,
            "prevoyance_3a": 588,
        },
        "recommandations": [
            "Rachat LPP pour optimisation fiscale (déduction importante)",
            "Stratégie de placement diversifiée (profil dynamique possible)",
            "Étudier le passage en indépendant pour le pilier 3a majoré",
            "Planification successorale à initier",
            "Comparaison cantonale pour optimisation fiscale",
        ],
    },
    "proche_retraite": {
        "titre": "Proche retraite",
        "description": "58 ans, marié, planification de la transition vers la retraite",
        "profil": {
            "prenom": "Pierre",
            "nom": "Bonvin",
            "age": 58,
            "situation_familiale": "Marié·e",
            "enfants": 0,
            "canton": "Valais (VS)",
            "commune": "Sion",
            "salaire_annuel": 110_000,
            "capital_lpp": 450_000,
            "capital_3a": 120_000,
        },
        "budget": {
            "salaire_net": 7_500,
            "loyer": 1_800,
            "assurance_maladie": 700,
            "transport": 300,
            "impots_mensuels": 1_100,
            "alimentation": 650,
            "loisirs": 300,
            "prevoyance_3a": 588,
        },
        "recommandations": [
            "Analyse du gap de revenu à la retraite (3 piliers combinés)",
            "Capital vs rente pour le 2ème pilier — simulation comparative",
            "Échelonnement du retrait des comptes 3a (optimisation fiscale)",
            "Réduction progressive du risque dans le portefeuille",
            "Planification du retrait anticipé vs retraite ordinaire",
        ],
    },
    "independant": {
        "titre": "Indépendant",
        "description": "35 ans, travailleur indépendant, prévoyance à construire",
        "profil": {
            "prenom": "Yann",
            "nom": "Berger",
            "age": 35,
            "situation_familiale": "Célibataire",
            "enfants": 0,
            "canton": "Neuchâtel (NE)",
            "commune": "Neuchâtel",
            "salaire_annuel": 75_000,
            "capital_lpp": 15_000,
            "capital_3a": 10_000,
        },
        "budget": {
            "salaire_net": 5_000,
            "loyer": 1_300,
            "assurance_maladie": 400,
            "transport": 200,
            "impots_mensuels": 700,
            "alimentation": 500,
            "loisirs": 150,
            "prevoyance_3a": 400,
        },
        "recommandations": [
            "Maximiser le 3ème pilier (plafond indépendant : CHF 35'280)",
            "Évaluer l'opportunité d'une affiliation LPP facultative",
            "Constituer une réserve de trésorerie de 6 mois",
            "Protection en cas d'incapacité de gain (assurance perte de gain)",
            "Structurer l'activité (raison individuelle vs Sàrl)",
        ],
    },
}


def get_template_names() -> list[str]:
    """Retourne la liste des noms de cas types."""
    return list(CASE_TEMPLATES.keys())


def get_template(template_key: str) -> dict | None:
    """Retourne un cas type par sa clé."""
    return CASE_TEMPLATES.get(template_key)


def get_templates_summary() -> list[dict]:
    """Retourne un résumé de tous les cas types pour affichage."""
    summaries = []
    for key, template in CASE_TEMPLATES.items():
        profil = template["profil"]
        summaries.append({
            "key": key,
            "titre": template["titre"],
            "description": template["description"],
            "age": profil["age"],
            "salaire": profil["salaire_annuel"],
            "situation": profil["situation_familiale"],
            "canton": profil["canton"],
            "recommandations": template.get("recommandations", []),
        })
    return summaries
