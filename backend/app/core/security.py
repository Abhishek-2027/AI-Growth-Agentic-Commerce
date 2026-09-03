import hmac
import hashlib
from app.core.config import settings


def verify_razorpay_signature(
    order_id: str,
    payment_id: str,
    signature: str,
) -> bool:
    """
    Verify Razorpay payment signature using HMAC-SHA256.
    This is the authoritative server-side verification — never trust frontend alone.
    """
    message = f"{order_id}|{payment_id}"
    expected = hmac.new(
        settings.razorpay_key_secret.encode("utf-8"),
        message.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, signature)
