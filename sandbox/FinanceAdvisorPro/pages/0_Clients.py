"""
Module Clients — Gestion du portefeuille clients
"""

import streamlit as st
from pathlib import Path
from datetime import datetime

# CSS
css_path = Path(__file__).parent.parent / "assets" / "style.css"
if css_path.exists():
    st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)

from utils.auth import require_auth, sidebar_user_info, get_current_user
from utils.database import (
    init_db, create_client, get_clients, get_client,
    update_client, delete_client, get_client_count,
)
from utils.case_templates import get_templates_summary, get_template

# Auth Guard 
require_auth()
sidebar_user_info()
init_db()

user = get_current_user()
advisor_id = user["username"]

# Header 
st.markdown(
    """
    <div class="premium-header">
        <div class="premium-title"> Portefeuille Clients</div>
        <div class="premium-subtitle">
            Gérez vos prospects et clients · Chargez un profil pour simuler
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# KPI Cards 
stats = get_client_count(advisor_id)

col1, col2, col3, col4 = st.columns(4)
for col, label_stat, value, label in [
    (col1, "", stats["total"], "Total clients"),
    (col2, "", stats["prospects"], "Prospects"),
    (col3, "", stats["actifs"], "Actifs"),
    (col4, "", stats["inactifs"], "Inactifs"),
]:
    with col:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-value">{value}</div>
                <div class="kpi-label">{label}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown("<br>", unsafe_allow_html=True)

# Toolbar : Recherche + Actions 
col_search, col_filter, col_add, col_case = st.columns([3, 1.5, 1.5, 1.5])

with col_search:
    search_query = st.text_input(" Rechercher", placeholder="Nom, prénom ou email…", label_visibility="collapsed")

with col_filter:
    filtre_statut = st.selectbox("Filtre", ["Tous", "Prospect", "Actif", "Inactif"], label_visibility="collapsed")

with col_add:
    add_clicked = st.button(" Nouveau client", use_container_width=True)

with col_case:
    case_clicked = st.button(" Cas type", use_container_width=True)


# Dialog : Nouveau client 
@st.dialog(" Nouveau client", width="large")
def new_client_dialog():
    """Formulaire de création d'un client."""
    col_a, col_b = st.columns(2)
    with col_a:
        prenom = st.text_input("Prénom *", key="nc_prenom")
        email = st.text_input("Email", key="nc_email")
        age = st.number_input("Âge", 18, 80, 35, key="nc_age")
        enfants = st.number_input("Nombre d'enfants", 0, 10, 0, key="nc_enfants")
        canton = st.selectbox("Canton", [
            "Vaud (VD)", "Genève (GE)", "Valais (VS)", "Fribourg (FR)",
            "Neuchâtel (NE)", "Jura (JU)", "Berne (BE) — partie francophone"
        ], key="nc_canton")
    with col_b:
        nom = st.text_input("Nom *", key="nc_nom")
        telephone = st.text_input("Téléphone", key="nc_tel")
        situation = st.selectbox("Situation familiale", [
            "Célibataire", "Marié·e", "Divorcé·e", "Veuf·ve"
        ], key="nc_situation")
        salaire = st.number_input("Salaire annuel brut (CHF)", 0, 500_000, 80_000, 1_000, key="nc_salaire")
        statut = st.selectbox("Statut", ["prospect", "actif", "inactif"], key="nc_statut")
    
    col_lpp, col_3a = st.columns(2)
    with col_lpp:
        capital_lpp = st.number_input("Capital LPP actuel (CHF)", 0, 2_000_000, 0, 5_000, key="nc_lpp")
    with col_3a:
        capital_3a = st.number_input("Capital 3a actuel (CHF)", 0, 500_000, 0, 1_000, key="nc_3a")

    notes = st.text_area("Notes", key="nc_notes", placeholder="Informations complémentaires…")

    if st.button(" Créer le client", use_container_width=True, type="primary"):
        if not prenom or not nom:
            st.error("Le prénom et le nom sont obligatoires.")
        else:
            create_client(
                advisor_id=advisor_id,
                prenom=prenom, nom=nom, email=email, telephone=telephone,
                age=age, situation_familiale=situation, enfants=enfants,
                canton=canton, salaire_annuel=salaire,
                capital_lpp=capital_lpp, capital_3a=capital_3a,
                statut=statut, notes=notes,
            )
            st.success(f" {prenom} {nom} ajouté !")
            st.rerun()


# Dialog : Cas types 
@st.dialog(" Charger un cas type", width="large")
def case_type_dialog():
    """Affiche les cas types et permet de les charger."""
    templates = get_templates_summary()
    for tpl in templates:
        with st.container():
            col_info, col_action = st.columns([4, 1])
            with col_info:
                st.markdown(
                    f"""
                    <div style="
                        background: rgba(255,255,255,0.04);
                        border: 1px solid rgba(255,255,255,0.08);
                        border-radius: 12px;
                        padding: 1rem;
                        margin-bottom: 0.5rem;
                    ">
                        <b style="font-size: 1.05rem; margin-left: 0.5rem;">{tpl['titre']}</b>
                        <br>
                        <span style="color: #A0A3B1; font-size: 0.85rem;">{tpl['description']}</span>
                        <br>
                        <span style="color: #6C63FF; font-size: 0.8rem;">
                            {tpl['age']} ans · {tpl['situation']} · {tpl['canton']} · CHF {tpl['salaire']:,}/an
                        </span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with col_action:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Charger", key=f"load_{tpl['key']}", use_container_width=True):
                    template_data = get_template(tpl["key"])
                    profil = template_data["profil"]

                    # Créer comme client temporaire dans la session
                    temp_client = {
                        "id": f"temp_{tpl['key']}",
                        "nom": profil["nom"],
                        "prenom": profil["prenom"],
                        "age": profil["age"],
                        "situation_familiale": profil["situation_familiale"],
                        "enfants": profil["enfants"],
                        "canton": profil["canton"],
                        "commune": profil.get("commune", ""),
                        "salaire_annuel": profil["salaire_annuel"],
                        "capital_lpp": profil["capital_lpp"],
                        "capital_3a": profil["capital_3a"],
                        "statut": "cas_type",
                        "email": "",
                        "telephone": "",
                        "notes": f"Cas type : {tpl['titre']}",
                        "_template_key": tpl["key"],
                        "_budget": template_data.get("budget", {}),
                        "_recommandations": template_data.get("recommandations", []),
                    }
                    st.session_state.current_client = temp_client
                    st.success(f" Cas type « {tpl['titre']} » chargé !")
                    st.rerun()


# Trigger dialogs
if add_clicked:
    new_client_dialog()
if case_clicked:
    case_type_dialog()


# Client actif 
current = st.session_state.get("current_client")
if current:
    nom_complet = f"{current.get('prenom', '')} {current.get('nom', '')}".strip()
    statut_txt = current.get("statut", "prospect")
    is_temp = str(current.get("id", "")).startswith("temp_")

    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, rgba(0, 212, 170, 0.12), rgba(108, 99, 255, 0.08));
            border: 1px solid rgba(0, 212, 170, 0.3);
            border-radius: 14px;
            padding: 1rem 1.5rem;
            margin-bottom: 1.5rem;
        ">
            <span style="font-size: 0.8rem; color: #00D4AA; font-weight: 600; letter-spacing: 0.05em;">
                CLIENT ACTIF {"(CAS TYPE)" if is_temp else ""}
            </span><br>
            <span style="font-size: 1.3rem; font-weight: 700;"> {nom_complet}</span>
            <span style="margin-left: 1rem; color: #A0A3B1;">
                {current.get('canton', '')} · CHF {current.get('salaire_annuel', 0):,.0f}/an
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Afficher les recommandations si cas type
    recs = current.get("_recommandations", [])
    if recs:
        with st.expander(" Recommandations pour ce profil", expanded=False):
            for rec in recs:
                st.markdown(f"- {rec}")

    col_deselect, col_save = st.columns([1, 1])
    with col_deselect:
        if st.button(" Désélectionner", use_container_width=True):
            st.session_state.current_client = None
            st.rerun()
    with col_save:
        if is_temp:
            if st.button(" Sauvegarder en client", use_container_width=True, type="primary"):
                profil = {k: v for k, v in current.items() if not k.startswith("_") and k != "id"}
                client_id = create_client(advisor_id=advisor_id, **profil)
                saved = get_client(client_id)
                st.session_state.current_client = saved
                st.success(" Client sauvegardé !")
                st.rerun()


# Liste des clients 
st.markdown("---")
st.markdown("### Vos clients")

clients = get_clients(advisor_id, statut=filtre_statut, search=search_query if search_query else None)

if not clients:
    st.markdown(
        """
        <div style="
            text-align: center;
            padding: 3rem;
            color: #A0A3B1;
        ">
            <b>Aucun client trouvé</b><br>
            Ajoutez votre premier client ou chargez un cas type pour commencer.
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    for client in clients:
        nom_complet = f"{client['prenom']} {client['nom']}"
        statut = client.get("statut", "prospect").capitalize()
        
        is_selected = (
            st.session_state.get("current_client", {}) or {}
        ).get("id") == client["id"]

        border_color = "rgba(0, 212, 170, 0.5)" if is_selected else "rgba(255,255,255,0.06)"
        bg = "rgba(0, 212, 170, 0.06)" if is_selected else "rgba(255,255,255,0.03)"

        col_info, col_details, col_actions = st.columns([3, 3, 2])

        with col_info:
            st.markdown(
                f"""
                <div style="
                    background: {bg};
                    border-left: 3px solid {border_color};
                    border-radius: 8px;
                    padding: 0.8rem 1rem;
                ">
                    <span style="font-weight: 700; font-size: 1rem;">{nom_complet}</span>
                    <span style="margin-left: 0.5rem;">{statut}</span>
                    <br>
                    <span style="color: #A0A3B1; font-size: 0.82rem;">
                        {client.get('canton', '')} · CHF {client.get('salaire_annuel', 0):,.0f}/an · {client.get('age', '?')} ans
                    </span>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col_details:
            st.markdown(
                f"""
                <div style="padding: 0.8rem 0; color: #A0A3B1; font-size: 0.82rem;">
                    {client.get('email', '-') or '-'}<br>
                    {client.get('telephone', '-') or '-'}
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col_actions:
            btn_col1, btn_col2, btn_col3 = st.columns(3)
            with btn_col1:
                # "Sélectionner" en primary pour l'action principale
                if st.button("Sélectionner", key=f"sel_{client['id']}", help="Sélectionner ce client", type="primary"):
                    st.session_state.current_client = client
                    st.rerun()
            with btn_col2:
                if st.button("Éditer", key=f"edit_{client['id']}", help="Modifier"):
                    st.session_state[f"editing_{client['id']}"] = True
                    st.rerun()
            with btn_col3:
                if st.button("Suppr.", key=f"del_{client['id']}", help="Supprimer"):
                    st.session_state[f"confirm_del_{client['id']}"] = True
                    st.rerun()

        # Confirmation de suppression
        if st.session_state.get(f"confirm_del_{client['id']}"):
            st.warning(f" Supprimer **{nom_complet}** et toutes ses simulations ?")
            col_yes, col_no = st.columns(2)
            with col_yes:
                if st.button("Oui, supprimer", key=f"yes_del_{client['id']}", type="primary"):
                    delete_client(client["id"])
                    if (st.session_state.get("current_client") or {}).get("id") == client["id"]:
                        st.session_state.current_client = None
                    del st.session_state[f"confirm_del_{client['id']}"]
                    st.rerun()
            with col_no:
                if st.button("Annuler", key=f"no_del_{client['id']}"):
                    del st.session_state[f"confirm_del_{client['id']}"]
                    st.rerun()

        # Dialog d'édition
        if st.session_state.get(f"editing_{client['id']}"):
            with st.expander(f" Modifier {nom_complet}", expanded=True):
                col_ea, col_eb = st.columns(2)
                with col_ea:
                    e_prenom = st.text_input("Prénom", client["prenom"], key=f"ep_{client['id']}")
                    e_email = st.text_input("Email", client.get("email", ""), key=f"ee_{client['id']}")
                    e_age = st.number_input("Âge", 18, 80, client.get("age", 30), key=f"ea_{client['id']}")
                    e_enfants = st.number_input("Enfants", 0, 10, client.get("enfants", 0), key=f"en_{client['id']}")
                with col_eb:
                    e_nom = st.text_input("Nom", client["nom"], key=f"eno_{client['id']}")
                    e_tel = st.text_input("Téléphone", client.get("telephone", ""), key=f"et_{client['id']}")
                    e_situation = st.selectbox("Situation", [
                        "Célibataire", "Marié·e", "Divorcé·e", "Veuf·ve"
                    ], index=["Célibataire", "Marié·e", "Divorcé·e", "Veuf·ve"].index(
                        client.get("situation_familiale", "Célibataire")
                    ) if client.get("situation_familiale") in ["Célibataire", "Marié·e", "Divorcé·e", "Veuf·ve"] else 0,
                    key=f"es_{client['id']}")
                    e_salaire = st.number_input("Salaire annuel", 0, 500_000,
                                                int(client.get("salaire_annuel", 0)), 1000, key=f"esal_{client['id']}")

                    e_statut = st.selectbox("Statut", ["prospect", "actif", "inactif"],
                                            index=["prospect", "actif", "inactif"].index(client.get("statut", "prospect")),
                                            key=f"est_{client['id']}")
                e_notes = st.text_area("Notes", client.get("notes", ""), key=f"enot_{client['id']}")

                col_save, col_cancel = st.columns(2)
                with col_save:
                    if st.button(" Sauvegarder", key=f"save_{client['id']}", type="primary", use_container_width=True):
                        update_client(
                            client["id"],
                            prenom=e_prenom, nom=e_nom, email=e_email, telephone=e_tel,
                            age=e_age, situation_familiale=e_situation, enfants=e_enfants,
                            salaire_annuel=e_salaire, statut=e_statut, notes=e_notes,
                        )
                        # Mettre à jour le client actif s'il est sélectionné
                        if (st.session_state.get("current_client") or {}).get("id") == client["id"]:
                            st.session_state.current_client = get_client(client["id"])
                        del st.session_state[f"editing_{client['id']}"]
                        st.rerun()
                with col_cancel:
                    if st.button("Annuler", key=f"cancelEdit_{client['id']}", use_container_width=True):
                        del st.session_state[f"editing_{client['id']}"]
                        st.rerun()

                st.markdown("<div style='margin-bottom: 0.3rem;'></div>", unsafe_allow_html=True)


# Footer 
st.markdown(
    """
    <div class="footer-text">
        Finance Advisor Pro · Gestion Clients · Suisse Romande
    </div>
    """,
    unsafe_allow_html=True,
)
