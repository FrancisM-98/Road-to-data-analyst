"""
Module d'authentification pour Finance Advisor Pro.
Gestion des sessions, login/logout, et rôles.
"""

import streamlit as st
import yaml
import hashlib
import uuid
from pathlib import Path
from datetime import datetime

# Chemin vers le fichier de credentials
CREDENTIALS_FILE = Path(__file__).parent.parent / "data" / "credentials.yaml"


def _ensure_credentials_file():
    """Crée le fichier de credentials par défaut s'il n'existe pas."""
    CREDENTIALS_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not CREDENTIALS_FILE.exists():
        default_credentials = {
            "users": {
                "demo": {
                    "name": "Conseiller Démo",
                    "email": "demo@financeadvisor.ch",
                    "password": _hash_password("demo123"),
                    "role": "conseiller",
                    "cabinet": "Cabinet Démo",
                    "created_at": datetime.now().isoformat(),
                }
            }
        }
        with open(CREDENTIALS_FILE, "w", encoding="utf-8") as f:
            yaml.dump(default_credentials, f, allow_unicode=True, default_flow_style=False)


def _hash_password(password: str) -> str:
    """Hash un mot de passe avec SHA-256 (MVP — bcrypt pour la prod)."""
    return hashlib.sha256(password.encode()).hexdigest()


def _load_credentials() -> dict:
    """Charge les credentials depuis le fichier YAML."""
    _ensure_credentials_file()
    with open(CREDENTIALS_FILE, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _save_credentials(credentials: dict):
    """Sauvegarde les credentials dans le fichier YAML."""
    with open(CREDENTIALS_FILE, "w", encoding="utf-8") as f:
        yaml.dump(credentials, f, allow_unicode=True, default_flow_style=False)


def authenticate(username: str, password: str) -> dict | None:
    """
    Authentifie un utilisateur.
    Retourne les infos user si succès, None sinon.
    """
    credentials = _load_credentials()
    users = credentials.get("users", {})

    if username in users:
        user = users[username]
        if user["password"] == _hash_password(password):
            return {
                "username": username,
                "name": user["name"],
                "email": user.get("email", ""),
                "role": user.get("role", "conseiller"),
                "cabinet": user.get("cabinet", ""),
            }
    return None


def register_user(
    username: str,
    password: str,
    name: str,
    email: str = "",
    cabinet: str = "",
    role: str = "conseiller",
) -> bool:
    """Enregistre un nouvel utilisateur. Retourne True si succès."""
    credentials = _load_credentials()
    users = credentials.get("users", {})

    if username in users:
        return False  # Username déjà pris

    users[username] = {
        "name": name,
        "email": email,
        "password": _hash_password(password),
        "role": role,
        "cabinet": cabinet,
        "created_at": datetime.now().isoformat(),
    }
    credentials["users"] = users
    _save_credentials(credentials)
    return True


def init_session():
    """Initialise les variables de session d'authentification.
    Restaure la session depuis query_params si disponible (persistance via localStorage).
    """
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "user" not in st.session_state:
        st.session_state.user = None
    if "current_client" not in st.session_state:
        st.session_state.current_client = None

    # Restaurer le thème depuis query_params (injecté par JS/localStorage) is removed — dark mode only for MVP

    # Restaurer la session depuis query_params (injecté par JS/localStorage)
    if not st.session_state.authenticated:
        qp_user = st.query_params.get("auth_user", "")
        qp_token = st.query_params.get("auth_token", "")
        if qp_user and qp_token:
            # Vérifier que le token correspond au user dans credentials
            credentials = _load_credentials()
            users = credentials.get("users", {})
            if qp_user in users:
                expected_token = hashlib.sha256(f"{qp_user}:{users[qp_user]['password']}".encode()).hexdigest()[:16]
                if qp_token == expected_token:
                    user_data = users[qp_user]
                    st.session_state.authenticated = True
                    st.session_state.user = {
                        "username": qp_user,
                        "name": user_data["name"],
                        "email": user_data.get("email", ""),
                        "role": user_data.get("role", "conseiller"),
                        "cabinet": user_data.get("cabinet", ""),
                    }


def _generate_auth_token(username: str) -> str:
    """Génère un token d'authentification pour la persistance localStorage."""
    credentials = _load_credentials()
    users = credentials.get("users", {})
    if username in users:
        return hashlib.sha256(f"{username}:{users[username]['password']}".encode()).hexdigest()[:16]
    return ""


def is_authenticated() -> bool:
    """Vérifie si l'utilisateur est authentifié."""
    return st.session_state.get("authenticated", False)


def get_current_user() -> dict | None:
    """Retourne l'utilisateur courant."""
    return st.session_state.get("user", None)


def logout():
    """Déconnecte l'utilisateur et signale la suppression du localStorage."""
    st.session_state.authenticated = False
    st.session_state.user = None
    st.session_state.current_client = None
    st.session_state._logout_triggered = True
    # Nettoyer les query_params
    for key in ["auth_user", "auth_token"]:
        if key in st.query_params:
            del st.query_params[key]


def login_page():
    """
    Affiche la page de login.
    Retourne True si l'utilisateur est authentifié.
    """
    import streamlit.components.v1 as components

    init_session()

    if is_authenticated():
        return True

    # ── Inject JS: restore auth from localStorage into query_params ──
    components.html(
        """
        <script>
        (function() {
            // Restore auth from localStorage into URL query_params
            const authUser = localStorage.getItem('fap_auth_user');
            const authToken = localStorage.getItem('fap_auth_token');
            const url = new URL(window.parent.location.href);
            if (authUser && authToken && !url.searchParams.has('auth_user')) {
                url.searchParams.set('auth_user', authUser);
                url.searchParams.set('auth_token', authToken);
                window.parent.location.replace(url.toString());
            }
        })();
        </script>
        """,
        height=0,
    )

    # ── Handle logout: clear localStorage ──
    if st.session_state.get("_logout_triggered"):
        components.html(
            """
            <script>
            localStorage.removeItem('fap_auth_user');
            localStorage.removeItem('fap_auth_token');
            </script>
            """,
            height=0,
        )
        st.session_state._logout_triggered = False

    # ── CSS: hide sidebar navigation on login page ──
    st.markdown(
        """
        <style>
        /* Hide sidebar navigation on login page */
        [data-testid="stSidebarNav"] { display: none !important; }
        section[data-testid="stSidebar"] { display: none !important; }
        [data-testid="stSidebarCollapsedControl"] { display: none !important; }
        .login-container {
            max-width: 450px;
            margin: 4rem auto;
            padding: 2.5rem;
            background: var(--bg-glass);
            backdrop-filter: blur(12px);
            border: 1px solid var(--border-glass);
            border-radius: 20px;
            box-shadow: var(--shadow-card);
        }
        .login-title {
            font-family: 'Outfit', sans-serif;
            font-size: 2rem;
            font-weight: 800;
            background: linear-gradient(135deg, #6C63FF, #00D4AA);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-align: center;
            margin-bottom: 0.5rem;
        }
        .login-subtitle {
            text-align: center;
            color: var(--text-secondary);
            font-size: 0.95rem;
            margin-bottom: 2rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    col_spacer1, col_center, col_spacer2 = st.columns([1, 2, 1])

    with col_center:
        st.markdown(
            """
            <div style="text-align: center; margin-top: 3rem;">
                <div class="login-title">🏦 Finance Advisor Pro</div>
                <div class="login-subtitle">Connectez-vous à votre espace conseiller</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        tab_login, tab_register = st.tabs(["🔐 Connexion", "📝 Créer un compte"])

        with tab_login:
            with st.form("login_form"):
                username = st.text_input("Identifiant", placeholder="votre.identifiant")
                password = st.text_input("Mot de passe", type="password", placeholder="••••••••")
                submitted = st.form_submit_button("Se connecter", use_container_width=True)

                if submitted:
                    if username and password:
                        user = authenticate(username, password)
                        if user:
                            st.session_state.authenticated = True
                            st.session_state.user = user
                            # Generate token and store in query_params for JS pickup
                            token = _generate_auth_token(username)
                            st.session_state._login_user = username
                            st.session_state._login_token = token
                            st.rerun()
                        else:
                            st.error("❌ Identifiant ou mot de passe incorrect.")
                    else:
                        st.warning("Veuillez remplir tous les champs.")

            st.markdown(
                "<p style='text-align: center; color: var(--text-secondary); font-size: 0.8rem; margin-top: 1rem;'>"
                "Compte démo : <b>demo</b> / <b>demo123</b></p>",
                unsafe_allow_html=True,
            )

        with tab_register:
            with st.form("register_form"):
                new_name = st.text_input("Nom complet", placeholder="Jean Dupont")
                new_cabinet = st.text_input("Nom du cabinet", placeholder="Mon Cabinet SA")
                new_email = st.text_input("Email", placeholder="jean@cabinet.ch")
                new_username = st.text_input("Identifiant souhaité", placeholder="jean.dupont")
                new_password = st.text_input("Mot de passe", type="password", placeholder="Min. 6 caractères")
                new_password2 = st.text_input("Confirmer le mot de passe", type="password")
                reg_submitted = st.form_submit_button("Créer mon compte", use_container_width=True)

                if reg_submitted:
                    if not all([new_name, new_username, new_password, new_password2]):
                        st.warning("Veuillez remplir tous les champs obligatoires.")
                    elif len(new_password) < 6:
                        st.warning("Le mot de passe doit contenir au moins 6 caractères.")
                    elif new_password != new_password2:
                        st.error("Les mots de passe ne correspondent pas.")
                    else:
                        success = register_user(
                            username=new_username,
                            password=new_password,
                            name=new_name,
                            email=new_email,
                            cabinet=new_cabinet,
                        )
                        if success:
                            st.success("✅ Compte créé ! Vous pouvez maintenant vous connecter.")
                        else:
                            st.error("❌ Cet identifiant est déjà pris.")


    return False


def require_auth():
    """
    Guard d'authentification. Appeler en haut de chaque page.
    Arrête l'exécution si non authentifié.
    """
    import streamlit.components.v1 as components

    init_session()
    if not is_authenticated():
        login_page()
        st.stop()

    # If we just logged in, inject JS to save credentials to localStorage
    if st.session_state.get("_login_user"):
        user = st.session_state._login_user
        token = st.session_state._login_token
        components.html(
            f"""
            <script>
            localStorage.setItem('fap_auth_user', '{user}');
            localStorage.setItem('fap_auth_token', '{token}');
            </script>
            """,
            height=0,
        )
        del st.session_state._login_user
        del st.session_state._login_token


def sidebar_user_info():
    """Affiche les infos utilisateur dans la sidebar."""
    user = get_current_user()
    if user:
        st.sidebar.markdown("---")
        st.sidebar.markdown(f"**👤 {user['name']}**")
        if user.get("cabinet"):
            st.sidebar.markdown(f"🏢 {user['cabinet']}")
        if st.sidebar.button("🚪 Déconnexion", use_container_width=True):
            logout()
            st.rerun()


def client_banner():
    """Affiche un bandeau avec le client actuellement sélectionné."""
    client = st.session_state.get("current_client")
    if client:
        nom_complet = f"{client.get('prenom', '')} {client.get('nom', '')}".strip()
        statut = client.get("statut", "prospect")
        statut_emoji = {"prospect": "🟡", "actif": "🟢", "inactif": "🔴"}.get(statut, "⚪")

        st.markdown(
            f"""
            <div style="
                background: linear-gradient(135deg, rgba(108, 99, 255, 0.15), rgba(0, 212, 170, 0.08));
                border: 1px solid rgba(108, 99, 255, 0.3);
                border-radius: 12px;
                padding: 0.75rem 1.25rem;
                margin-bottom: 1rem;
                display: flex;
                justify-content: space-between;
                align-items: center;
            ">
                <div>
                    <span style="font-weight: 700; font-size: 1.05rem;">👤 {nom_complet}</span>
                    <span style="margin-left: 1rem; color: var(--text-secondary);">
                        {statut_emoji} {statut.capitalize()} ·
                        {client.get('canton', '')} ·
                        CHF {client.get('salaire_annuel', 0):,.0f}/an
                    </span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        col_msg, col_btn = st.columns([4, 1])
        with col_msg:
            st.markdown(
                """
                <div style="
                    background: rgba(255, 179, 71, 0.1);
                    border: 1px solid rgba(255, 179, 71, 0.3);
                    border-radius: 12px;
                    padding: 0.6rem 1.25rem;
                    margin-bottom: 1rem;
                    color: #FFB347;
                    font-size: 0.9rem;
                ">
                    ⚠️ Aucun client sélectionné
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col_btn:
            if st.button("👥 Sélectionner un client", use_container_width=True):
                st.switch_page("pages/0_Clients.py")
