"""
Composant réutilisable pour la sauvegarde et le chargement des simulations.
Fournit un panneau save/load/history intégrable dans chaque page de simulation.
Intègre aussi l'export PDF et l'envoi par email.
"""

import streamlit as st
from datetime import datetime
from utils.database import save_simulation, get_simulations, delete_simulation
from utils.auth import get_current_user
from utils.pdf_export import (
    export_budget_pdf,
    export_fiscalite_pdf,
    export_prevoyance_pdf,
    export_investissements_pdf,
)
from utils.email_sender import email_send_section

# Map module name → export function
_EXPORT_MAP = {
    "budget": ("Budget", export_budget_pdf),
    "fiscalite": ("Fiscalité", export_fiscalite_pdf),
    "prevoyance": ("Prévoyance", export_prevoyance_pdf),
    "investissements": ("Investissements", export_investissements_pdf),
}


def simulation_save_section(module: str, parametres: dict, resultats: dict):
    """
    Affiche la section de sauvegarde, historique, export PDF et email.
    
    Args:
        module: Nom du module (budget, fiscalite, prevoyance, investissements)
        parametres: Dict des paramètres de la simulation courante
        resultats: Dict des résultats de la simulation courante
    """
    client = st.session_state.get("current_client")
    user = get_current_user()

    if not client or not user:
        return

    client_id = client["id"]
    advisor_id = user["username"]
    advisor_name = user.get("name", advisor_id)
    nom_client = f"{client.get('prenom', '')} {client.get('nom', '')}".strip()

    st.markdown("---")
    st.markdown("### Sauvegarder & Exporter")

    # Save + PDF row 
    col_name, col_save, col_pdf = st.columns([3, 1, 1])
    with col_name:
        default_name = f"{module.capitalize()} — {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        sim_name = st.text_input(
            "Nom de la simulation",
            value=default_name,
            key=f"sim_name_{module}",
            label_visibility="collapsed",
            placeholder="Nom de la simulation...",
        )
    with col_save:
        if st.button(" Sauvegarder", key=f"save_sim_{module}", use_container_width=True):
            sim_id = save_simulation(
                client_id=client_id,
                advisor_id=advisor_id,
                module=module,
                nom=sim_name,
                parametres=parametres,
                resultats=resultats,
            )
            st.success(f" Simulation sauvegardée (v{_get_latest_version(client_id, module)})")
            st.rerun()

    # PDF Export 
    with col_pdf:
        module_label, export_fn = _EXPORT_MAP.get(module, ("Rapport", None))
        if export_fn:
            pdf_bytes = export_fn(
                advisor_name=advisor_name,
                client_name=nom_client,
                params=parametres,
                results=resultats,
            )
            filename = f"Rapport_{module_label}_{nom_client}_{datetime.now().strftime('%Y%m%d')}.pdf"
            filename = filename.replace(" ", "_")
            st.download_button(
                label=" PDF",
                data=bytes(pdf_bytes),
                file_name=filename,
                mime="application/pdf",
                key=f"pdf_{module}",
                use_container_width=True,
            )

    # Email section 
    if export_fn:
        pdf_bytes = export_fn(
            advisor_name=advisor_name,
            client_name=nom_client,
            params=parametres,
            results=resultats,
        )
        email_send_section(module_label, pdf_bytes, client, advisor_name)

    # History section 
    simulations = get_simulations(client_id, module=module)

    if simulations:
        with st.expander(f" Historique ({len(simulations)} version{'s' if len(simulations) > 1 else ''})", expanded=False):
            for sim in simulations:
                _render_simulation_card(sim, module)
    else:
        st.caption("Aucune simulation sauvegardée pour ce module.")


def _get_latest_version(client_id: str, module: str) -> int:
    """Retourne le numéro de la dernière version."""
    sims = get_simulations(client_id, module=module)
    if sims:
        return max(s.get("version", 1) for s in sims)
    return 1


def _render_simulation_card(sim: dict, module: str):
    """Affiche une carte de simulation dans l'historique."""
    created = sim.get("created_at", "")
    try:
        date_str = datetime.fromisoformat(created).strftime("%d/%m/%Y à %H:%M")
    except (ValueError, TypeError):
        date_str = created

    version = sim.get("version", "?")
    nom = sim.get("nom", "Sans nom")

    col_info, col_load, col_delete = st.columns([4, 1, 1])

    with col_info:
        st.markdown(
            f"""
            <div style="
                background: rgba(108, 99, 255, 0.08);
                border: 1px solid rgba(108, 99, 255, 0.2);
                border-radius: 10px;
                padding: 0.6rem 1rem;
                margin-bottom: 0.3rem;
            ">
                <b>v{version}</b> — {nom}<br>
                <span style="color: var(--text-secondary, #A0A3B1); font-size: 0.8rem;">{date_str}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_load:
        if st.button(" Charger", key=f"load_{sim['id']}", use_container_width=True):
            _load_simulation(sim, module)

    with col_delete:
        if st.button("", key=f"del_{sim['id']}", use_container_width=True):
            delete_simulation(sim["id"])
            st.success("Simulation supprimée.")
            st.rerun()


def _load_simulation(sim: dict, module: str):
    """Charge les paramètres d'une simulation dans session_state et relance la page."""
    params = sim.get("parametres", {})

    # Stocker les paramètres dans session_state pour que la page les récupère
    st.session_state[f"loaded_sim_{module}"] = params
    st.session_state[f"loaded_sim_name_{module}"] = sim.get("nom", "")
    st.session_state[f"loaded_sim_version_{module}"] = sim.get("version", "?")

    st.info(f" Simulation **v{sim.get('version', '?')}** chargée — les paramètres sont restaurés.")
    st.rerun()


def get_loaded_params(module: str) -> dict | None:
    """
    Récupère les paramètres d'une simulation chargée, s'il y en a une.
    À appeler au début de la page pour pré-remplir les inputs.
    Retourne None si aucune simulation n'est chargée.
    """
    key = f"loaded_sim_{module}"
    if key in st.session_state:
        params = st.session_state[key]
        # Afficher un bandeau informatif
        version = st.session_state.get(f"loaded_sim_version_{module}", "?")
        name = st.session_state.get(f"loaded_sim_name_{module}", "")
        st.markdown(
            f"""
            <div style="
                background: rgba(0, 212, 170, 0.1);
                border: 1px solid rgba(0, 212, 170, 0.3);
                border-radius: 10px;
                padding: 0.5rem 1rem;
                margin-bottom: 1rem;
                font-size: 0.9rem;
                color: #00D4AA;
            ">
                Simulation chargée : <b>v{version}</b> — {name}
            </div>
            """,
            unsafe_allow_html=True,
        )
        # Nettoyer pour ne pas reboucler
        del st.session_state[key]
        if f"loaded_sim_name_{module}" in st.session_state:
            del st.session_state[f"loaded_sim_name_{module}"]
        if f"loaded_sim_version_{module}" in st.session_state:
            del st.session_state[f"loaded_sim_version_{module}"]
        return params
    return None
