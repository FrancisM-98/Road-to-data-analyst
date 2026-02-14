"""
🏦 Finance Advisor Pro — Dashboard Principal
Version B2B pour conseillers financiers
"""

import streamlit as st
import plotly.graph_objects as go
from pathlib import Path

# ─── Configuration ───────────────────────────────────────────
st.set_page_config(
    page_title="Finance Advisor Pro",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# CSS
css_path = Path(__file__).parent / "assets" / "style.css"
if css_path.exists():
    st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)

# ─── Auth Guard ──────────────────────────────────────────────
from utils.auth import require_auth, sidebar_user_info, get_current_user, client_banner, init_session
from utils.database import init_db, get_client_count

init_session()
init_db()

# Login page (bloque l'exécution si non authentifié)
from utils.auth import login_page, is_authenticated
if not is_authenticated():
    login_page()
    st.stop()

# ─── Sidebar ─────────────────────────────────────────────────
user = get_current_user()
advisor_id = user["username"]

with st.sidebar:
    # Logo / Nom du cabinet
    cabinet_name = user.get("cabinet", "") or "Finance Advisor Pro"
    st.markdown(f"# 🏦 {cabinet_name}")
    st.markdown("**Suisse Romande**")
    st.markdown("---")

    # Client actif
    current_client = st.session_state.get("current_client")
    if current_client:
        nom_complet = f"{current_client.get('prenom', '')} {current_client.get('nom', '')}".strip()
        st.markdown(f"### 👤 Client actif")
        st.markdown(f"**{nom_complet}**")
        st.markdown(f"_{current_client.get('canton', '')} · CHF {current_client.get('salaire_annuel', 0):,.0f}/an_")

        if st.button("✖ Désélectionner", key="sidebar_deselect", use_container_width=True):
            st.session_state.current_client = None
            st.rerun()
    else:
        st.markdown("### 👤 Aucun client")
        st.info("Rendez-vous dans **👥 Clients** pour sélectionner un client.")

    sidebar_user_info()


# ─── Header ──────────────────────────────────────────────────
greeting = f"Bonjour {user['name'].split()[0]}"

st.markdown(
    f"""
    <div class="premium-header">
        <div class="premium-title">{greeting} 👋</div>
        <div class="premium-subtitle">
            Votre tableau de bord conseiller · {cabinet_name}
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ─── Bandeau client actif ────────────────────────────────────
client_banner()

# ─── KPIs du cabinet ─────────────────────────────────────────
stats = get_client_count(advisor_id)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-emoji">👥</div>
            <div class="kpi-value">{stats['total']}</div>
            <div class="kpi-label">Clients total</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-emoji">🟡</div>
            <div class="kpi-value">{stats['prospects']}</div>
            <div class="kpi-label">Prospects</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-emoji">🟢</div>
            <div class="kpi-value">{stats['actifs']}</div>
            <div class="kpi-label">Clients actifs</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col4:
    # Conversion rate
    taux_conv = round(stats['actifs'] / stats['total'] * 100) if stats['total'] > 0 else 0
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-emoji">📈</div>
            <div class="kpi-value">{taux_conv}%</div>
            <div class="kpi-label">Taux de conversion</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# ─── Aperçu du client sélectionné ou vue d'ensemble ─────────
if current_client:
    st.markdown("### 📊 Aperçu du client")

    nom_complet = f"{current_client.get('prenom', '')} {current_client.get('nom', '')}".strip()
    salaire = current_client.get("salaire_annuel", 0)
    age = current_client.get("age", 30)
    canton = current_client.get("canton", "")
    capital_lpp = current_client.get("capital_lpp", 0)
    capital_3a = current_client.get("capital_3a", 0)

    col_left, col_right = st.columns([3, 2])

    with col_left:
        # Mini-profil financier
        salaire_net_mois = round(salaire * 0.87 / 12)
        impot_estime = round(salaire * 0.12)
        annees_retraite = max(0, 65 - age)
        patrimoine_prevoyance = capital_lpp + capital_3a

        sub_cols = st.columns(4)
        kpis = [
            ("💰", f"CHF {salaire_net_mois:,}", "Salaire net / mois"),
            ("🏛️", f"CHF {impot_estime:,}", "Impôts estimés / an"),
            ("🏦", f"CHF {patrimoine_prevoyance:,}", "Patrimoine prévoyance"),
            ("⏳", f"{annees_retraite} ans", "Jusqu'à la retraite"),
        ]
        for sub_col, (emoji, value, label) in zip(sub_cols, kpis):
            with sub_col:
                st.markdown(
                    f"""
                    <div class="kpi-card">
                        <div class="kpi-emoji">{emoji}</div>
                        <div class="kpi-value">{value}</div>
                        <div class="kpi-label">{label}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    with col_right:
        # Estimation rapide de la répartition
        st.markdown("### 🎯 Répartition budgétaire estimée")

        categories = ["Logement", "Assurance maladie", "Alimentation", "Transport",
                       "Impôts", "Loisirs", "Épargne", "Autres"]
        proportions = [0.33, 0.07, 0.11, 0.08, 0.12, 0.06, 0.12, 0.11]
        valeurs = [round(salaire_net_mois * p) for p in proportions]

        fig = go.Figure(data=[go.Pie(
            labels=categories,
            values=valeurs,
            hole=0.55,
            marker=dict(
                colors=["#6C63FF", "#3B82F6", "#00D4AA", "#FFB347",
                         "#FF6B6B", "#A78BFA", "#34D399", "#94A3B8"],
                line=dict(color='rgba(0,0,0,0.3)', width=2),
            ),
            textinfo='label+percent',
            textfont=dict(size=10, color='white', family='Inter'),
            hovertemplate="<b>%{label}</b><br>CHF %{value:,}<br>%{percent}<extra></extra>",
        )])

        fig.update_layout(
            showlegend=False,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(t=10, b=10, l=10, r=10),
            height=300,
            annotations=[
                dict(
                    text=f"CHF<br>{salaire_net_mois:,}",
                    x=0.5, y=0.5,
                    font=dict(size=16, color='white', family='Outfit'),
                    showarrow=False,
                )
            ],
        )

        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

else:
    st.markdown("### 🚀 Actions rapides")
    col_a, col_b, col_c = st.columns(3)

    with col_a:
        st.markdown(
            """
            <div class="suggestion-haute">
                <b>👥 Gérer vos clients</b><br>
                <span style="color: #A0A3B1;">
                    Ajoutez vos premiers clients ou chargez un cas type pour démarrer une simulation.
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_b:
        st.markdown(
            """
            <div class="suggestion-moyenne">
                <b>📋 Cas types</b><br>
                <span style="color: #A0A3B1;">
                    5 profils pré-configurés (jeune diplômé, famille, cadre, retraite, indépendant) pour vos démos.
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_c:
        st.markdown(
            """
            <div class="suggestion-haute">
                <b>🔄 Workflow type</b><br>
                <span style="color: #A0A3B1;">
                    Client → Budget → Fiscalité → Prévoyance → Investissement → Rapport PDF
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ─── Modules disponibles ────────────────────────────────────
st.markdown("---")
st.markdown("### 📚 Modules de simulation")

col_m1, col_m2, col_m3, col_m4 = st.columns(4)

modules = [
    (col_m1, "💰", "Budget", "Revenus, charges fixes et variables, comparaison CH"),
    (col_m2, "🏛️", "Fiscalité", "Impôts cantonaux, déductions, optimisation"),
    (col_m3, "🔒", "Prévoyance", "AVS, LPP, 3ème pilier, gap retraite"),
    (col_m4, "📈", "Investissements", "Intérêts composés, Monte Carlo, profils de risque"),
]

for col, emoji, name, desc in modules:
    with col:
        st.markdown(
            f"""
            <div class="kpi-card" style="cursor: pointer;">
                <div class="kpi-emoji">{emoji}</div>
                <div class="kpi-value" style="font-size: 1.2rem;">{name}</div>
                <div class="kpi-label" style="font-size: 0.8rem;">{desc}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ─── Footer ──────────────────────────────────────────────────
st.markdown(
    """
    <div class="footer-text">
        Finance Advisor Pro · Suisse Romande · 2025<br>
        Application à titre indicatif uniquement · Ne remplace pas un conseil fiscal ou financier professionnel
    </div>
    """,
    unsafe_allow_html=True,
)
