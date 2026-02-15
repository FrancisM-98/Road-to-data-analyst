"""
Module Investissements — Simulateur d'investissement
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.investment import interets_composes, simulation_monte_carlo, cout_opportunite, comparer_scenarios
from utils.constants import PROFILS_INVESTISSEMENT

css_path = Path(__file__).parent.parent / "assets" / "style.css"
if css_path.exists():
    st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)

from utils.auth import require_auth, sidebar_user_info, client_banner
from utils.database import init_db
from utils.simulation_manager import simulation_save_section, get_loaded_params

require_auth()
sidebar_user_info()
init_db()

# Titre 
st.markdown(
    """
    <div class="animate-in">
        <div class="premium-title"> Simulateur d'Investissement</div>
        <div class="premium-subtitle">Projetez la croissance de votre patrimoine · Intérêts composés & Monte Carlo</div>
    </div>
    """,
    unsafe_allow_html=True,
)

client_banner()

# Tabs 
tab1, tab2, tab3, tab4 = st.tabs([
    " Calculateur",
    " Profils & Comparaison",
    " Monte Carlo",
    " Coût d'opportunité",
])

# Tab 1 : Calculateur d'intérêts composés 
with tab1:
    st.markdown("### Calculateur d'intérêts composés")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        capital_initial = st.number_input("Capital initial (CHF)", 0, 5_000_000, 10_000, 1_000, key="cap_init")
    with col2:
        versement_mensuel = st.number_input("Versement mensuel (CHF)", 0, 50_000, 500, 50, key="vers_mens")
    with col3:
        taux_annuel = st.slider("Rendement annuel (%)", 0.0, 15.0, 6.0, 0.5, key="taux_an") / 100
    with col4:
        annees = st.slider("Durée (années)", 1, 50, 20, 1, key="duree_inv")

    result = interets_composes(capital_initial, versement_mensuel, taux_annuel, annees)

    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-value">CHF {result['capital_final']:,.0f}</div>
                <div class="kpi-label">Capital final</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-value">CHF {result['total_interets']:,.0f}</div>
                <div class="kpi-label">Intérêts totaux</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-value">CHF {result['total_verse']:,.0f}</div>
                <div class="kpi-label">Total versé</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col4:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-value">{result['rendement_pct']:.1f}%</div>
                <div class="kpi-label">Rendement total</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Graphique
    if result["evolution"]:
        annees_ev = [e["annee"] for e in result["evolution"]]
        capital_ev = [e["capital"] for e in result["evolution"]]
        verse_ev = [e["verse"] for e in result["evolution"]]
        interets_ev = [e["interets_cumules"] for e in result["evolution"]]

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=annees_ev, y=verse_ev,
            mode='lines', name='Montant versé',
            line=dict(color='#6C63FF', width=2),
            stackgroup='one',
            fillcolor='rgba(108, 99, 255, 0.3)',
            hovertemplate="Année %{x}<br>Versé: CHF %{y:,.0f}<extra></extra>",
        ))
        fig.add_trace(go.Scatter(
            x=annees_ev, y=interets_ev,
            mode='lines', name='Intérêts cumulés',
            line=dict(color='#00D4AA', width=2),
            stackgroup='one',
            fillcolor='rgba(0, 212, 170, 0.3)',
            hovertemplate="Année %{x}<br>Intérêts: CHF %{y:,.0f}<extra></extra>",
        ))

        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(t=30, b=20, l=40, r=20), height=420,
            xaxis=dict(title="Années", showgrid=False, color='#A0A3B1'),
            yaxis=dict(title="CHF", showgrid=True, gridcolor='rgba(255,255,255,0.05)',
                       color='#A0A3B1', tickformat=","),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                        font=dict(color='#A0A3B1')),
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

# Tab 2 : Profils & Comparaison 
with tab2:
    st.markdown("### Profils d'investissement")

    # Afficher les profils
    cols = st.columns(len(PROFILS_INVESTISSEMENT))
    for i, (nom, profil) in enumerate(PROFILS_INVESTISSEMENT.items()):
        risk_class = ["risk-low", "risk-medium", "risk-high", "risk-extreme"][i]
        allocation_html = "<br>".join([f"• {k}: {v}%" for k, v in profil["allocation"].items()])
        with cols[i]:
            st.markdown(
                f"""
                <div class="section-card" style="text-align: center; min-height: 280px;">
                    <h4 style="margin: 0.5rem 0;">{nom}</h4>
                    <p style="color: #A0A3B1; font-size: 0.85rem;">{profil['description']}</p>
                    <p style="font-size: 1.2rem; font-weight: 700; color: #00D4AA;">{profil['rendement_moyen']*100:.1f}%/an</p>
                    <span class="risk-badge {risk_class}">Vol. {profil['volatilite']*100:.0f}%</span>
                    <div style="text-align: left; margin-top: 1rem; font-size: 0.8rem; color: #A0A3B1;">
                        {allocation_html}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # Comparaison
    st.markdown("---")
    st.markdown("### Comparaison des scénarios")

    col1, col2, col3 = st.columns(3)
    with col1:
        cap_comp = st.number_input("Capital initial (CHF)", 0, 5_000_000, 10_000, 1_000, key="cap_comp")
    with col2:
        vers_comp = st.number_input("Versement mensuel (CHF)", 0, 50_000, 500, 50, key="vers_comp")
    with col3:
        dur_comp = st.slider("Durée (années)", 5, 50, 20, 1, key="dur_comp")

    resultats = comparer_scenarios(cap_comp, vers_comp, dur_comp, PROFILS_INVESTISSEMENT)

    fig = go.Figure()
    colors = ["#00D4AA", "#6C63FF", "#FFB347", "#FF6B6B"]

    for i, (nom, data) in enumerate(resultats.items()):
        evolution = data["deterministe"]["evolution"]
        annees_ev = [e["annee"] for e in evolution]
        capital_ev = [e["capital"] for e in evolution]

        fig.add_trace(go.Scatter(
            x=annees_ev, y=capital_ev,
            mode='lines', name=nom,
            line=dict(color=colors[i], width=3),
            hovertemplate=f"<b>{nom}</b><br>Année %{{x}}<br>Capital: CHF %{{y:,.0f}}<extra></extra>",
        ))

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=30, b=20, l=40, r=20), height=450,
        xaxis=dict(title="Années", showgrid=False, color='#A0A3B1'),
        yaxis=dict(title="Capital (CHF)", showgrid=True, gridcolor='rgba(255,255,255,0.05)',
                   color='#A0A3B1', tickformat=","),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                    font=dict(color='#A0A3B1', size=12)),
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # Tableau comparatif
    st.markdown("#### Résultats comparatifs")
    tableau_data = []
    for nom, data in resultats.items():
        d = data["deterministe"]
        mc = data["monte_carlo"]
        tableau_data.append({
            "Profil": nom,
            "Capital final": f"CHF {d['capital_final']:,.0f}",
            "Total versé": f"CHF {d['total_verse']:,.0f}",
            "Intérêts": f"CHF {d['total_interets']:,.0f}",
            "Rendement": f"{d['rendement_pct']:.1f}%",
            "Prob. perte": f"{mc['probabilite_perte']:.1f}%",
        })

    df = pd.DataFrame(tableau_data)
    st.dataframe(df, use_container_width=True, hide_index=True)

# Tab 3 : Simulation Monte Carlo 
with tab3:
    st.markdown("### Simulation Monte Carlo")
    st.markdown(
        """
        <div class="section-card">
            La simulation Monte Carlo génère <b>500 scénarios aléatoires</b> pour estimer la distribution
            probable de vos résultats d'investissement. Elle prend en compte la volatilité du marché
            pour montrer l'éventail des résultats possibles.
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        cap_mc = st.number_input("Capital initial (CHF)", 0, 5_000_000, 20_000, 1_000, key="cap_mc")
    with col2:
        vers_mc = st.number_input("Versement mensuel (CHF)", 0, 50_000, 500, 50, key="vers_mc")
    with col3:
        profil_mc = st.selectbox("Profil de risque", list(PROFILS_INVESTISSEMENT.keys()), index=1, key="profil_mc")
    with col4:
        dur_mc = st.slider("Durée (années)", 5, 40, 20, 1, key="dur_mc")

    profil_info = PROFILS_INVESTISSEMENT[profil_mc]
    mc = simulation_monte_carlo(
        cap_mc, vers_mc,
        profil_info["rendement_moyen"],
        profil_info["volatilite"],
        dur_mc,
    )

    # KPIs Monte Carlo
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-value">CHF {mc['mediane']:,.0f}</div>
                <div class="kpi-label">Médiane (50%)</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-value">CHF {mc['percentile_5']:,.0f}</div>
                <div class="kpi-label">Pessimiste (5%)</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-value">CHF {mc['percentile_95']:,.0f}</div>
                <div class="kpi-label">Optimiste (95%)</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col4:
        prob_color = "#00D4AA" if mc["probabilite_perte"] < 20 else "#FFB347" if mc["probabilite_perte"] < 40 else "#FF6B6B"
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-value" style="background: {prob_color}; -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{mc['probabilite_perte']:.1f}%</div>
                <div class="kpi-label">Probabilité de perte</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Graphique des percentiles
    percentiles = mc["percentiles_evolution"]
    annees_mc = [e["annee"] for e in percentiles[50]]
    p5 = [e["valeur"] for e in percentiles[5]]
    p25 = [e["valeur"] for e in percentiles[25]]
    p50 = [e["valeur"] for e in percentiles[50]]
    p75 = [e["valeur"] for e in percentiles[75]]
    p95 = [e["valeur"] for e in percentiles[95]]

    fig = go.Figure()

    # Bande 5-95%
    fig.add_trace(go.Scatter(
        x=annees_mc + annees_mc[::-1],
        y=p95 + p5[::-1],
        fill='toself', fillcolor='rgba(108, 99, 255, 0.08)',
        line=dict(color='rgba(0,0,0,0)'),
        name='5% - 95%',
        hoverinfo='skip',
    ))

    # Bande 25-75%
    fig.add_trace(go.Scatter(
        x=annees_mc + annees_mc[::-1],
        y=p75 + p25[::-1],
        fill='toself', fillcolor='rgba(108, 99, 255, 0.15)',
        line=dict(color='rgba(0,0,0,0)'),
        name='25% - 75%',
        hoverinfo='skip',
    ))

    # Médiane
    fig.add_trace(go.Scatter(
        x=annees_mc, y=p50,
        mode='lines', name='Médiane',
        line=dict(color='#6C63FF', width=3),
        hovertemplate="Année %{x}<br>Médiane: CHF %{y:,.0f}<extra></extra>",
    ))

    # Ligne du capital versé
    total_verse_ev = [cap_mc + vers_mc * 12 * a for a in annees_mc]
    fig.add_trace(go.Scatter(
        x=annees_mc, y=total_verse_ev,
        mode='lines', name='Capital versé',
        line=dict(color='#A0A3B1', width=2, dash='dot'),
        hovertemplate="Année %{x}<br>Versé: CHF %{y:,.0f}<extra></extra>",
    ))

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=30, b=20, l=40, r=20), height=450,
        xaxis=dict(title="Années", showgrid=False, color='#A0A3B1'),
        yaxis=dict(title="Capital (CHF)", showgrid=True, gridcolor='rgba(255,255,255,0.05)',
                   color='#A0A3B1', tickformat=","),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                    font=dict(color='#A0A3B1')),
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

# Tab 4 : Coût d'opportunité 
with tab4:
    st.markdown("### Coût d'opportunité")
    st.markdown(
        """
        <div class="section-card">
            Le <b>coût d'opportunité</b> montre combien une dépense récurrente vous « coûte » réellement
            si cet argent avait été investi. C'est un outil puissant pour prendre conscience de l'impact
            à long terme de vos habitudes de dépenses.
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        depense = st.number_input("Dépense mensuelle (CHF)", 0, 10_000, 100, 10, key="dep_opp")
    with col2:
        taux_opp = st.slider("Rendement annuel (%)", 0.0, 12.0, 6.0, 0.5, key="taux_opp") / 100
    with col3:
        annees_opp = st.slider("Durée (années)", 5, 50, 20, 1, key="dur_opp")

    opp = cout_opportunite(depense, taux_opp, annees_opp)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-value">CHF {opp['total_depense']:,.0f}</div>
                <div class="kpi-label">Total dépensé sur {annees_opp} ans</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-value" style="background: #FF6B6B; -webkit-background-clip: text; -webkit-text-fill-color: transparent;">CHF {opp['valeur_si_investi']:,.0f}</div>
                <div class="kpi-label">Valeur si investi</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-value">{opp['facteur_multiplicateur']:.1f}x</div>
                <div class="kpi-label">Facteur multiplicateur</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Exemples concrets
    st.markdown("#### Exemples de dépenses courantes")

    exemples = [
        ("", "Café quotidien (Starbucks)", 5 * 22),
        ("", "Lunch au restaurant", 15 * 22),
        ("", "Abonnement streaming", 40),
        ("", "Paquet de cigarettes / jour", 9 * 30),
        ("", "Leasing vs occasion", 300),
        ("", "Shopping mode", 200),
    ]

    cols = st.columns(3)
    for i, (_, label, montant) in enumerate(exemples):
        with cols[i % 3]:
            opp_ex = cout_opportunite(montant, taux_opp, annees_opp)
            st.markdown(
                f"""
                <div class="section-card">
                    <b>{label}</b><br>
                    <span style="color: #A0A3B1;">CHF {montant:,.0f}/mois</span><br><br>
                    <span style="font-size: 0.85rem;">En {annees_opp} ans :</span><br>
                    <span style="color: #FF6B6B; font-weight: 700;">Dépensé : CHF {opp_ex['total_depense']:,.0f}</span><br>
                    <span style="color: #00D4AA; font-weight: 700;">Si investi : CHF {opp_ex['valeur_si_investi']:,.0f}</span><br>
                    <span style="font-weight: 700;">Gain manqué : CHF {opp_ex['gain_manque']:,.0f}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

# Sauvegarde 
inv_params = {
    "capital_initial": capital_initial, "versement_mensuel": versement_mensuel,
    "taux_annuel": taux_annuel, "annees": annees,
}
inv_results = {
    "capital_final": result["capital_final"], "total_interets": result["total_interets"],
    "total_verse": result["total_verse"], "rendement_pct": result["rendement_pct"],
}

simulation_save_section("investissements", inv_params, inv_results)

# Footer 
st.markdown(
    """
    <div class="footer-text">
        Finance Advisor · Module Investissements · Suisse Romande<br>
        Les performances passées ne sont pas indicatives des performances futures
    </div>
    """,
    unsafe_allow_html=True,
)
