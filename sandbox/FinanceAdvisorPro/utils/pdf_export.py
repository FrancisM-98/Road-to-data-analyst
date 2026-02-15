"""
Module PDF Export -- Rapport professionnel brande
Genere des PDF pour chaque module de simulation avec couverture,
KPIs, tableaux et conseils.
"""

import io
import os
import re
from datetime import datetime
from fpdf import FPDF


# ─── Couleurs ────────────────────────────────────────────────
COLORS = {
    "primary": (108, 99, 255),      # #6C63FF
    "accent": (0, 212, 170),        # #00D4AA
    "warning": (255, 179, 71),      # #FFB347
    "danger": (255, 107, 107),      # #FF6B6B
    "dark": (14, 17, 23),           # #0E1117
    "text": (255, 255, 255),
    "muted": (160, 163, 177),       # #A0A3B1
    "bg_card": (30, 33, 45),
}


def _clean_text(text: str) -> str:
    """Remove characters not supported by Helvetica/latin-1 (e.g. emojis)."""
    symbol_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map
        "\U0001F1E0-\U0001F1FF"  # flags
        "\U00002702-\U000027B0"  # dingbats
        "\U000024C2-\U0001F251"
        "\U0001f900-\U0001f9FF"  # supplemental symbols
        "\U00002600-\U000026FF"  # misc symbols
        "\U0000FE00-\U0000FE0F"  # variation selectors
        "\U0000200D"             # ZWJ
        "]+",
        flags=re.UNICODE,
    )
    return symbol_pattern.sub("", text).strip()


class FinanceAdvisorPDF(FPDF):
    """PDF personnalise avec en-tete/pied de page brandes."""

    def __init__(self, advisor_name: str = "", client_name: str = "", module: str = ""):
        super().__init__()
        self.advisor_name = advisor_name
        self.client_name = client_name
        self.module_name = module
        self.set_auto_page_break(auto=True, margin=20)

    def header(self):
        if self.page_no() == 1:
            return  # Cover page has its own header
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(*COLORS["muted"])
        self.cell(0, 8, f"Finance Advisor Pro - {self.module_name}", align="L")
        self.cell(0, 8, f"Client : {self.client_name}", align="R", new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(*COLORS["primary"])
        self.set_line_width(0.5)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 7)
        self.set_text_color(*COLORS["muted"])
        self.cell(0, 10, f"Finance Advisor Pro - Rapport confidentiel - Page {self.page_no()}/{{nb}}", align="C")


def _add_cover_page(pdf: FinanceAdvisorPDF, module_title: str):
    """Ajoute une page de couverture professionnelle."""
    pdf.add_page()

    # Background
    pdf.set_fill_color(*COLORS["dark"])
    pdf.rect(0, 0, 210, 297, "F")

    # Primary accent bar
    pdf.set_fill_color(*COLORS["primary"])
    pdf.rect(0, 80, 210, 4, "F")

    # Title
    pdf.set_y(100)
    pdf.set_font("Helvetica", "B", 28)
    pdf.set_text_color(*COLORS["text"])
    pdf.cell(0, 15, module_title, align="C", new_x="LMARGIN", new_y="NEXT")

    # Subtitle
    pdf.set_font("Helvetica", "", 14)
    pdf.set_text_color(*COLORS["muted"])
    pdf.cell(0, 10, "Rapport de simulation personnalise", align="C", new_x="LMARGIN", new_y="NEXT")

    # Accent bar
    pdf.set_fill_color(*COLORS["accent"])
    pdf.rect(80, pdf.get_y() + 5, 50, 2, "F")

    # Client & advisor info
    pdf.set_y(160)
    pdf.set_font("Helvetica", "", 12)
    pdf.set_text_color(*COLORS["text"])
    pdf.cell(0, 8, f"Client : {pdf.client_name}", align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(*COLORS["muted"])
    pdf.cell(0, 8, f"Conseiller : {pdf.advisor_name}", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, f"Date : {datetime.now().strftime('%d/%m/%Y %H:%M')}", align="C", new_x="LMARGIN", new_y="NEXT")

    # Disclaimer
    pdf.set_y(250)
    pdf.set_font("Helvetica", "I", 7)
    pdf.set_text_color(*COLORS["muted"])
    pdf.multi_cell(0, 4,
        "Ce rapport est fourni a titre indicatif et ne constitue pas un conseil financier. "
        "Les projections sont basees sur des hypotheses simplifiees. "
        "Consultez un professionnel certifie pour toute decision financiere.",
        align="C",
    )


def _add_section_title(pdf: FinanceAdvisorPDF, title: str):
    """Ajoute un titre de section avec barre d'accent."""
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(*COLORS["primary"])
    pdf.cell(0, 12, _clean_text(title), new_x="LMARGIN", new_y="NEXT")
    pdf.set_draw_color(*COLORS["primary"])
    pdf.set_line_width(0.8)
    pdf.line(10, pdf.get_y(), 60, pdf.get_y())
    pdf.ln(6)


def _add_kpi_row(pdf: FinanceAdvisorPDF, kpis: list[tuple[str, str]]):
    """Ajoute une rangee de KPI (label, value)."""
    col_width = (190 - 5 * (len(kpis) - 1)) / len(kpis)
    start_x = 10

    for i, (label, value) in enumerate(kpis):
        x = start_x + i * (col_width + 5)
        y = pdf.get_y()

        # Card background
        pdf.set_fill_color(*COLORS["bg_card"])
        pdf.rect(x, y, col_width, 22, "F")

        # Value
        pdf.set_xy(x + 2, y + 3)
        pdf.set_font("Helvetica", "B", 13)
        pdf.set_text_color(*COLORS["text"])
        pdf.cell(col_width - 4, 8, _clean_text(value), align="C")

        # Label
        pdf.set_xy(x + 2, y + 12)
        pdf.set_font("Helvetica", "", 8)
        pdf.set_text_color(*COLORS["muted"])
        pdf.cell(col_width - 4, 6, _clean_text(label), align="C")

    pdf.set_y(pdf.get_y() + 28)


def _add_table(pdf: FinanceAdvisorPDF, headers: list[str], rows: list[list[str]]):
    """Ajoute un tableau avec en-tetes colorees."""
    col_width = 190 / len(headers)

    # Headers
    pdf.set_fill_color(*COLORS["primary"])
    pdf.set_text_color(*COLORS["text"])
    pdf.set_font("Helvetica", "B", 9)
    for header in headers:
        pdf.cell(col_width, 8, _clean_text(header), border=0, fill=True, align="C")
    pdf.ln()

    # Rows
    pdf.set_font("Helvetica", "", 9)
    for i, row in enumerate(rows):
        if i % 2 == 0:
            pdf.set_fill_color(*COLORS["bg_card"])
        else:
            pdf.set_fill_color(20, 23, 35)

        pdf.set_text_color(*COLORS["text"])
        for cell in row:
            pdf.cell(col_width, 7, _clean_text(str(cell)), border=0, fill=True, align="C")
        pdf.ln()

    pdf.ln(5)


def _add_advice(pdf: FinanceAdvisorPDF, advices: list[tuple[str, str]]):
    """Ajoute des conseils (title, description)."""
    for title, desc in advices:
        y = pdf.get_y()
        if y > 260:
            pdf.add_page()
            y = pdf.get_y()

        pdf.set_fill_color(*COLORS["bg_card"])
        pdf.rect(10, y, 190, 18, "F")

        # Left accent bar
        pdf.set_fill_color(*COLORS["accent"])
        pdf.rect(10, y, 3, 18, "F")

        pdf.set_xy(16, y + 2)
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_text_color(*COLORS["text"])
        pdf.cell(180, 5, _clean_text(title))

        pdf.set_xy(16, y + 8)
        pdf.set_font("Helvetica", "", 8)
        pdf.set_text_color(*COLORS["muted"])
        pdf.multi_cell(178, 4, _clean_text(desc))

        pdf.set_y(y + 22)


# ═══════════════════════════════════════════════════════════════
# Fonctions d'export par module
# ═══════════════════════════════════════════════════════════════

def export_budget_pdf(
    advisor_name: str,
    client_name: str,
    params: dict,
    results: dict,
) -> bytes:
    """Genere un rapport PDF pour le module Budget."""
    pdf = FinanceAdvisorPDF(advisor_name, client_name, "Module Budget")
    pdf.alias_nb_pages()

    _add_cover_page(pdf, "Gestion Budgetaire")

    # Page 2 -- Resultats
    pdf.add_page()
    pdf.set_fill_color(*COLORS["dark"])
    pdf.rect(0, 0, 210, 297, "F")

    _add_section_title(pdf, "Bilan mensuel")
    _add_kpi_row(pdf, [
        ("Revenus totaux", f"CHF {results.get('revenu_total', 0):,}"),
        ("Depenses totales", f"CHF {results.get('total_depenses', 0):,}"),
        ("Solde disponible", f"CHF {results.get('solde', 0):,}"),
        ("Taux d'epargne", f"{results.get('taux_epargne', 0)}%"),
    ])

    # Detail revenus
    _add_section_title(pdf, "Detail des revenus")
    _add_table(pdf,
        ["Poste", "Montant mensuel"],
        [
            ["Salaire net", f"CHF {params.get('salaire_net', 0):,}"],
            ["Bonus / 13eme", f"CHF {params.get('bonus_mensuel', 0):,}"],
            ["Autres revenus", f"CHF {params.get('revenus_annexes', 0):,}"],
        ],
    )

    # Detail charges fixes
    _add_section_title(pdf, "Charges fixes")
    charges = [
        ("Loyer / Hypotheque", params.get("loyer", 0)),
        ("Assurance maladie", params.get("assurance_maladie", 0)),
        ("Impots", params.get("impots_mensuels", 0)),
        ("Transport", params.get("transport", 0)),
        ("Autres assurances", params.get("assurances_autres", 0)),
        ("Telecom", params.get("telecom", 0)),
        ("3eme pilier", params.get("prevoyance_3a", 0)),
    ]
    _add_table(pdf,
        ["Poste", "Montant mensuel"],
        [[label, f"CHF {val:,}"] for label, val in charges if val > 0],
    )

    # Detail depenses variables
    _add_section_title(pdf, "Depenses variables")
    variables = [
        ("Alimentation", params.get("alimentation", 0)),
        ("Restaurants", params.get("restaurants", 0)),
        ("Loisirs", params.get("loisirs", 0)),
        ("Habillement", params.get("habillement", 0)),
        ("Sante", params.get("sante", 0)),
        ("Vacances", params.get("vacances", 0)),
    ]
    _add_table(pdf,
        ["Poste", "Montant mensuel"],
        [[label, f"CHF {val:,}"] for label, val in variables if val > 0],
    )

    # Conseils
    advices = []
    rev = results.get("revenu_total", 1)
    if rev > 0 and params.get("loyer", 0) / rev * 100 > 33:
        advices.append(("Logement eleve", f"Le loyer represente {params['loyer']/rev*100:.1f}% du revenu (recommande : max 33%)."))
    if results.get("taux_epargne", 0) < 10:
        advices.append(("Taux d'epargne insuffisant", "L'ideal suisse est 15-20%. Identifiez les depenses a reduire."))
    elif results.get("taux_epargne", 0) >= 20:
        advices.append(("Excellent taux d'epargne", "Vous epargnez plus de 20%. Pensez a investir le surplus."))
    if params.get("prevoyance_3a", 0) < 588:
        advices.append(("Optimisez votre 3eme pilier", f"Vous versez CHF {params.get('prevoyance_3a', 0)}/mois. Le max est CHF 588/mois."))

    if advices:
        _add_section_title(pdf, "Conseils personnalises")
        _add_advice(pdf, advices)

    return bytes(pdf.output())


def export_fiscalite_pdf(
    advisor_name: str,
    client_name: str,
    params: dict,
    results: dict,
) -> bytes:
    """Genere un rapport PDF pour le module Fiscalite."""
    pdf = FinanceAdvisorPDF(advisor_name, client_name, "Module Fiscalite")
    pdf.alias_nb_pages()

    _add_cover_page(pdf, "Simulateur Fiscal")

    pdf.add_page()
    pdf.set_fill_color(*COLORS["dark"])
    pdf.rect(0, 0, 210, 297, "F")

    _add_section_title(pdf, "Resultats de la simulation")
    _add_kpi_row(pdf, [
        ("Impot total annuel", f"CHF {results.get('impot_total', 0):,.0f}"),
        ("Taux effectif", f"{results.get('taux_effectif', 0)}%"),
        ("Impot mensuel", f"CHF {results.get('impot_total', 0)/12:,.0f}"),
        ("Total deductions", f"CHF {results.get('total_deductions', 0):,.0f}"),
    ])

    _add_section_title(pdf, "Parametres")
    situation = params.get("marie", "Celibataire")
    _add_table(pdf,
        ["Parametre", "Valeur"],
        [
            ["Revenu annuel brut", f"CHF {params.get('revenu_brut', 0):,}"],
            ["Canton", params.get("canton", "--")],
            ["Commune", params.get("commune", "(Moyenne)")],
            ["Situation familiale", situation],
            ["Enfants", str(params.get("enfants", 0))],
            ["Deduction 3a", f"CHF {params.get('deduction_3a', 0):,}"],
            ["Rachat LPP", f"CHF {params.get('rachat_lpp', 0):,}"],
        ],
    )

    _add_section_title(pdf, "Decomposition de l'impot")
    _add_table(pdf,
        ["Niveau", "Montant"],
        [
            ["Federal", f"CHF {results.get('impot_federal', 0):,.0f}"],
            ["Cantonal", f"CHF {results.get('impot_cantonal', 0):,.0f}"],
            ["Communal", f"CHF {results.get('impot_communal', 0):,.0f}"],
        ],
    )

    return bytes(pdf.output())


def export_prevoyance_pdf(
    advisor_name: str,
    client_name: str,
    params: dict,
    results: dict,
) -> bytes:
    """Genere un rapport PDF pour le module Prevoyance."""
    pdf = FinanceAdvisorPDF(advisor_name, client_name, "Module Prevoyance")
    pdf.alias_nb_pages()

    _add_cover_page(pdf, "Prevoyance Retraite")

    pdf.add_page()
    pdf.set_fill_color(*COLORS["dark"])
    pdf.rect(0, 0, 210, 297, "F")

    _add_section_title(pdf, "Projection globale")
    _add_kpi_row(pdf, [
        ("Rente totale / mois", f"CHF {results.get('rente_totale_mensuelle', 0):,.0f}"),
        ("Taux remplacement", f"{results.get('taux_remplacement', 0)}%"),
        ("Gap mensuel", f"CHF {abs(results.get('gap_mensuel', 0)):,.0f}"),
    ])

    _add_section_title(pdf, "Detail par pilier")
    _add_table(pdf,
        ["Pilier", "Rente / mois", "Capital projete"],
        [
            ["1er Pilier (AVS)", f"CHF {results.get('rente_avs_mensuelle', 0):,.0f}", "--"],
            ["2eme Pilier (LPP)", f"CHF {results.get('rente_lpp_mensuelle', 0):,.0f}", f"CHF {results.get('capital_lpp_projete', 0):,.0f}"],
            ["3eme Pilier (3a)", "--", f"CHF {results.get('capital_3a_final', 0):,.0f}"],
        ],
    )

    _add_section_title(pdf, "Parametres utilises")
    _add_table(pdf,
        ["Parametre", "Valeur"],
        [
            ["Age actuel", str(params.get("age", "--"))],
            ["Salaire annuel", f"CHF {params.get('salaire', 0):,}"],
            ["Age de retraite", str(params.get("age_retraite", 65))],
            ["Capital LPP actuel", f"CHF {params.get('capital_lpp', 0):,}"],
            ["Capital 3a actuel", f"CHF {params.get('capital_3a_actuel', 0):,}"],
            ["Versement 3a annuel", f"CHF {params.get('versement_3a', 0):,}"],
        ],
    )

    # Gap analysis advice
    gap = results.get("gap_mensuel", 0)
    taux = results.get("taux_remplacement", 0)
    if gap > 0:
        _add_section_title(pdf, "Recommandations")
        _add_advice(pdf, [
            (f"Ecart de prevoyance : CHF {gap:,.0f}/mois",
             f"Votre rente projetee couvre {taux}% de votre revenu. L'objectif est 60-80%. "
             "Envisagez d'augmenter vos cotisations 3a, d'effectuer des rachats LPP, "
             "ou de constituer une epargne complementaire."),
        ])

    return bytes(pdf.output())


def export_investissements_pdf(
    advisor_name: str,
    client_name: str,
    params: dict,
    results: dict,
) -> bytes:
    """Genere un rapport PDF pour le module Investissements."""
    pdf = FinanceAdvisorPDF(advisor_name, client_name, "Module Investissements")
    pdf.alias_nb_pages()

    _add_cover_page(pdf, "Simulateur d'Investissement")

    pdf.add_page()
    pdf.set_fill_color(*COLORS["dark"])
    pdf.rect(0, 0, 210, 297, "F")

    _add_section_title(pdf, "Resultats de la simulation")
    _add_kpi_row(pdf, [
        ("Capital final", f"CHF {results.get('capital_final', 0):,.0f}"),
        ("Interets totaux", f"CHF {results.get('total_interets', 0):,.0f}"),
        ("Total verse", f"CHF {results.get('total_verse', 0):,.0f}"),
        ("Rendement total", f"{results.get('rendement_pct', 0):.1f}%"),
    ])

    _add_section_title(pdf, "Parametres de la simulation")
    taux = params.get("taux_annuel", 0)
    taux_str = f"{taux*100:.1f}%" if isinstance(taux, float) and taux < 1 else f"{taux}%"
    _add_table(pdf,
        ["Parametre", "Valeur"],
        [
            ["Capital initial", f"CHF {params.get('capital_initial', 0):,}"],
            ["Versement mensuel", f"CHF {params.get('versement_mensuel', 0):,}"],
            ["Rendement annuel", taux_str],
            ["Duree", f"{params.get('annees', 0)} ans"],
        ],
    )

    # Power of compound interest
    total_verse = results.get("total_verse", 0)
    total_interets = results.get("total_interets", 0)
    if total_verse > 0:
        pct_interets = round(total_interets / (total_verse + total_interets) * 100, 1)
        _add_section_title(pdf, "La puissance des interets composes")
        _add_advice(pdf, [
            (f"{pct_interets}% de votre capital final provient des interets",
             f"Sur {params.get('annees', 0)} ans, vos versements de CHF {total_verse:,.0f} ont genere "
             f"CHF {total_interets:,.0f} d'interets grace a l'effet boule de neige des interets composes."),
        ])

    return bytes(pdf.output())
