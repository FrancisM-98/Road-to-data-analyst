"""
🏛️ Module Fiscalité — Simulateur fiscal suisse
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.swiss_tax import calcul_impot_total, comparaison_cantonale, suggestions_optimisation
from utils.constants import CANTONS_ROMANDS, PILIER_3A_SALARIE

css_path = Path(__file__).parent.parent / "assets" / "style.css"
if css_path.exists():
    st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)

from utils.auth import require_auth, sidebar_user_info, client_banner
from utils.database import init_db
from utils.simulation_manager import simulation_save_section, get_loaded_params

require_auth()
sidebar_user_info()
init_db()

# ─── Client context ──────────────────────────────────────────
client = st.session_state.get("current_client")
cantons_list = list(CANTONS_ROMANDS.keys())
default_canton_idx = cantons_list.index(client["canton"]) if client and client.get("canton") in cantons_list else 0
default_salaire = int(client.get("salaire_annuel", 85_000)) if client else 85_000
default_enfants = client.get("enfants", 0) if client else 0
default_marie = client.get("situation_familiale", "") in ["Marié·e", "Marié·e"] if client else False

# ─── Titre ───────────────────────────────────────────────────
st.markdown(
    """
    <div class="animate-in">
        <div class="premium-title">🏛️ Simulateur Fiscal</div>
        <div class="premium-subtitle">Estimez vos impôts et optimisez votre situation fiscale · Cantons romands</div>
    </div>
    """,
    unsafe_allow_html=True,
)

client_banner()

# ─── Paramètres ──────────────────────────────────────────────
st.markdown("### 📋 Votre situation")

col1, col2, col3 = st.columns(3)
with col1:
    revenu_brut = st.number_input("Revenu annuel brut (CHF)", 0, 1_000_000, default_salaire, 1_000, key="rev_brut")
with col2:
    canton = st.selectbox("Canton", cantons_list, index=default_canton_idx, key="canton_select")
with col3:
    communes_list = list(CANTONS_ROMANDS[canton].get("communes", {}).keys())
    default_commune_list = ["(Moyenne)"] + communes_list
    commune_idx = default_commune_list.index(client["commune"]) if client and client.get("commune") in default_commune_list else 0
    commune = st.selectbox("Commune", default_commune_list, index=commune_idx, key="commune_select")

commune_val = None if commune == "(Moyenne)" else commune

col4, col5, col6 = st.columns(3)
with col4:
    marie = st.selectbox("Situation familiale", ["Célibataire", "Marié·e"], index=1 if default_marie else 0, key="situation_fisc")
    is_marie = marie == "Marié·e"
with col5:
    enfants = st.number_input("Nombre d'enfants", 0, 10, default_enfants, key="enfants_fisc")
with col6:
    deduction_3a = st.slider(
        "Versement 3ème pilier (CHF/an)",
        0, PILIER_3A_SALARIE, PILIER_3A_SALARIE, 100,
        key="ded_3a",
    )

with st.expander("🔧 Déductions supplémentaires"):
    col_a, col_b = st.columns(2)
    with col_a:
        rachat_lpp = st.number_input("Rachat LPP (CHF)", 0, 200_000, 0, 1_000, key="rachat_lpp")
    with col_b:
        frais_effectifs = st.number_input("Frais effectifs (CHF)", 0, 50_000, 0, 500, key="frais_eff")

# ─── Calcul ──────────────────────────────────────────────────
result = calcul_impot_total(
    revenu_brut=revenu_brut,
    canton=canton,
    commune=commune_val,
    marie=is_marie,
    enfants=enfants,
    deduction_3a=deduction_3a,
    deduction_rachat_lpp=rachat_lpp,
    deduction_frais_effectifs=frais_effectifs,
)

# ─── Résultats ───────────────────────────────────────────────
st.markdown("---")
st.markdown("### 💰 Résultats de la simulation")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-emoji">🏛️</div>
            <div class="kpi-value">CHF {result['impot_total']:,.0f}</div>
            <div class="kpi-label">Impôt total annuel</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-emoji">📊</div>
            <div class="kpi-value">{result['taux_effectif']}%</div>
            <div class="kpi-label">Taux effectif</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col3:
    impot_mensuel = round(result['impot_total'] / 12)
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-emoji">📅</div>
            <div class="kpi-value">CHF {impot_mensuel:,}</div>
            <div class="kpi-label">Impôt mensuel</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col4:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-emoji">📝</div>
            <div class="kpi-value">CHF {result['total_deductions']:,.0f}</div>
            <div class="kpi-label">Total déductions</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# ─── Détail des impôts ──────────────────────────────────────
col_left, col_right = st.columns(2)

with col_left:
    st.markdown("### 📊 Décomposition de l'impôt")

    fig = go.Figure(data=[go.Pie(
        labels=["Fédéral", "Cantonal", "Communal"],
        values=[result["impot_federal"], result["impot_cantonal"], result["impot_communal"]],
        hole=0.55,
        marker=dict(
            colors=["#6C63FF", "#3B82F6", "#00D4AA"],
            line=dict(color='#0E1117', width=2),
        ),
        textinfo='label+percent',
        textfont=dict(size=13, color='white', family='Inter'),
        hovertemplate="<b>%{label}</b><br>CHF %{value:,.0f}<br>%{percent}<extra></extra>",
    )])

    fig.update_layout(
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=20, b=20, l=20, r=20),
        height=350,
        annotations=[dict(
            text=f"<b>CHF {result['impot_total']:,.0f}</b>",
            x=0.5, y=0.5,
            font=dict(size=18, color='white', family='Outfit'),
            showarrow=False,
        )],
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

with col_right:
    st.markdown("### 📝 Détail des déductions")

    deductions = result["detail_deductions"]
    for label, montant in deductions.items():
        if montant > 0:
            pct = round(montant / result["total_deductions"] * 100, 1) if result["total_deductions"] > 0 else 0
            st.markdown(
                f"""
                <div class="section-card" style="padding: 0.75rem 1rem; margin-bottom: 0.5rem;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-size: 0.9rem;">{label}</span>
                        <span style="font-weight: 700; color: #00D4AA;">CHF {montant:,.0f}</span>
                    </div>
                    <div class="progress-container" style="height: 6px; margin-top: 0.4rem;">
                        <div class="progress-bar success" style="width: {min(pct, 100)}%"></div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

# ─── Comparaison cantonale ───────────────────────────────────
st.markdown("---")
st.markdown("### 🗺️ Comparaison inter-cantonale")

comparaison = comparaison_cantonale(revenu_brut, is_marie, enfants, deduction_3a)

cantons_noms = list(comparaison.keys())
impots_totaux = [comparaison[c]["impot_total"] for c in cantons_noms]
taux_effectifs = [comparaison[c]["taux_effectif"] for c in cantons_noms]

# Trier par impôt croissant
sorted_data = sorted(zip(cantons_noms, impots_totaux, taux_effectifs), key=lambda x: x[1])
cantons_sorted, impots_sorted, taux_sorted = zip(*sorted_data)

# Colorer le canton actuel
colors = ["#00D4AA" if c == canton else "#6C63FF" for c in cantons_sorted]

fig2 = go.Figure(data=[go.Bar(
    x=list(cantons_sorted),
    y=list(impots_sorted),
    marker=dict(color=colors, line=dict(color='#0E1117', width=1), cornerradius=6),
    text=[f"CHF {v:,.0f}" for v in impots_sorted],
    textposition='outside',
    textfont=dict(color='white', size=11, family='Outfit'),
    hovertemplate="<b>%{x}</b><br>Impôt: CHF %{y:,.0f}<extra></extra>",
)])

fig2.update_layout(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    margin=dict(t=40, b=20, l=20, r=20),
    height=400,
    xaxis=dict(showgrid=False, color='#A0A3B1', tickfont=dict(size=10, family='Inter'), tickangle=-30),
    yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', color='#A0A3B1', title="Impôt total (CHF)"),
)

st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

# Canton le moins cher
canton_min = cantons_sorted[0]
impot_min = impots_sorted[0]
impot_actuel = comparaison[canton]["impot_total"]
economie = impot_actuel - impot_min

if economie > 0 and canton != canton_min:
    st.markdown(
        f"""
        <div class="suggestion-info">
            <b>🗺️ Le canton le plus avantageux est {canton_min}</b><br>
            <span style="color: #A0A3B1;">Économie potentielle de <b>CHF {economie:,.0f}/an</b> par rapport à votre canton actuel ({canton}).</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ─── Suggestions d'optimisation ─────────────────────────────
st.markdown("---")
st.markdown("### 💡 Optimisations fiscales recommandées")

suggestions = suggestions_optimisation(
    revenu_brut=revenu_brut,
    deduction_3a_actuelle=deduction_3a,
    rachat_lpp_actuel=rachat_lpp,
    canton=canton,
    marie=is_marie,
    enfants=enfants,
)

if suggestions:
    for s in suggestions:
        css_class = f"suggestion-{s['priorite']}"
        st.markdown(
            f"""
            <div class="{css_class}">
                <b>{s['titre']}</b><br>
                <span style="color: #A0A3B1;">{s['description']}</span><br>
                <span style="color: #00D4AA; font-weight: 700;">💰 Économie estimée : CHF {s['economie_estimee']:,.0f}/an</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
else:
    st.markdown(
        """
        <div class="suggestion-info">
            <b>✅ Votre situation semble déjà bien optimisée !</b><br>
            <span style="color: #A0A3B1;">Continuez à maximiser votre 3ème pilier et surveillez les évolutions législatives.</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ─── Sauvegarde ──────────────────────────────────────────────
fisc_params = {
    "revenu_brut": revenu_brut, "canton": canton, "commune": commune,
    "marie": marie, "enfants": enfants, "deduction_3a": deduction_3a,
    "rachat_lpp": rachat_lpp, "frais_effectifs": frais_effectifs,
}
fisc_results = {
    "impot_total": result["impot_total"], "taux_effectif": result["taux_effectif"],
    "impot_federal": result["impot_federal"], "impot_cantonal": result["impot_cantonal"],
    "impot_communal": result["impot_communal"], "total_deductions": result["total_deductions"],
}

simulation_save_section("fiscalite", fisc_params, fisc_results)

# ─── Footer ──────────────────────────────────────────────────
st.markdown(
    """
    <div class="footer-text">
        Finance Advisor · Module Fiscalité · Suisse Romande<br>
        ⚠️ Estimation simplifiée — Consultez un fiduciaire pour une déclaration exacte
    </div>
    """,
    unsafe_allow_html=True,
)
