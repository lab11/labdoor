'''
Spec:

Uses sorted json with no whitespace in separators, fight me

{
    "v": 1, # version
    "u": "name",   # user
    "s": start_timestamp, int
    "e": end_timestamp, int
}

'''

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.serialization import load_pem_private_key
import base64
import datetime
import json
from flask import Flask
app = Flask(__name__)


BLACKLIST = {
    'zakir',
}


def postvalidate_token(token_dict):
    try:
        start = token_dict['s']
        end = token_dict['e']
        u = token_dict['u']
        now = datetime.datetime.utcnow().timestamp()
        if not end > start:
            raise Exception("Invalid start/end")
        if start > now:
            raise Exception("Token not yet valid")
        if now > end:
            raise Exception("Token expired")
        if u in BLACKLIST:
            raise Exception("Blacklisted")
    except KeyError:
        raise Exception("Token missing key")


@app.route('/')
def index():
    return "Fuck you, Branden"


@app.route('/u/<token>/<signature>')
def unlock(token, signature):
    token = base64.urlsafe_b64decode(token)
    signature = base64.urlsafe_b64decode(signature)
    with open("key.pem", "rb") as fd:
        private_key = load_pem_private_key(
                fd.read(), password=None, backend=default_backend())
    public_key = private_key.public_key()
    # Throws exception if invalid
    public_key.verify(signature, token, ec.ECDSA(hashes.SHA256()))
    token_dict = json.loads(token.decode("utf-8"))
    postvalidate_token(token_dict)
    return 'Unlock!'


@app.route('/issue/<name>')
def issue(name):
    '''
    Find a way to protect this route. Either hack in some basic auth, check
    knowledge of an additional password in an environment variable, etc.
    '''
    start = datetime.datetime.utcnow()
    end = start + datetime.timedelta(days=7)
    obj = {
        'v': 1,
        'u': name,
        's': int(start.timestamp()),
        'e': int(end.timestamp()),
    }
    j = json.dumps(obj, sort_keys=True, separators=(',', ':'))
    token = bytes(j, 'utf-8')
    with open("key.pem", "rb") as fd:
        private_key = load_pem_private_key(
                fd.read(), password=None, backend=default_backend())
    signature = private_key.sign(token, ec.ECDSA(hashes.SHA256()))
    encoded_token = base64.urlsafe_b64encode(token).decode('utf-8')
    encoded_signature = base64.urlsafe_b64encode(signature).decode('utf-8')
    return json.dumps({
        'token': encoded_token,
        'signature': encoded_signature,
    })


if __name__ == '__main__':
    import flask
    flask.run(app)
