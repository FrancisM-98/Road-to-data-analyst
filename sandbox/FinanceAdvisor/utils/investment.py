"""
Fonctions de simulation d'investissement.
"""

import numpy as np


def interets_composes(
    capital_initial: float,
    versement_mensuel: float,
    taux_annuel: float,
    annees: int,
) -> dict:
    """Calcul d'intérêts composés avec versements mensuels."""
    taux_mensuel = taux_annuel / 12
    n_mois = annees * 12

    evolution = []
    capital = capital_initial
    total_verse = capital_initial

    for mois in range(n_mois + 1):
        if mois > 0:
            interests = capital * taux_mensuel
            capital += versement_mensuel + interests
            total_verse += versement_mensuel

        if mois % 12 == 0:
            evolution.append({
                "annee": mois // 12,
                "capital": round(capital, 2),
                "verse": round(total_verse, 2),
                "interets_cumules": round(capital - total_verse, 2),
            })

    return {
        "capital_final": round(capital, 2),
        "total_verse": round(total_verse, 2),
        "total_interets": round(capital - total_verse, 2),
        "rendement_pct": round(((capital - total_verse) / total_verse) * 100, 2) if total_verse > 0 else 0,
        "evolution": evolution,
    }


def simulation_monte_carlo(
    capital_initial: float,
    versement_mensuel: float,
    rendement_moyen: float,
    volatilite: float,
    annees: int,
    n_simulations: int = 500,
) -> dict:
    """
    Simulation Monte Carlo pour estimer la distribution des résultats d'investissement.
    """
    np.random.seed(42)
    taux_mensuel = rendement_moyen / 12
    vol_mensuelle = volatilite / np.sqrt(12)
    n_mois = annees * 12

    resultats_finaux = []
    percentiles_evolution = {5: [], 25: [], 50: [], 75: [], 95: []}

    # Simuler
    all_trajectories = np.zeros((n_simulations, n_mois + 1))
    all_trajectories[:, 0] = capital_initial

    for sim in range(n_simulations):
        capital = capital_initial
        for m in range(1, n_mois + 1):
            rendement = np.random.normal(taux_mensuel, vol_mensuelle)
            capital = capital * (1 + rendement) + versement_mensuel
            capital = max(capital, 0)
            all_trajectories[sim, m] = capital
        resultats_finaux.append(capital)

    # Calculer les percentiles par année
    for annee in range(annees + 1):
        mois = annee * 12
        valeurs = all_trajectories[:, mois]
        for p in percentiles_evolution:
            percentiles_evolution[p].append({
                "annee": annee,
                "valeur": round(float(np.percentile(valeurs, p)), 2),
            })

    total_verse = capital_initial + versement_mensuel * n_mois

    return {
        "mediane": round(float(np.median(resultats_finaux)), 2),
        "percentile_5": round(float(np.percentile(resultats_finaux, 5)), 2),
        "percentile_25": round(float(np.percentile(resultats_finaux, 25)), 2),
        "percentile_75": round(float(np.percentile(resultats_finaux, 75)), 2),
        "percentile_95": round(float(np.percentile(resultats_finaux, 95)), 2),
        "total_verse": round(total_verse, 2),
        "probabilite_perte": round(float(np.mean(np.array(resultats_finaux) < total_verse)) * 100, 2),
        "percentiles_evolution": percentiles_evolution,
    }


def cout_opportunite(
    depense_mensuelle: float,
    taux_annuel: float = 0.06,
    annees: int = 20,
) -> dict:
    """
    Calcule le coût d'opportunité d'une dépense récurrente :
    combien aurait-on si on investissait cette somme ?
    """
    result = interets_composes(0, depense_mensuelle, taux_annuel, annees)
    return {
        "depense_mensuelle": depense_mensuelle,
        "total_depense": round(depense_mensuelle * annees * 12, 2),
        "valeur_si_investi": result["capital_final"],
        "gain_manque": result["total_interets"],
        "facteur_multiplicateur": round(result["capital_final"] / (depense_mensuelle * annees * 12), 2)
        if (depense_mensuelle * annees * 12) > 0 else 0,
    }


def comparer_scenarios(
    capital_initial: float,
    versement_mensuel: float,
    annees: int,
    profils: dict,
) -> dict:
    """Compare plusieurs profils d'investissement."""
    resultats = {}
    for nom, profil in profils.items():
        result = interets_composes(
            capital_initial,
            versement_mensuel,
            profil["rendement_moyen"],
            annees,
        )
        monte_carlo = simulation_monte_carlo(
            capital_initial,
            versement_mensuel,
            profil["rendement_moyen"],
            profil["volatilite"],
            annees,
            n_simulations=300,
        )
        resultats[nom] = {
            "deterministe": result,
            "monte_carlo": monte_carlo,
            "profil": profil,
        }
    return resultats
