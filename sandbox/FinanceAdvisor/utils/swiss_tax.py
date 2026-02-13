"""
Moteur de calcul fiscal suisse simplifié.
Couvre l'impôt fédéral direct et une estimation cantonale/communale.
"""

from .constants import (
    BAREME_FEDERAL_SEUL,
    BAREME_FEDERAL_MARIE,
    CANTONS_ROMANDS,
    PILIER_3A_SALARIE,
)


def calcul_impot_federal(revenu_imposable: float, marie: bool = False) -> float:
    """Calcul de l'impôt fédéral direct (IFD) selon le barème progressif."""
    bareme = BAREME_FEDERAL_MARIE if marie else BAREME_FEDERAL_SEUL
    impot = 0.0
    revenu_precedent = 0.0

    for seuil, taux in bareme:
        if revenu_imposable <= seuil:
            impot += (revenu_imposable - revenu_precedent) * taux
            break
        else:
            impot += (seuil - revenu_precedent) * taux
            revenu_precedent = seuil

    return round(impot, 2)


def calcul_impot_cantonal(
    revenu_imposable: float,
    canton: str,
    commune: str | None = None,
    marie: bool = False,
) -> dict:
    """
    Estimation de l'impôt cantonal et communal.
    Utilise le barème fédéral comme base, multiplié par les coefficients cantonaux/communaux.
    C'est une simplification — en réalité, chaque canton a son propre barème.
    """
    if canton not in CANTONS_ROMANDS:
        return {"cantonal": 0, "communal": 0, "total": 0}

    info = CANTONS_ROMANDS[canton]
    base_impot = calcul_impot_federal(revenu_imposable, marie)

    coeff_cantonal = info["coefficient_cantonal"]
    coeff_communal = info["coefficient_communal_moyen"]

    if commune and commune in info.get("communes", {}):
        coeff_communal = info["communes"][commune]

    impot_cantonal = round(base_impot * coeff_cantonal, 2)
    impot_communal = round(base_impot * coeff_communal, 2)

    return {
        "cantonal": impot_cantonal,
        "communal": impot_communal,
        "total": round(impot_cantonal + impot_communal, 2),
    }


def calcul_impot_total(
    revenu_brut: float,
    canton: str,
    commune: str | None = None,
    marie: bool = False,
    enfants: int = 0,
    deduction_3a: float = 0,
    deduction_rachat_lpp: float = 0,
    deduction_frais_effectifs: float = 0,
) -> dict:
    """Calcul complet de l'impôt (fédéral + cantonal + communal) avec déductions."""

    # Déductions forfaitaires
    deduction_professionnelle = min(revenu_brut * 0.03, 4_000)
    deduction_avs_ai = revenu_brut * 0.0535  # Part employé AVS/AI/APG/AC
    deduction_lpp_estimee = revenu_brut * 0.05  # Estimation cotisation LPP

    # Déduction enfants
    deduction_enfants = enfants * 6_600 if not marie else enfants * 6_600

    # Plafond 3a
    deduction_3a = min(deduction_3a, PILIER_3A_SALARIE)

    total_deductions = (
        deduction_professionnelle
        + deduction_avs_ai
        + deduction_lpp_estimee
        + deduction_enfants
        + deduction_3a
        + deduction_rachat_lpp
        + deduction_frais_effectifs
    )

    revenu_imposable = max(0, revenu_brut - total_deductions)

    impot_federal = calcul_impot_federal(revenu_imposable, marie)
    impots_cantonaux = calcul_impot_cantonal(revenu_imposable, canton, commune, marie)

    impot_total = round(impot_federal + impots_cantonaux["total"], 2)

    return {
        "revenu_brut": revenu_brut,
        "total_deductions": round(total_deductions, 2),
        "revenu_imposable": round(revenu_imposable, 2),
        "impot_federal": impot_federal,
        "impot_cantonal": impots_cantonaux["cantonal"],
        "impot_communal": impots_cantonaux["communal"],
        "impot_total": impot_total,
        "taux_effectif": round((impot_total / revenu_brut) * 100, 2) if revenu_brut > 0 else 0,
        "detail_deductions": {
            "Frais professionnels": round(deduction_professionnelle, 2),
            "Cotisations sociales (AVS/AI/AC)": round(deduction_avs_ai, 2),
            "Cotisation LPP (estimée)": round(deduction_lpp_estimee, 2),
            "Déduction enfants": round(deduction_enfants, 2),
            "3ème pilier (3a)": round(deduction_3a, 2),
            "Rachat LPP": round(deduction_rachat_lpp, 2),
            "Frais effectifs": round(deduction_frais_effectifs, 2),
        },
    }


def comparaison_cantonale(
    revenu_brut: float,
    marie: bool = False,
    enfants: int = 0,
    deduction_3a: float = 0,
) -> dict:
    """Compare l'imposition entre tous les cantons romands."""
    resultats = {}
    for canton in CANTONS_ROMANDS:
        result = calcul_impot_total(
            revenu_brut=revenu_brut,
            canton=canton,
            marie=marie,
            enfants=enfants,
            deduction_3a=deduction_3a,
        )
        resultats[canton] = result
    return resultats


def suggestions_optimisation(
    revenu_brut: float,
    deduction_3a_actuelle: float = 0,
    rachat_lpp_actuel: float = 0,
    canton: str = "Vaud (VD)",
    marie: bool = False,
    enfants: int = 0,
) -> list[dict]:
    """Génère des suggestions d'optimisation fiscale personnalisées."""
    suggestions = []

    # Suggestion 3ème pilier
    if deduction_3a_actuelle < PILIER_3A_SALARIE:
        economie_potentielle = calcul_impot_total(
            revenu_brut, canton, marie=marie, enfants=enfants, deduction_3a=0
        )["impot_total"] - calcul_impot_total(
            revenu_brut, canton, marie=marie, enfants=enfants, deduction_3a=PILIER_3A_SALARIE
        )["impot_total"]

        suggestions.append({
            "titre": "💰 Maximiser le 3ème pilier (3a)",
            "description": f"Versez le maximum de CHF {PILIER_3A_SALARIE:,.0f} par an dans votre 3ème pilier.",
            "economie_estimee": round(economie_potentielle, 0),
            "priorite": "haute",
        })

    # Suggestion rachat LPP
    if rachat_lpp_actuel == 0:
        rachat_test = 10_000
        eco_rachat = calcul_impot_total(
            revenu_brut, canton, marie=marie, enfants=enfants,
            deduction_3a=deduction_3a_actuelle
        )["impot_total"] - calcul_impot_total(
            revenu_brut, canton, marie=marie, enfants=enfants,
            deduction_3a=deduction_3a_actuelle, deduction_rachat_lpp=rachat_test
        )["impot_total"]

        suggestions.append({
            "titre": "🏦 Envisager un rachat LPP",
            "description": f"Un rachat de CHF {rachat_test:,.0f} dans votre 2ème pilier est déductible fiscalement.",
            "economie_estimee": round(eco_rachat, 0),
            "priorite": "moyenne",
        })

    # Suggestion comparaison cantonale
    comparaison = comparaison_cantonale(revenu_brut, marie, enfants, deduction_3a_actuelle)
    canton_moins_cher = min(comparaison, key=lambda c: comparaison[c]["impot_total"])
    impot_actuel = comparaison.get(canton, {}).get("impot_total", 0)
    impot_minimum = comparaison[canton_moins_cher]["impot_total"]

    if canton != canton_moins_cher and (impot_actuel - impot_minimum) > 1000:
        suggestions.append({
            "titre": f"🗺️ Canton plus avantageux : {canton_moins_cher}",
            "description": f"Un déménagement permettrait une économie significative.",
            "economie_estimee": round(impot_actuel - impot_minimum, 0),
            "priorite": "info",
        })

    return suggestions
