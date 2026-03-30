"""
Email service using Python's built-in smtplib.
Configure via environment variables: SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD.
"""

import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.config.settings import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Sends emails via SMTP."""

    def _build_message(self, to: str, subject: str, html: str) -> MIMEMultipart:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{settings.smtp_from_name} <{settings.smtp_from}>"
        msg["To"] = to
        msg.attach(MIMEText(html, "html", "utf-8"))
        return msg

    def send(self, to: str, subject: str, html: str) -> None:
        """Send an email. Logs a warning if SMTP is not configured."""
        if not settings.smtp_user or not settings.smtp_password:
            logger.warning(
                "SMTP not configured — skipping email to %s | Subject: %s", to, subject
            )
            return

        msg = self._build_message(to, subject, html)
        try:
            with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as server:
                server.ehlo()
                server.starttls()
                server.login(settings.smtp_user, settings.smtp_password)
                server.sendmail(settings.smtp_from, to, msg.as_string())
            logger.info("Email sent to %s | Subject: %s", to, subject)
        except Exception as exc:
            logger.error("Failed to send email to %s: %s", to, exc)
            raise

    def send_verification_code(self, to: str, code: str) -> None:
        """Send email verification code with a styled HTML template."""
        subject = "Tu código de verificación — Archivo ROGER"
        digits = list(code)
        html = f"""
<!DOCTYPE html>
<html lang="es">
<head><meta charset="utf-8" /></head>
<body style="margin:0;padding:0;background:#f4f4f5;font-family:system-ui,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0">
    <tr>
      <td align="center" style="padding:40px 16px;">
        <table width="100%" style="max-width:520px;background:#ffffff;border-radius:12px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,0.08);">

          <!-- Header -->
          <tr>
            <td style="background:#1d1d1f;padding:28px 32px;text-align:center;">
              <p style="margin:0;font-size:22px;font-weight:700;color:#ffffff;letter-spacing:2px;">ROGER</p>
              <p style="margin:4px 0 0;font-size:11px;color:#888;text-transform:uppercase;letter-spacing:1px;">Archivo Gerstmann · UCN</p>
            </td>
          </tr>

          <!-- Body -->
          <tr>
            <td style="padding:36px 32px 12px;">
              <h1 style="margin:0 0 10px;font-size:20px;font-weight:700;color:#1d1d1f;">Verifica tu correo electrónico</h1>
              <p style="margin:0 0 8px;font-size:15px;color:#555;line-height:1.6;">
                Gracias por unirte al Archivo ROGER. Para completar el registro de tu cuenta, ingresa el siguiente código de verificación:
              </p>
              <p style="margin:0 0 28px;font-size:13px;color:#999;">
                El código es válido por <strong style="color:#555;">10 minutos</strong> y es de un solo uso.
              </p>
            </td>
          </tr>

          <!-- Code block -->
          <tr>
            <td style="padding:0 32px 32px;">
              <table width="100%" cellpadding="0" cellspacing="0">
                <tr>
                  <td align="center">
                    <div style="background:#f4f4f5;border-radius:12px;padding:24px 16px;display:inline-block;width:100%;">
                      <p style="margin:0 0 12px;font-size:11px;font-weight:600;color:#999;text-transform:uppercase;letter-spacing:2px;">Código de verificación</p>
                      <div style="display:flex;justify-content:center;gap:8px;text-align:center;">
                        {''.join(f'<span style="display:inline-block;width:44px;height:56px;line-height:56px;background:#ffffff;border:2px solid #e5e7eb;border-radius:8px;font-size:28px;font-weight:800;color:#1d1d1f;font-family:monospace;box-shadow:0 1px 3px rgba(0,0,0,0.08);">{d}</span>' for d in digits)}
                      </div>
                    </div>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- Warning -->
          <tr>
            <td style="padding:0 32px 32px;">
              <div style="background:#fff8ed;border:1px solid #fcd34d;border-radius:8px;padding:12px 16px;">
                <p style="margin:0;font-size:12px;color:#92400e;line-height:1.5;">
                  ⚠️ Si no creaste una cuenta en el Archivo ROGER, ignora este correo. Nadie más puede usar este código.
                </p>
              </div>
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="padding:20px 32px;background:#f9f9f9;border-top:1px solid #eee;text-align:center;">
              <p style="margin:0;font-size:11px;color:#bbb;">
                Universidad Católica del Norte · Proyecto FONDEF ROGER<br />
                Este es un mensaje automático, por favor no respondas a este correo.
              </p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>
        """
        self.send(to, subject, html)

    def send_password_reset(self, to: str, reset_url: str) -> None:
        """Send password reset email with a styled HTML template."""
        subject = "Recupera tu contraseña — Archivo ROGER"
        html = f"""
<!DOCTYPE html>
<html lang="es">
<head><meta charset="utf-8" /></head>
<body style="margin:0;padding:0;background:#f4f4f5;font-family:system-ui,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0">
    <tr>
      <td align="center" style="padding:40px 16px;">
        <table width="100%" style="max-width:520px;background:#ffffff;border-radius:12px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,0.08);">

          <!-- Header -->
          <tr>
            <td style="background:#1d1d1f;padding:28px 32px;text-align:center;">
              <p style="margin:0;font-size:22px;font-weight:700;color:#ffffff;letter-spacing:2px;">ROGER</p>
              <p style="margin:4px 0 0;font-size:11px;color:#888;text-transform:uppercase;letter-spacing:1px;">Archivo Gerstmann · UCN</p>
            </td>
          </tr>

          <!-- Body -->
          <tr>
            <td style="padding:36px 32px 28px;">
              <h1 style="margin:0 0 12px;font-size:20px;font-weight:700;color:#1d1d1f;">Recupera tu contraseña</h1>
              <p style="margin:0 0 24px;font-size:15px;color:#555;line-height:1.6;">
                Recibimos una solicitud para restablecer la contraseña de tu cuenta. Haz clic en el botón a continuación para crear una nueva contraseña.
              </p>
              <p style="margin:0 0 32px;font-size:13px;color:#999;">
                Este enlace es válido por <strong style="color:#555;">15 minutos</strong>. Si no solicitaste este cambio, puedes ignorar este correo.
              </p>

              <!-- CTA Button -->
              <table width="100%" cellpadding="0" cellspacing="0">
                <tr>
                  <td align="center">
                    <a href="{reset_url}"
                       style="display:inline-block;background:#2563eb;color:#ffffff;text-decoration:none;font-size:15px;font-weight:600;padding:14px 32px;border-radius:8px;">
                      Restablecer contraseña
                    </a>
                  </td>
                </tr>
              </table>

              <!-- Fallback URL -->
              <p style="margin:28px 0 0;font-size:12px;color:#bbb;text-align:center;">
                Si el botón no funciona, copia este enlace en tu navegador:<br />
                <a href="{reset_url}" style="color:#2563eb;word-break:break-all;">{reset_url}</a>
              </p>
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="padding:20px 32px;background:#f9f9f9;border-top:1px solid #eee;text-align:center;">
              <p style="margin:0;font-size:11px;color:#bbb;">
                Universidad Católica del Norte · Proyecto FONDEF ROGER<br />
                Este es un mensaje automático, por favor no respondas a este correo.
              </p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>
        """
        self.send(to, subject, html)


email_service = EmailService()
