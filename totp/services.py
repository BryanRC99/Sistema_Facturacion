import base64
import io

import pyotp
import qrcode


def generate_totp_secret() -> str:
    return pyotp.random_base32()  # compatible con Google Authenticator


def build_provisioning_uri(secret: str, username: str, issuer: str) -> str:
    # issuer = nombre de tu sistema (sale en Google Authenticator)
    totp = pyotp.TOTP(secret)
    return totp.provisioning_uri(name=username, issuer_name=issuer)


def make_qr_base64(data: str) -> str:
    """
    Devuelve un PNG en base64 listo para usar en:
    <img src="data:image/png;base64,{{ qr_b64 }}">
    """
    img = qrcode.make(data)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("utf-8")


def verify_totp_code(secret: str, code: str) -> bool:
    if not secret:
        return False
    code = (code or "").strip().replace(" ", "")
    if not code.isdigit() or len(code) != 6:
        return False
    totp = pyotp.TOTP(secret)
    # valid_window=1 permite un margen de 30s antes/después (reduce falsos negativos)
    return bool(totp.verify(code, valid_window=1))
