"""
Module Email — Envoi de rapports par email
Infrastructure SMTP pour l'envoi de PDF et notifications aux clients.
"""

import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from datetime import datetime
import streamlit as st


def get_smtp_config() -> dict | None:
    """Récupère la configuration SMTP depuis les secrets Streamlit ou les session_state."""
    # Try Streamlit secrets first
    try:
        return {
            "host": st.secrets["smtp"]["host"],
            "port": st.secrets["smtp"]["port"],
            "user": st.secrets["smtp"]["user"],
            "password": st.secrets["smtp"]["password"],
            "from_name": st.secrets["smtp"].get("from_name", "Finance Advisor Pro"),
        }
    except (KeyError, FileNotFoundError):
        pass

    # Try session_state (set by advisor settings)
    if "smtp_config" in st.session_state:
        return st.session_state["smtp_config"]

    return None


def is_email_configured() -> bool:
    """Vérifie si l'email est configuré."""
    return get_smtp_config() is not None


def send_report_email(
    to_email: str,
    client_name: str,
    module_name: str,
    pdf_bytes: bytes,
    advisor_name: str = "",
) -> tuple[bool, str]:
    """
    Envoie un rapport PDF par email au client.
    
    Returns:
        (success, message)
    """
    config = get_smtp_config()
    if not config:
        return False, "Configuration SMTP non trouvée. Configurez vos identifiants SMTP dans .streamlit/secrets.toml"

    try:
        msg = MIMEMultipart("mixed")
        msg["From"] = f"{config['from_name']} <{config['user']}>"
        msg["To"] = to_email
        msg["Subject"] = f"Rapport {module_name} — {client_name} — Finance Advisor Pro"

        # HTML body
        html_body = _build_email_html(client_name, module_name, advisor_name)
        msg.attach(MIMEText(html_body, "html", "utf-8"))

        # PDF attachment
        filename = f"Rapport_{module_name}_{client_name}_{datetime.now().strftime('%Y%m%d')}.pdf"
        filename = filename.replace(" ", "_")
        pdf_part = MIMEApplication(pdf_bytes, _subtype="pdf")
        pdf_part.add_header("Content-Disposition", "attachment", filename=filename)
        msg.attach(pdf_part)

        # Send
        context = ssl.create_default_context()
        with smtplib.SMTP(config["host"], config["port"]) as server:
            server.starttls(context=context)
            server.login(config["user"], config["password"])
            server.send_message(msg)

        return True, f" Email envoyé à {to_email}"

    except smtplib.SMTPAuthenticationError:
        return False, " Erreur d'authentification SMTP. Vérifiez vos identifiants."
    except smtplib.SMTPException as e:
        return False, f" Erreur SMTP : {str(e)}"
    except Exception as e:
        return False, f" Erreur : {str(e)}"


def _build_email_html(client_name: str, module_name: str, advisor_name: str) -> str:
    """Construit le corps HTML de l'email."""
    return f"""
    <html>
    <body style="font-family: 'Segoe UI', Arial, sans-serif; background: #0E1117; color: #fff; padding: 20px;">
        <div style="max-width: 600px; margin: 0 auto; background: #1E2130; border-radius: 12px; overflow: hidden;">
            <div style="background: linear-gradient(135deg, #6C63FF, #3B82F6); padding: 30px; text-align: center;">
                <h1 style="margin: 0; font-size: 24px; color: white;">Finance Advisor Pro</h1>
                <p style="margin: 5px 0 0; color: rgba(255,255,255,0.8); font-size: 14px;">Rapport de simulation</p>
            </div>
            <div style="padding: 30px;">
                <p style="color: #A0A3B1; font-size: 14px;">Bonjour {client_name},</p>
                <p style="color: #fff; font-size: 14px;">
                    Veuillez trouver ci-joint votre rapport <b>{module_name}</b> 
                    généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}.
                </p>
                <div style="background: rgba(108, 99, 255, 0.1); border: 1px solid rgba(108, 99, 255, 0.3); 
                    border-radius: 8px; padding: 15px; margin: 20px 0;">
                    <p style="color: #6C63FF; font-weight: 700; margin: 0;"> {module_name}</p>
                    <p style="color: #A0A3B1; font-size: 12px; margin: 5px 0 0;">
                        Le rapport PDF est en pièce jointe de cet email.
                    </p>
                </div>
                <p style="color: #A0A3B1; font-size: 13px;">
                    N'hésitez pas à me contacter pour toute question concernant ce rapport.
                </p>
                <p style="color: #fff; font-size: 14px; margin-top: 20px;">
                    Cordialement,<br>
                    <b>{advisor_name}</b>
                </p>
            </div>
            <div style="background: #0E1117; padding: 15px; text-align: center;">
                <p style="color: #A0A3B1; font-size: 11px; margin: 0;">
                    Ce rapport est fourni à titre indicatif et ne constitue pas un conseil financier.<br>
                    Finance Advisor Pro · Suisse Romande
                </p>
            </div>
        </div>
    </body>
    </html>
    """


def email_send_section(
    module_name: str,
    pdf_bytes: bytes,
    client: dict | None = None,
    advisor_name: str = "",
):
    """
    Affiche la section d'envoi par email dans l'interface.
    À appeler après la génération du PDF.
    """
    if not client:
        return

    client_name = f"{client.get('prenom', '')} {client.get('nom', '')}".strip()
    client_email = client.get("email", "")

    if not is_email_configured():
        st.caption(" Pour activer l'envoi par email, configurez SMTP dans `.streamlit/secrets.toml`")
        return

    with st.expander(" Envoyer par email"):
        email_to = st.text_input(
            "Adresse email",
            value=client_email,
            key=f"email_to_{module_name}",
            placeholder="client@email.com",
        )

        if st.button(f" Envoyer le rapport", key=f"send_email_{module_name}", use_container_width=True):
            if email_to:
                with st.spinner("Envoi en cours..."):
                    success, message = send_report_email(
                        to_email=email_to,
                        client_name=client_name,
                        module_name=module_name,
                        pdf_bytes=pdf_bytes,
                        advisor_name=advisor_name,
                    )
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
            else:
                st.warning("Veuillez saisir une adresse email.")
