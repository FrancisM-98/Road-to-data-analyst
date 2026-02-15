"""
Module Prévoyance — Les 3 piliers suisses
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.pillar_calc import (
    estimation_rente_avs,
    projection_lpp,
    simulation_3a,
    projection_retraite_globale,
)
from utils.constants import (
    PILIER_3A_SALARIE,
    RENTE_AVS_MAX_MENSUELLE,
    TAUX_CONVERSION_LPP,
    TAUX_INTERET_3A_MOYEN,
    TAUX_INTERET_3A_FONDS,
    AGE_RETRAITE_HOMMES,
)

css_path = Path(__file__).parent.parent / "assets" / "style.css"
if css_path.exists():
    st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)

from utils.auth import require_auth, sidebar_user_info, client_banner
from utils.database import init_db
from utils.simulation_manager import simulation_save_section, get_loaded_params

require_auth()
sidebar_user_info()
init_db()

# Client context 
client = st.session_state.get("current_client")
default_age = client.get("age", 35) if client else 35
default_salaire = int(client.get("salaire_annuel", 85_000)) if client else 85_000
default_lpp = int(client.get("capital_lpp", 50_000)) if client else 50_000
default_3a = int(client.get("capital_3a", 15_000)) if client else 15_000

# Titre 
st.markdown(
    """
    <div class="animate-in">
        <div class="premium-title"> Prévoyance Retraite</div>
        <div class="premium-subtitle">Planifiez votre retraite avec les 3 piliers du système suisse</div>
    </div>
    """,
    unsafe_allow_html=True,
)

client_banner()

# Paramètres globaux 
st.markdown("### Votre profil")

col1, col2, col3, col4 = st.columns(4)
with col1:
    age = st.slider("Votre âge", 20, 64, default_age, key="age_prev")
with col2:
    salaire = st.number_input("Salaire annuel brut (CHF)", 0, 500_000, default_salaire, 1_000, key="sal_prev")
with col3:
    age_retraite = st.slider("Âge de retraite souhaité", 58, 70, 65, key="age_ret")
with col4:
    annees_cotisation = st.slider("Années de cotisation AVS", 10, 44, min(default_age - 20, 44), key="annees_cot")

annees_restantes = max(0, age_retraite - age)

# Tabs des 3 piliers 
st.markdown("---")
tab1, tab2, tab3, tab4 = st.tabs([
    " 1er Pilier (AVS)",
    " 2ème Pilier (LPP)",
    " 3ème Pilier (3a/3b)",
    " Vue Globale",
])

# 1er Pilier 
with tab1:
    st.markdown("### AVS — Assurance vieillesse et survivants")
    st.markdown(
        """
        <div class="section-card">
            <b>Le 1er pilier</b> assure le minimum vital à la retraite.
            La rente dépend de vos années de cotisation et de votre revenu moyen.
            La rente maximale est de <b>CHF 2'450/mois</b> (simple) pour 44 années de cotisation complètes.
        </div>
        """,
        unsafe_allow_html=True,
    )

    avs = estimation_rente_avs(salaire, annees_cotisation)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-value">CHF {avs['rente_mensuelle']:,.0f}</div>
                <div class="kpi-label">Rente AVS / mois</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-value">CHF {avs['rente_annuelle']:,.0f}</div>
                <div class="kpi-label">Rente AVS / an</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col3:
        pct_complet = round(avs['fraction_cotisation'] * 100)
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-value">{pct_complet}%</div>
                <div class="kpi-label">Échelle de cotisation</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if avs["annees_manquantes"] > 0:
        st.markdown(
            f"""
            <div class="suggestion-moyenne">
                <b> {avs['annees_manquantes']} années de cotisation manquantes</b><br>
                <span style="color: #A0A3B1;">Des lacunes dans vos cotisations AVS réduisent votre rente.
                Vous pouvez racheter les 5 dernières années manquantes auprès de la caisse de compensation.</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Graphique sensibilité au salaire
    st.markdown("#### Sensibilité de la rente au salaire moyen")
    salaires_test = list(range(30_000, 150_001, 10_000))
    rentes_test = [estimation_rente_avs(s, annees_cotisation)["rente_mensuelle"] for s in salaires_test]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=salaires_test, y=rentes_test,
        mode='lines+markers',
        line=dict(color='#6C63FF', width=3),
        marker=dict(size=8, color='#6C63FF'),
        fill='tozeroy',
        fillcolor='rgba(108, 99, 255, 0.1)',
        hovertemplate="Salaire: CHF %{x:,.0f}<br>Rente: CHF %{y:,.0f}/mois<extra></extra>",
    ))
    fig.add_vline(x=salaire, line=dict(color='#00D4AA', width=2, dash='dash'))
    fig.add_annotation(x=salaire, y=max(rentes_test) * 0.9, text="Votre salaire",
                       font=dict(color='#00D4AA', size=12), showarrow=False)

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=20, b=20, l=40, r=20), height=350,
        xaxis=dict(title="Salaire annuel moyen (CHF)", showgrid=False, color='#A0A3B1',
                   tickformat=","),
        yaxis=dict(title="Rente mensuelle (CHF)", showgrid=True,
                   gridcolor='rgba(255,255,255,0.05)', color='#A0A3B1'),
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

# 2ème Pilier 
with tab2:
    st.markdown("### LPP — Prévoyance professionnelle")
    st.markdown(
        """
        <div class="section-card">
            <b>Le 2ème pilier</b> vise à maintenir votre niveau de vie à la retraite.
            Avec le 1er pilier, il doit couvrir environ <b>60%</b> de votre dernier salaire.
            Le taux de conversion actuel est de <b>6.8%</b>.
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)
    with col1:
        capital_lpp = st.number_input("Capital LPP actuel (CHF)", 0, 2_000_000, default_lpp, 5_000, key="cap_lpp")
    with col2:
        st.markdown(f"**Taux de conversion :** {TAUX_CONVERSION_LPP * 100}%")

    lpp = projection_lpp(salaire, age, capital_lpp, age_retraite)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-value">CHF {lpp['capital_projete']:,.0f}</div>
                <div class="kpi-label">Capital projeté à {age_retraite} ans</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-value">CHF {lpp['rente_mensuelle']:,.0f}</div>
                <div class="kpi-label">Rente LPP / mois</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-value">CHF {lpp.get('salaire_coordonne', 0):,.0f}</div>
                <div class="kpi-label">Salaire coordonné</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Graphique évolution du capital LPP
    if lpp["evolution"]:
        st.markdown("#### Projection du capital LPP")
        ages = [e["age"] for e in lpp["evolution"]]
        capitals = [e["capital"] for e in lpp["evolution"]]

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=ages, y=capitals,
            mode='lines',
            line=dict(color='#3B82F6', width=3),
            fill='tozeroy',
            fillcolor='rgba(59, 130, 246, 0.1)',
            hovertemplate="Âge: %{x}<br>Capital: CHF %{y:,.0f}<extra></extra>",
        ))

        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(t=20, b=20, l=40, r=20), height=350,
            xaxis=dict(title="Âge", showgrid=False, color='#A0A3B1'),
            yaxis=dict(title="Capital LPP (CHF)", showgrid=True,
                       gridcolor='rgba(255,255,255,0.05)', color='#A0A3B1', tickformat=","),
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

# 3ème Pilier 
with tab3:
    st.markdown("### 3ème Pilier — Épargne privée")
    st.markdown(
        f"""
        <div class="section-card">
            <b>Le 3ème pilier a (3a)</b> est une épargne individuelle liée, déductible fiscalement.
            Le plafond annuel 2025 pour un salarié est de <b>CHF {PILIER_3A_SALARIE:,}</b>.
            Vous pouvez choisir entre un compte bancaire (sûr, ~1.5%/an) et des fonds de placement (plus risqué, ~4.5%/an).
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        versement_3a = st.slider("Versement annuel (CHF)", 0, PILIER_3A_SALARIE, PILIER_3A_SALARIE, 100, key="vers_3a")
    with col2:
        capital_3a_actuel = st.number_input("Capital 3a actuel (CHF)", 0, 500_000, default_3a, 1_000, key="cap_3a")
    with col3:
        type_3a = st.radio("Type de placement", ["Compte bancaire (~1.5%)", "Fonds de placement (~4.5%)"], key="type_3a")

    taux_3a = TAUX_INTERET_3A_MOYEN if "bancaire" in type_3a else TAUX_INTERET_3A_FONDS

    sim_3a = simulation_3a(versement_3a, annees_restantes, taux_3a, capital_3a_actuel)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-value">CHF {sim_3a['capital_final']:,.0f}</div>
                <div class="kpi-label">Capital à {age_retraite} ans</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-value">CHF {sim_3a['total_interets']:,.0f}</div>
                <div class="kpi-label">Intérêts cumulés</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-value">{sim_3a['rendement_total_pct']}%</div>
                <div class="kpi-label">Rendement total</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Graphique évolution 3a
    if sim_3a["evolution"]:
        st.markdown("#### Projection du capital 3a")
        annees_ev = [e["annee"] for e in sim_3a["evolution"]]
        capital_ev = [e["capital"] for e in sim_3a["evolution"]]
        verse_ev = [e["verse"] for e in sim_3a["evolution"]]

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=annees_ev, y=capital_ev,
            mode='lines', name='Capital total',
            line=dict(color='#00D4AA', width=3),
            fill='tozeroy', fillcolor='rgba(0, 212, 170, 0.1)',
            hovertemplate="Année %{x}<br>Capital: CHF %{y:,.0f}<extra></extra>",
        ))
        fig.add_trace(go.Scatter(
            x=annees_ev, y=verse_ev,
            mode='lines', name='Montant versé',
            line=dict(color='#6C63FF', width=2, dash='dash'),
            hovertemplate="Année %{x}<br>Versé: CHF %{y:,.0f}<extra></extra>",
        ))

        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(t=20, b=20, l=40, r=20), height=350,
            xaxis=dict(title="Années", showgrid=False, color='#A0A3B1'),
            yaxis=dict(title="CHF", showgrid=True,
                       gridcolor='rgba(255,255,255,0.05)', color='#A0A3B1', tickformat=","),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                        font=dict(color='#A0A3B1')),
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # Comparaison compte vs fonds
    st.markdown("#### Compte bancaire vs Fonds de placement")
    sim_compte = simulation_3a(versement_3a, annees_restantes, TAUX_INTERET_3A_MOYEN, capital_3a_actuel)
    sim_fonds = simulation_3a(versement_3a, annees_restantes, TAUX_INTERET_3A_FONDS, capital_3a_actuel)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            f"""
            <div class="section-card">
                <b> Compte bancaire (~1.5%/an)</b><br><br>
                Capital final : <b style="color: #6C63FF;">CHF {sim_compte['capital_final']:,.0f}</b><br>
                Intérêts cumulés : CHF {sim_compte['total_interets']:,.0f}<br>
                <span class="risk-badge risk-low">Risque faible</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f"""
            <div class="section-card">
                <b> Fonds de placement (~4.5%/an)</b><br><br>
                Capital final : <b style="color: #00D4AA;">CHF {sim_fonds['capital_final']:,.0f}</b><br>
                Intérêts cumulés : CHF {sim_fonds['total_interets']:,.0f}<br>
                <span class="risk-badge risk-medium">Risque modéré</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    diff = sim_fonds["capital_final"] - sim_compte["capital_final"]
    if diff > 0:
        st.markdown(
            f"""
            <div class="suggestion-haute">
                <b> Différence fonds vs compte : + CHF {diff:,.0f}</b><br>
                <span style="color: #A0A3B1;">Sur {annees_restantes} ans, les fonds de placement génèrent potentiellement CHF {diff:,.0f} de plus, mais avec un risque de perte à court terme.</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

# Vue Globale 
with tab4:
    st.markdown("### Projection globale de la retraite")

    projection = projection_retraite_globale(
        salaire_annuel=salaire,
        age_actuel=age,
        capital_lpp_actuel=capital_lpp if 'capital_lpp' in dir() else 50_000,
        capital_3a_actuel=capital_3a_actuel if 'capital_3a_actuel' in dir() else 15_000,
        versement_3a_annuel=versement_3a if 'versement_3a' in dir() else PILIER_3A_SALARIE,
        taux_rendement_3a=taux_3a if 'taux_3a' in dir() else TAUX_INTERET_3A_MOYEN,
        annees_cotisation_avs=annees_cotisation,
        age_retraite=age_retraite,
    )

    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-value">CHF {projection['rente_totale_mensuelle']:,.0f}</div>
                <div class="kpi-label">Rente totale / mois</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        taux_color = "#00D4AA" if projection['taux_remplacement'] >= 60 else "#FFB347" if projection['taux_remplacement'] >= 40 else "#FF6B6B"
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-value" style="background: {taux_color}; -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{projection['taux_remplacement']}%</div>
                <div class="kpi-label">Taux de remplacement</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-value">CHF {projection['revenu_mensuel_actuel']:,.0f}</div>
                <div class="kpi-label">Revenu actuel / mois</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col4:
        gap_color = "#FF6B6B" if projection['gap_mensuel'] > 0 else "#00D4AA"
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-value" style="background: {gap_color}; -webkit-background-clip: text; -webkit-text-fill-color: transparent;">CHF {abs(projection['gap_mensuel']):,.0f}</div>
                <div class="kpi-label">{"Écart mensuel" if projection['gap_mensuel'] > 0 else "Surplus mensuel"}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Graphique de répartition des piliers
    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("#### Répartition de la rente par pilier")
        avs_rente = projection["avs"]["rente_mensuelle"]
        lpp_rente = projection["lpp"]["rente_mensuelle"]
        p3a_rente = round(projection["pilier_3a"]["capital_final"] / (20 * 12), 2)

        fig = go.Figure(data=[go.Pie(
            labels=["1er Pilier (AVS)", "2ème Pilier (LPP)", "3ème Pilier (3a)"],
            values=[avs_rente, lpp_rente, p3a_rente],
            hole=0.55,
            marker=dict(
                colors=["#6C63FF", "#3B82F6", "#00D4AA"],
                line=dict(color='#0E1117', width=2),
            ),
            textinfo='label+percent',
            textfont=dict(size=12, color='white', family='Inter'),
            hovertemplate="<b>%{label}</b><br>CHF %{value:,.0f}/mois<br>%{percent}<extra></extra>",
        )])

        fig.update_layout(
            showlegend=False,
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(t=20, b=20, l=20, r=20), height=350,
            annotations=[dict(
                text=f"<b>CHF {projection['rente_totale_mensuelle']:,.0f}</b><br><span style='font-size:11px;color:#A0A3B1'>/mois</span>",
                x=0.5, y=0.5,
                font=dict(size=16, color='white', family='Outfit'),
                showarrow=False,
            )],
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with col_right:
        st.markdown("#### Revenu actuel vs Rente projetée")

        fig2 = go.Figure()
        fig2.add_trace(go.Bar(
            x=["Revenu actuel"],
            y=[projection["revenu_mensuel_actuel"]],
            name="Revenu actuel",
            marker=dict(color="#6C63FF", cornerradius=8),
            text=[f"CHF {projection['revenu_mensuel_actuel']:,.0f}"],
            textposition='outside',
            textfont=dict(color='white', size=12, family='Outfit'),
            width=0.4,
        ))
        fig2.add_trace(go.Bar(
            x=["Rente projetée"],
            y=[projection["rente_totale_mensuelle"]],
            name="Rente projetée",
            marker=dict(color="#00D4AA", cornerradius=8),
            text=[f"CHF {projection['rente_totale_mensuelle']:,.0f}"],
            textposition='outside',
            textfont=dict(color='white', size=12, family='Outfit'),
            width=0.4,
        ))

        fig2.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(t=40, b=20, l=20, r=20), height=350, showlegend=False,
            xaxis=dict(showgrid=False, color='#A0A3B1'),
            yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', color='#A0A3B1', tickformat=","),
        )
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

    # Gap analysis
    if projection["gap_mensuel"] > 0:
        st.markdown(
            f"""
            <div class="suggestion-haute">
                <b> Écart de prévoyance : CHF {projection['gap_mensuel']:,.0f}/mois</b><br>
                <span style="color: #A0A3B1;">
                    Votre rente projetée couvre {projection['taux_remplacement']}% de votre revenu actuel.
                    L'objectif recommandé est de 60-80%. Envisagez d'augmenter vos cotisations 3a, d'effectuer des rachats LPP,
                    ou de constituer une épargne complémentaire.
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

# Sauvegarde 
prev_params = {
    "age": age, "salaire": salaire, "age_retraite": age_retraite,
    "annees_cotisation": annees_cotisation,
    "capital_lpp": capital_lpp if 'capital_lpp' in dir() else default_lpp,
    "capital_3a_actuel": capital_3a_actuel if 'capital_3a_actuel' in dir() else default_3a,
    "versement_3a": versement_3a if 'versement_3a' in dir() else PILIER_3A_SALARIE,
    "type_3a": type_3a if 'type_3a' in dir() else "Compte bancaire (~1.5%)",
}
prev_results = {
    "rente_avs_mensuelle": avs["rente_mensuelle"],
    "rente_lpp_mensuelle": lpp["rente_mensuelle"] if 'lpp' in dir() else 0,
    "capital_lpp_projete": lpp["capital_projete"] if 'lpp' in dir() else 0,
    "capital_3a_final": sim_3a["capital_final"] if 'sim_3a' in dir() else 0,
    "rente_totale_mensuelle": projection["rente_totale_mensuelle"],
    "taux_remplacement": projection["taux_remplacement"],
    "gap_mensuel": projection["gap_mensuel"],
}

simulation_save_section("prevoyance", prev_params, prev_results)

# Footer 
st.markdown(
    """
    <div class="footer-text">
        Finance Advisor · Module Prévoyance · Suisse Romande<br>
        Les projections sont basées sur des hypothèses simplifiées et ne garantissent pas les résultats futurs
    </div>
    """,
    unsafe_allow_html=True,
)
