"""
🏦 Finance Advisor — Suisse Romande
Dashboard Principal
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path

# ─── Configuration ───────────────────────────────────────────
st.set_page_config(
    page_title="Finance Advisor · Suisse Romande",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Charger le CSS
css_path = Path(__file__).parent / "assets" / "style.css"
if css_path.exists():
    st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)

# ─── Sidebar ─────────────────────────────────────────────────
with st.sidebar:
    st.markdown("# 🏦 Finance Advisor")
    st.markdown("**Suisse Romande**")
    st.markdown("---")

    st.markdown("### 👤 Votre Profil")
    nom = st.text_input("Nom", value="", placeholder="Votre nom")
    salaire = st.number_input(
        "Salaire annuel brut (CHF)",
        min_value=0,
        max_value=1_000_000,
        value=85_000,
        step=1_000,
        format="%d",
    )
    age = st.slider("Âge", 18, 70, 35)
    situation = st.selectbox("Situation", ["Célibataire", "Marié·e", "Divorcé·e"])
    enfants = st.number_input("Nombre d'enfants", 0, 10, 0)

    st.markdown("---")
    st.markdown(
        """
        <div class="footer-text">
        ⚠️ Application à titre indicatif<br>
        Ne remplace pas un conseil professionnel<br>
        Données basées sur les valeurs 2025
        </div>
        """,
        unsafe_allow_html=True,
    )

# ─── En-tête ─────────────────────────────────────────────────
greeting = f"Bienvenue, {nom}" if nom else "Bienvenue"

st.markdown(
    f"""
    <div class="animate-in">
        <div class="premium-title">{greeting} 👋</div>
        <div class="premium-subtitle">
            Votre tableau de bord financier personnel · Suisse Romande
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ─── KPIs Principaux ─────────────────────────────────────────
salaire_net_mois = round(salaire * 0.87 / 12)  # Estimation nette simplifiée
epargne_cible = round(salaire_net_mois * 0.20)
impot_estime = round(salaire * 0.14)  # Estimation moyenne

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-emoji">💼</div>
            <div class="kpi-value">CHF {salaire_net_mois:,}</div>
            <div class="kpi-label">Salaire net / mois (est.)</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-emoji">🎯</div>
            <div class="kpi-value">CHF {epargne_cible:,}</div>
            <div class="kpi-label">Objectif épargne / mois</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-emoji">🏛️</div>
            <div class="kpi-value">CHF {impot_estime:,}</div>
            <div class="kpi-label">Impôts estimés / an</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col4:
    annees_retraite = 65 - age
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-emoji">⏳</div>
            <div class="kpi-value">{annees_retraite} ans</div>
            <div class="kpi-label">Avant la retraite</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# ─── Aperçu de la répartition du budget ─────────────────────
col_left, col_right = st.columns([3, 2])

with col_left:
    st.markdown("### 📊 Répartition budgétaire estimée")

    categories = ["Logement", "Assurance maladie", "Alimentation", "Transport",
                   "Impôts", "Loisirs", "Épargne", "Autres"]
    pcts = [33, 7, 11, 8, 14, 6, 12, 9]
    montants = [round(salaire_net_mois * p / 100) for p in pcts]
    colors = ["#6C63FF", "#3B82F6", "#00D4AA", "#34E8C3",
              "#FFB347", "#FF6B6B", "#8B83FF", "#A0A3B1"]

    fig = go.Figure(data=[go.Pie(
        labels=categories,
        values=montants,
        hole=0.55,
        marker=dict(colors=colors, line=dict(color='#0E1117', width=2)),
        textinfo='label+percent',
        textfont=dict(size=12, color='white', family='Inter'),
        hovertemplate="<b>%{label}</b><br>CHF %{value:,}<br>%{percent}<extra></extra>",
    )])

    fig.update_layout(
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=20, b=20, l=20, r=20),
        height=380,
        annotations=[
            dict(
                text=f"<b>CHF {salaire_net_mois:,}</b><br><span style='font-size:12px;color:#A0A3B1'>/ mois</span>",
                x=0.5, y=0.5,
                font=dict(size=20, color='white', family='Outfit'),
                showarrow=False,
            )
        ],
    )

    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

with col_right:
    st.markdown("### 🎯 Indicateurs clés")

    # Taux d'épargne visuel
    taux_epargne = 20
    st.markdown(f"**Taux d'épargne recommandé : {taux_epargne}%**")
    color_class = "success" if taux_epargne >= 15 else "danger"
    st.markdown(
        f"""
        <div class="progress-container">
            <div class="progress-bar {color_class}" style="width: {min(taux_epargne, 100)}%"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # Aperçu des modules
    modules = [
        ("💰", "Budget", "Gérez vos revenus et dépenses"),
        ("🏛️", "Fiscalité", "Simulez vos impôts par canton"),
        ("🔒", "Prévoyance", "Planifiez votre retraite (3 piliers)"),
        ("📈", "Investissements", "Simulez vos placements"),
    ]

    for emoji, titre, desc in modules:
        st.markdown(
            f"""
            <div class="section-card">
                <b>{emoji} {titre}</b><br>
                <span style="color: #A0A3B1; font-size: 0.9rem;">{desc}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ─── Taux d'épargne / Santé financière ──────────────────────
st.markdown("---")
st.markdown("### 💡 Conseils rapides")

col_a, col_b, col_c = st.columns(3)

with col_a:
    st.markdown(
        """
        <div class="suggestion-haute">
            <b>💰 3ème Pilier</b><br>
            <span style="color: #A0A3B1;">Versez CHF 7'056/an pour maximiser votre déduction fiscale et préparer votre retraite.</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col_b:
    st.markdown(
        """
        <div class="suggestion-moyenne">
            <b>🏦 Fonds d'urgence</b><br>
            <span style="color: #A0A3B1;">Constituez un matelas de 3 à 6 mois de dépenses pour faire face aux imprévus.</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col_c:
    st.markdown(
        """
        <div class="suggestion-info">
            <b>📊 Diversification</b><br>
            <span style="color: #A0A3B1;">Ne mettez pas tous vos œufs dans le même panier. Diversifiez entre actions, obligations et immobilier.</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ─── Footer ──────────────────────────────────────────────────
st.markdown(
    """
    <div class="footer-text">
        Finance Advisor · Suisse Romande · 2025<br>
        Application à titre indicatif uniquement · Ne remplace pas un conseil fiscal ou financier professionnel
    </div>
    """,
    unsafe_allow_html=True,
)
