"""Access code authentication for the single coordinator demo."""
import hashlib
import hmac
import re
import secrets
import time


class DemoAuth:
    def __init__(self, access_digest, signing_key):
        if not re.fullmatch(r'[0-9a-f]{64}', access_digest or '') or len(signing_key or '') < 43:
            raise ValueError('Hosted mode requires a SHA256 access digest and a strong session signing key.')
        self.access_digest = access_digest
        self.signing_key = signing_key.encode()

    def accepts(self, code):
        return secrets.compare_digest(hashlib.sha256(code.encode()).hexdigest(), self.access_digest)

    def issue(self):
        payload = f'{int(time.time()) + 43200}.{secrets.token_urlsafe(16)}'
        signature = hmac.new(self.signing_key, payload.encode(), hashlib.sha256).hexdigest()
        return f'{payload}.{signature}'

    def valid(self, token):
        try:
            expires, nonce, signature = token.split('.')
            expected = hmac.new(self.signing_key, f'{expires}.{nonce}'.encode(), hashlib.sha256).hexdigest()
            return int(time.time()) < int(expires) <= int(time.time()) + 43200 and hmac.compare_digest(expected, signature)
        except (ValueError, TypeError):
            return False
