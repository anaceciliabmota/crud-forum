from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(senha: str) -> str:
    return pwd_context.hash(senha)


def verify_password(senha: str, senha_hash: str) -> bool:
    return pwd_context.verify(senha, senha_hash)
