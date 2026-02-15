"""
Module Budget — Gestion budgétaire
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from pathlib import Path

css_path = Path(__file__).parent.parent / "assets" / "style.css"
if css_path.exists():
    st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)

from utils.auth import require_auth, sidebar_user_info, client_banner
from utils.database import init_db
from utils.simulation_manager import simulation_save_section, get_loaded_params

# Auth Guard 
require_auth()
sidebar_user_info()
init_db()

# Client context 
client = st.session_state.get("current_client")
client_salaire_net = round(client.get("salaire_annuel", 0) * 0.87 / 12) if client else 6_200
client_budget = (client or {}).get("_budget", {})

# Loaded simulation override 
loaded = get_loaded_params("budget")
if loaded:
    client_budget = loaded # Override with saved simulation params

# Titre 
st.markdown(
    """
    <div class="animate-in">
        <div class="premium-title"> Gestion Budgétaire</div>
        <div class="premium-subtitle">Maîtrisez vos finances personnelles · Revenus, charges et épargne</div>
    </div>
    """,
    unsafe_allow_html=True,
)

client_banner()

# Revenus 
st.markdown("### Revenus mensuels")
col1, col2, col3 = st.columns(3)

with col1:
    salaire_net = st.number_input("Salaire net mensuel (CHF)", 0, 50_000, client_budget.get("salaire_net", client_salaire_net), 100, key="sal")
with col2:
    bonus_mensuel = st.number_input("Bonus / 13ème (mensuel, CHF)", 0, 20_000, 0, 100, key="bonus")
with col3:
    revenus_annexes = st.number_input("Autres revenus (CHF)", 0, 20_000, 0, 100, key="autres_rev")

revenu_total = salaire_net + bonus_mensuel + revenus_annexes

# Charges Fixes 
st.markdown("---")
st.markdown("### Charges fixes mensuelles")

col1, col2, col3, col4 = st.columns(4)
with col1:
    loyer = st.number_input("Loyer / Hypothèque", 0, 10_000, client_budget.get("loyer", 1_800), 50, key="loyer")
with col2:
    assurance_maladie = st.number_input("Assurance maladie", 0, 2_000, client_budget.get("assurance_maladie", 380), 10, key="lamal")
with col3:
    impots_mensuels = st.number_input("Impôts (mensuel)", 0, 10_000, client_budget.get("impots_mensuels", 850), 50, key="impots")
with col4:
    transport = st.number_input("Transport (AG, auto)", 0, 3_000, client_budget.get("transport", 300), 25, key="transport")

col5, col6, col7, col8 = st.columns(4)
with col5:
    assurances_autres = st.number_input("Autres assurances", 0, 2_000, 150, 10, key="assur")
with col6:
    telecom = st.number_input("Télécom / Internet", 0, 500, 90, 10, key="telecom")
with col7:
    prevoyance_3a = st.number_input("3ème pilier (mensuel)", 0, 1_000, client_budget.get("prevoyance_3a", 588), 10, key="3a")
with col8:
    charges_autres = st.number_input("Autres charges fixes", 0, 5_000, 0, 50, key="charges_autres")

total_charges_fixes = loyer + assurance_maladie + impots_mensuels + transport + assurances_autres + telecom + prevoyance_3a + charges_autres

# Dépenses Variables 
st.markdown("---")
st.markdown("### Dépenses variables mensuelles")

col1, col2, col3, col4 = st.columns(4)
with col1:
    alimentation = st.number_input("Alimentation", 0, 5_000, client_budget.get("alimentation", 600), 25, key="alim")
with col2:
    restaurants = st.number_input("Restaurants / Sorties", 0, 3_000, 200, 25, key="resto")
with col3:
    loisirs = st.number_input("Loisirs / Sport", 0, 3_000, client_budget.get("loisirs", 150), 25, key="loisirs")
with col4:
    habillement = st.number_input("Habillement", 0, 2_000, 100, 25, key="habits")

col5, col6, col7, col8 = st.columns(4)
with col5:
    sante = st.number_input("Santé (non remboursé)", 0, 2_000, 50, 10, key="sante")
with col6:
    cadeaux = st.number_input("Cadeaux / Dons", 0, 2_000, 50, 10, key="cadeaux")
with col7:
    vacances = st.number_input("Vacances (mensuel)", 0, 3_000, 200, 25, key="vacances")
with col8:
    depenses_autres = st.number_input("Autres dépenses", 0, 5_000, 100, 25, key="dep_autres")

total_variables = alimentation + restaurants + loisirs + habillement + sante + cadeaux + vacances + depenses_autres

# Bilan 
st.markdown("---")

total_depenses = total_charges_fixes + total_variables
solde = revenu_total - total_depenses
taux_epargne = round((solde / revenu_total) * 100, 1) if revenu_total > 0 else 0

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-value">CHF {revenu_total:,}</div>
            <div class="kpi-label">Revenus totaux</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-value">CHF {total_depenses:,}</div>
            <div class="kpi-label">Dépenses totales</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col3:
    color = "#00D4AA" if solde >= 0 else "#FF6B6B"
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-value" style="background: {color}; -webkit-background-clip: text; -webkit-text-fill-color: transparent;">CHF {solde:,}</div>
            <div class="kpi-label">Solde disponible</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col4:
    epargne_color = "success" if taux_epargne >= 15 else ("" if taux_epargne >= 5 else "danger")
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-value">{taux_epargne}%</div>
            <div class="kpi-label">Taux d'épargne</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# Graphiques 
col_left, col_right = st.columns(2)

with col_left:
    st.markdown("### Répartition des dépenses")

    labels = ["Logement", "Assurance maladie", "Impôts", "Transport",
              "Alimentation", "Restaurants", "Loisirs", "Prévoyance 3a",
              "Assurances", "Télécom", "Habillement", "Santé", "Vacances",
              "Cadeaux", "Autres"]
    values = [loyer, assurance_maladie, impots_mensuels, transport,
              alimentation, restaurants, loisirs, prevoyance_3a,
              assurances_autres, telecom, habillement, sante, vacances,
              cadeaux, charges_autres + depenses_autres]

    # Filtrer les valeurs nulles
    data = [(l, v) for l, v in zip(labels, values) if v > 0]
    if data:
        labels_f, values_f = zip(*data)
    else:
        labels_f, values_f = ["Aucune dépense"], [1]

    colors = ["#6C63FF", "#3B82F6", "#FFB347", "#34E8C3", "#00D4AA",
              "#FF6B6B", "#8B83FF", "#4F46E5", "#A0A3B1", "#60A5FA",
              "#F472B6", "#FBBF24", "#22D3EE", "#A78BFA", "#6B7280"]

    fig = go.Figure(data=[go.Pie(
        labels=labels_f,
        values=values_f,
        hole=0.5,
        marker=dict(colors=colors[:len(labels_f)], line=dict(color='#0E1117', width=2)),
        textinfo='label+percent',
        textfont=dict(size=11, color='white', family='Inter'),
        hovertemplate="<b>%{label}</b><br>CHF %{value:,}<br>%{percent}<extra></extra>",
    )])

    fig.update_layout(
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=10, b=10, l=10, r=10),
        height=400,
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

with col_right:
    st.markdown("### Fixe vs Variable vs Épargne")

    categories_bar = ["Charges fixes", "Dépenses variables", "Épargne"]
    valeurs_bar = [total_charges_fixes, total_variables, max(solde, 0)]
    colors_bar = ["#6C63FF", "#FFB347", "#00D4AA"]

    fig2 = go.Figure(data=[go.Bar(
        x=categories_bar,
        y=valeurs_bar,
        marker=dict(
            color=colors_bar,
            line=dict(color='#0E1117', width=1),
            cornerradius=8,
        ),
        text=[f"CHF {v:,}" for v in valeurs_bar],
        textposition='outside',
        textfont=dict(color='white', size=13, family='Outfit'),
        hovertemplate="<b>%{x}</b><br>CHF %{y:,}<extra></extra>",
    )])

    fig2.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=30, b=20, l=20, r=20),
        height=400,
        xaxis=dict(showgrid=False, color='#A0A3B1', tickfont=dict(family='Inter')),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', color='#A0A3B1'),
    )
    st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

# Comparaison avec les moyennes suisses 
st.markdown("---")
st.markdown("### Comparaison avec les moyennes suisses")

comparaison_data = {
    "Catégorie": ["Logement", "Assurance maladie", "Alimentation", "Transport", "Impôts", "Loisirs", "Épargne"],
    "Vous (%)": [
        round(loyer / revenu_total * 100, 1) if revenu_total > 0 else 0,
        round(assurance_maladie / revenu_total * 100, 1) if revenu_total > 0 else 0,
        round(alimentation / revenu_total * 100, 1) if revenu_total > 0 else 0,
        round(transport / revenu_total * 100, 1) if revenu_total > 0 else 0,
        round(impots_mensuels / revenu_total * 100, 1) if revenu_total > 0 else 0,
        round(loisirs / revenu_total * 100, 1) if revenu_total > 0 else 0,
        round(max(solde, 0) / revenu_total * 100, 1) if revenu_total > 0 else 0,
    ],
    "Moyenne CH (%)": [33, 7, 11, 8, 12, 6, 12],
}

df = pd.DataFrame(comparaison_data)

fig3 = go.Figure()
fig3.add_trace(go.Bar(
    name="Vous",
    x=df["Catégorie"],
    y=df["Vous (%)"],
    marker_color="#6C63FF",
    text=[f"{v}%" for v in df["Vous (%)"]],
    textposition='outside',
    textfont=dict(color='white', size=11),
))
fig3.add_trace(go.Bar(
    name="Moyenne suisse",
    x=df["Catégorie"],
    y=df["Moyenne CH (%)"],
    marker_color="#3B82F6",
    text=[f"{v}%" for v in df["Moyenne CH (%)"]],
    textposition='outside',
    textfont=dict(color='#A0A3B1', size=11),
    opacity=0.6,
))

fig3.update_layout(
    barmode='group',
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    margin=dict(t=30, b=20, l=20, r=20),
    height=380,
    xaxis=dict(showgrid=False, color='#A0A3B1'),
    yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', color='#A0A3B1',
               title="% du revenu"),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                font=dict(color='#A0A3B1')),
)

st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})

# Conseils personnalisés 
st.markdown("---")
st.markdown("### Analyse personnalisée")

if revenu_total > 0:
    pct_logement = loyer / revenu_total * 100
    if pct_logement > 33:
        st.markdown(
            f"""
            <div class="suggestion-haute">
                <b> Logement élevé ({pct_logement:.1f}% du revenu)</b><br>
                <span style="color: #A0A3B1;">La règle des 33% est dépassée. Envisagez un logement plus abordable ou augmentez vos revenus.</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if taux_epargne < 10:
        st.markdown(
            """
            <div class="suggestion-haute">
                <b> Taux d'épargne insuffisant</b><br>
                <span style="color: #A0A3B1;">Votre taux d'épargne est inférieur à 10%. L'idéal suisse est de 15-20%. Identifiez les dépenses à réduire.</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    elif taux_epargne >= 20:
        st.markdown(
            """
            <div class="suggestion-info">
                <b> Excellent taux d'épargne !</b><br>
                <span style="color: #A0A3B1;">Vous épargnez plus de 20% de vos revenus. Pensez à investir le surplus pour le faire fructifier.</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if prevoyance_3a < 588:
        st.markdown(
            f"""
            <div class="suggestion-moyenne">
                <b> Optimisez votre 3ème pilier</b><br>
                <span style="color: #A0A3B1;">Vous versez CHF {prevoyance_3a}/mois. Le maximum est CHF 588/mois (CHF 7'056/an) pour une déduction fiscale complète.</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

# Sauvegarde 
budget_params = {
    "salaire_net": salaire_net, "bonus_mensuel": bonus_mensuel, "revenus_annexes": revenus_annexes,
    "loyer": loyer, "assurance_maladie": assurance_maladie, "impots_mensuels": impots_mensuels,
    "transport": transport, "assurances_autres": assurances_autres, "telecom": telecom,
    "prevoyance_3a": prevoyance_3a, "charges_autres": charges_autres,
    "alimentation": alimentation, "restaurants": restaurants, "loisirs": loisirs,
    "habillement": habillement, "sante": sante, "cadeaux": cadeaux,
    "vacances": vacances, "depenses_autres": depenses_autres,
}
budget_results = {
    "revenu_total": revenu_total, "total_charges_fixes": total_charges_fixes,
    "total_variables": total_variables, "total_depenses": total_depenses,
    "solde": solde, "taux_epargne": taux_epargne,
}

simulation_save_section("budget", budget_params, budget_results)

# Footer 
st.markdown(
    """
    <div class="footer-text">
        Finance Advisor Pro · Module Budget · Suisse Romande
    </div>
    """,
    unsafe_allow_html=True,
)
