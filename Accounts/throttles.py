from rest_framework.throttling import AnonRateThrottle


class LoginThrottle(AnonRateThrottle):
    rate = "5/min"


class RegisterThrottle(AnonRateThrottle):
    rate = "10/min"





class PasswordResetThrottle(AnonRateThrottle):
    """Limit password reset requests per IP."""
    scope = "password_reset"


class PasswordResetConfirmThrottle(AnonRateThrottle):
    """Limit confirm attempts to slow down token brute-forcing."""
    scope = "password_reset_confirm"
