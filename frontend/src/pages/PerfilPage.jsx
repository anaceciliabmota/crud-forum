import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import api from '../api/client';
import Layout from '../components/Layout';

export default function PerfilPage() {
  const { id } = useParams();
  const [perfil, setPerfil] = useState(null);
  const [error, setError] = useState('');
  const [aba, setAba] = useState('topicos');

  useEffect(() => {
    api.get(`/usuarios/${id}/perfil`)
      .then(({ data }) => setPerfil(data))
      .catch((err) => setError(err.response?.data?.detail || 'Erro ao carregar perfil'));
  }, [id]);

  if (!perfil && !error) return <Layout><p>Carregando...</p></Layout>;

  return (
    <Layout>
      {error && <p className="error">{error}</p>}
      {perfil && (
        <>
          <div className="card perfil-header">
            <h1>{perfil.usuario.nome}</h1>
            <p>
              <span className="badge">{perfil.usuario.role}</span>
              {' '}Membro desde {new Date(perfil.usuario.created_at).toLocaleDateString('pt-BR')}
            </p>
            <p>{perfil.topicos.length} tópicos · {perfil.respostas.length} respostas</p>
          </div>

          <div className="abas">
            <button
              type="button"
              className={aba === 'topicos' ? 'aba ativa' : 'aba'}
              onClick={() => setAba('topicos')}
            >
              Tópicos ({perfil.topicos.length})
            </button>
            <button
              type="button"
              className={aba === 'respostas' ? 'aba ativa' : 'aba'}
              onClick={() => setAba('respostas')}
            >
              Respostas ({perfil.respostas.length})
            </button>
          </div>

          {aba === 'topicos' && (
            <ul className="list">
              {perfil.topicos.length === 0 && <li className="card hint">Nenhum tópico publicado.</li>}
              {perfil.topicos.map((t) => (
                <li key={t.id} className="card">
                  <Link to={`/topicos/${t.id}`}><strong>{t.titulo}</strong></Link>
                  <p>{t.corpo.slice(0, 120)}{t.corpo.length > 120 ? '...' : ''}</p>
                  <small>{new Date(t.created_at).toLocaleDateString('pt-BR')}</small>
                </li>
              ))}
            </ul>
          )}

          {aba === 'respostas' && (
            <ul className="list">
              {perfil.respostas.length === 0 && <li className="card hint">Nenhuma resposta publicada.</li>}
              {perfil.respostas.map((r) => (
                <li key={r.id} className="card">
                  {r.aceita && <span className="badge badge-aceita">Melhor resposta</span>}
                  <p>{r.corpo.slice(0, 120)}{r.corpo.length > 120 ? '...' : ''}</p>
                  <small>
                    Em <Link to={`/topicos/${r.topico_id}`}>tópico #{r.topico_id}</Link>
                    {' · '}{new Date(r.created_at).toLocaleDateString('pt-BR')}
                  </small>
                </li>
              ))}
            </ul>
          )}
        </>
      )}
    </Layout>
  );
}
