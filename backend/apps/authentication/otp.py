import pyotp

def generate_totp_secret():
    return pyotp.random_base32()

def get_totp_uri(user):
    if not user.totp_secret:
        user.totp_secret = generate_totp_secret()
        user.save()
    totp = pyotp.TOTP(user.totp_secret)
    return totp.provisioning_uri(name=user.phone_number, issuer_name="SecureOnlineVoting")

def verify_totp_code(user, entered_code):
    if not user.totp_secret or not entered_code:
        return False
    totp = pyotp.TOTP(user.totp_secret)
    return totp.verify(str(entered_code).strip())
