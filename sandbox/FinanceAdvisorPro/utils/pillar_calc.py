"""
Calculs de prévoyance suisse — 3 piliers.
"""

import numpy as np

from .constants import (
    RENTE_AVS_MAX_MENSUELLE,
    RENTE_AVS_MIN_MENSUELLE,
    SALAIRE_AVS_MAX_POUR_RENTE,
    SEUIL_ENTREE_LPP,
    DEDUCTION_COORDINATION,
    SALAIRE_MAX_LPP,
    TAUX_CONVERSION_LPP,
    TAUX_LPP_PAR_AGE,
    TAUX_INTERET_LPP,
    TAUX_INTERET_3A_MOYEN,
    TAUX_INTERET_3A_FONDS,
    PILIER_3A_SALARIE,
    AGE_RETRAITE_HOMMES,
)


def estimation_rente_avs(salaire_annuel_moyen: float, annees_cotisation: int = 44) -> dict:
    """
    Estime la rente AVS mensuelle basée sur le salaire moyen et les années de cotisation.
    Échelle complète = 44 ans de cotisation.
    """
    # Fraction de la rente complète
    fraction = min(annees_cotisation / 44, 1.0)

    # Calcul proportionnel au salaire (simplifié)
    if salaire_annuel_moyen >= SALAIRE_AVS_MAX_POUR_RENTE:
        rente_base = RENTE_AVS_MAX_MENSUELLE
    elif salaire_annuel_moyen <= 0:
        rente_base = 0
    else:
        ratio = salaire_annuel_moyen / SALAIRE_AVS_MAX_POUR_RENTE
        # Formule simplifiée avec effet dégressif
        rente_base = RENTE_AVS_MIN_MENSUELLE + (
            (RENTE_AVS_MAX_MENSUELLE - RENTE_AVS_MIN_MENSUELLE) * ratio
        )

    rente_mensuelle = round(rente_base * fraction, 2)
    rente_annuelle = round(rente_mensuelle * 12, 2)

    return {
        "rente_mensuelle": rente_mensuelle,
        "rente_annuelle": rente_annuelle,
        "fraction_cotisation": fraction,
        "annees_manquantes": max(0, 44 - annees_cotisation),
    }


def projection_lpp(
    salaire_annuel: float,
    age_actuel: int,
    capital_actuel_lpp: float = 0,
    age_retraite: int = AGE_RETRAITE_HOMMES,
) -> dict:
    """
    Projette le capital LPP à la retraite.
    """
    if salaire_annuel < SEUIL_ENTREE_LPP:
        return {
            "capital_projete": capital_actuel_lpp,
            "rente_annuelle": round(capital_actuel_lpp * TAUX_CONVERSION_LPP, 2),
            "rente_mensuelle": round(capital_actuel_lpp * TAUX_CONVERSION_LPP / 12, 2),
            "message": "Salaire inférieur au seuil d'entrée LPP.",
            "evolution": [],
        }

    salaire_coordonne = min(salaire_annuel, SALAIRE_MAX_LPP) - DEDUCTION_COORDINATION
    salaire_coordonne = max(salaire_coordonne, 0)

    capital = capital_actuel_lpp
    evolution = [{"age": age_actuel, "capital": round(capital, 2)}]

    for age in range(age_actuel, age_retraite):
        # Trouver le taux de cotisation selon l'âge
        taux = 0
        for (age_min, age_max), t in TAUX_LPP_PAR_AGE.items():
            if age_min <= age <= age_max:
                taux = t * 2  # Total (employeur + employé)
                break

        cotisation_annuelle = salaire_coordonne * taux
        interests = capital * TAUX_INTERET_LPP
        capital += cotisation_annuelle + interests
        evolution.append({"age": age + 1, "capital": round(capital, 2)})

    rente_annuelle = round(capital * TAUX_CONVERSION_LPP, 2)

    return {
        "capital_projete": round(capital, 2),
        "rente_annuelle": rente_annuelle,
        "rente_mensuelle": round(rente_annuelle / 12, 2),
        "salaire_coordonne": round(salaire_coordonne, 2),
        "evolution": evolution,
    }


def simulation_3a(
    versement_annuel: float = PILIER_3A_SALARIE,
    annees: int = 30,
    taux_rendement: float = TAUX_INTERET_3A_MOYEN,
    capital_initial: float = 0,
) -> dict:
    """
    Simule l'épargne 3ème pilier a avec intérêts composés.
    """
    versement_annuel = min(versement_annuel, PILIER_3A_SALARIE)
    capital = capital_initial
    total_verse = capital_initial
    evolution = [{"annee": 0, "capital": round(capital, 2), "verse": round(total_verse, 2)}]

    for annee in range(1, annees + 1):
        interests = capital * taux_rendement
        capital += versement_annuel + interests
        total_verse += versement_annuel
        evolution.append({
            "annee": annee,
            "capital": round(capital, 2),
            "verse": round(total_verse, 2),
        })

    return {
        "capital_final": round(capital, 2),
        "total_verse": round(total_verse, 2),
        "total_interets": round(capital - total_verse, 2),
        "rendement_total_pct": round(((capital - total_verse) / total_verse) * 100, 2) if total_verse > 0 else 0,
        "evolution": evolution,
    }


def projection_retraite_globale(
    salaire_annuel: float,
    age_actuel: int,
    capital_lpp_actuel: float = 0,
    capital_3a_actuel: float = 0,
    versement_3a_annuel: float = PILIER_3A_SALARIE,
    taux_rendement_3a: float = TAUX_INTERET_3A_MOYEN,
    annees_cotisation_avs: int = 44,
    age_retraite: int = AGE_RETRAITE_HOMMES,
) -> dict:
    """
    Projection combinée des 3 piliers pour estimer le revenu de retraite.
    """
    annees_restantes = max(0, age_retraite - age_actuel)

    # 1er pilier — AVS
    avs = estimation_rente_avs(salaire_annuel, annees_cotisation_avs)

    # 2ème pilier — LPP
    lpp = projection_lpp(salaire_annuel, age_actuel, capital_lpp_actuel, age_retraite)

    # 3ème pilier — 3a
    pilier_3a = simulation_3a(versement_3a_annuel, annees_restantes, taux_rendement_3a, capital_3a_actuel)

    # Rente totale estimée
    rente_mensuelle_avs = avs["rente_mensuelle"]
    rente_mensuelle_lpp = lpp["rente_mensuelle"]
    # Le 3a est un capital, converti en rente sur 20 ans (estimation)
    rente_mensuelle_3a = round(pilier_3a["capital_final"] / (20 * 12), 2)

    rente_totale_mensuelle = round(rente_mensuelle_avs + rente_mensuelle_lpp + rente_mensuelle_3a, 2)
    revenu_mensuel_actuel = round(salaire_annuel / 12, 2)

    taux_remplacement = round((rente_totale_mensuelle / revenu_mensuel_actuel) * 100, 2) if revenu_mensuel_actuel > 0 else 0

    return {
        "avs": avs,
        "lpp": lpp,
        "pilier_3a": pilier_3a,
        "rente_totale_mensuelle": rente_totale_mensuelle,
        "rente_totale_annuelle": round(rente_totale_mensuelle * 12, 2),
        "revenu_mensuel_actuel": revenu_mensuel_actuel,
        "taux_remplacement": taux_remplacement,
        "gap_mensuel": round(revenu_mensuel_actuel - rente_totale_mensuelle, 2),
        "annees_restantes": annees_restantes,
    }
