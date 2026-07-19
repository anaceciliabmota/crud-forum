from sqlalchemy.orm import Session

from app.models import AlvoTipo, Voto


def contar_votos(db: Session, alvo_tipo: AlvoTipo, alvo_id: int, usuario_id: int | None = None) -> dict:
    votos = db.query(Voto).filter(Voto.alvo_tipo == alvo_tipo, Voto.alvo_id == alvo_id).all()
    upvotes = sum(1 for v in votos if v.valor == 1)
    downvotes = sum(1 for v in votos if v.valor == -1)
    meu_voto = None
    if usuario_id is not None:
        voto = next((v for v in votos if v.usuario_id == usuario_id), None)
        meu_voto = voto.valor if voto else None
    return {"upvotes": upvotes, "downvotes": downvotes, "score": upvotes - downvotes, "meu_voto": meu_voto}
