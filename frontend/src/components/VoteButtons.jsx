import { ThumbsDown, ThumbsUp } from 'lucide-react';
import { useState } from 'react';
import api from '../api/client';
import { useAuth } from '../context/AuthContext';

export default function VoteButtons({ alvoTipo, alvoId, votosIniciais, onUpdate, autorId }) {
  const [votos, setVotos] = useState(
    votosIniciais || { upvotes: 0, downvotes: 0, score: 0, meu_voto: null }
  );
  const { isMembro, user } = useAuth();

  const ehAutor = autorId != null && user?.id === autorId;

  const handleVoto = async (valor) => {
    if (!isMembro || ehAutor) return;
    try {
      if (votos.meu_voto === valor) {
        await api.delete(`/votos?alvo_tipo=${alvoTipo}&alvo_id=${alvoId}`);
        setVotos((v) => ({
          ...v,
          upvotes: valor === 1 ? v.upvotes - 1 : v.upvotes,
          downvotes: valor === -1 ? v.downvotes - 1 : v.downvotes,
          score: v.score - valor,
          meu_voto: null,
        }));
      } else {
        const { data } = await api.post('/votos', { alvo_tipo: alvoTipo, alvo_id: alvoId, valor });
        setVotos(data);
      }
      onUpdate?.();
    } catch {
      // silently ignore other errors
    }
  };

  const loginTitle = 'Faça login para votar';
  const autorTitle = 'Autores não podem votar no próprio conteúdo';

  return (
    <div className="vote-wrapper">
      <div className="vote-buttons">
        <button
          type="button"
          className={`vote-btn vote-btn-like${votos.meu_voto === 1 ? ' ativo' : ''}`}
          onClick={() => handleVoto(1)}
          disabled={!isMembro || ehAutor}
          title={ehAutor ? autorTitle : isMembro ? 'Curtir' : loginTitle}
        >
          <ThumbsUp size={15} />
          <span className="vote-count">{votos.upvotes}</span>
        </button>

        <button
          type="button"
          className={`vote-btn vote-btn-dislike${votos.meu_voto === -1 ? ' ativo' : ''}`}
          onClick={() => handleVoto(-1)}
          disabled={!isMembro || ehAutor}
          title={ehAutor ? autorTitle : isMembro ? 'Descurtir' : loginTitle}
        >
          <ThumbsDown size={15} />
          <span className="vote-count">{votos.downvotes}</span>
        </button>
      </div>

      {ehAutor && (
        <span className="vote-hint">Autores não podem votar</span>
      )}
    </div>
  );
}
