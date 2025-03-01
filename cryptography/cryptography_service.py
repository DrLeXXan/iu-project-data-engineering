from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from fastapi import FastAPI

app = FastAPI()

# Generate RSA keys once and store them
def generate_rsa_keys() -> str:
    """This function generates the private and public key and returns them as serialized and decoded string"""
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    public_key = private_key.public_key()

    # Serialize private key
    private_key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ).decode('utf-8')

    # Serialize public key
    public_key_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode('utf-8')

    return private_key_pem, public_key_pem

# Generate keys once and store them in memory
private_key_pem, public_key_pem = generate_rsa_keys()


#Creates the different API for private and public key
@app.get("/private-key")
def get_private_key() -> dict:
    """Returns the RSA public key in PEM format."""
    return {"private-key": private_key_pem}

@app.get("/public-key")
def get_public_key() -> dict:
    """Returns the RSA public key in PEM format."""
    return {"public-key": public_key_pem}
