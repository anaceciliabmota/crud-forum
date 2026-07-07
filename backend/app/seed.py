from app.config import settings
from app.database import SessionLocal
from app.models import Comunidade, MembroComunidade, Topico, UserRole, Usuario
from app.services.auth import hash_password
from app.services.slug import slugify


def run_seed():
    db = SessionLocal()
    try:
        admin = db.query(Usuario).filter(Usuario.email == settings.admin_email).first()
        if not admin:
            admin = Usuario(
                nome=settings.admin_nome,
                email=settings.admin_email,
                senha_hash=hash_password(settings.admin_password),
                role=UserRole.ADMIN,
            )
            db.add(admin)
            db.commit()
            db.refresh(admin)
            print(f"Admin criado: {settings.admin_email}")
        else:
            print("Admin já existe, pulando criação.")

        comunidade = db.query(Comunidade).filter(Comunidade.slug == "comunidade-demo").first()
        if not comunidade:
            comunidade = Comunidade(
                nome="Comunidade Demo",
                slug="comunidade-demo",
                descricao="Comunidade de demonstração do fórum.",
                criador_id=admin.id,
            )
            db.add(comunidade)
            db.flush()

            db.add(MembroComunidade(usuario_id=admin.id, comunidade_id=comunidade.id))

            topico = Topico(
                titulo="Bem-vindo ao fórum!",
                corpo="Este é um tópico de demonstração. Explore as comunidades e participe.",
                autor_id=admin.id,
                comunidade_id=comunidade.id,
                fixado=True,
            )
            db.add(topico)
            db.commit()
            print("Dados demo criados.")
        else:
            print("Dados demo já existem, pulando criação.")
    finally:
        db.close()


if __name__ == "__main__":
    run_seed()
