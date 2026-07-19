import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import api from '../api/client';
import Layout from '../components/Layout';
import VoteButtons from '../components/VoteButtons';
import { useAuth } from '../context/AuthContext';

export default function TopicoPage() {
  const { id } = useParams();
  const [topico, setTopico] = useState(null);
  const [respostas, setRespostas] = useState([]);
  const [error, setError] = useState('');
  const [corpo, setCorpo] = useState('');
  const [editResposta, setEditResposta] = useState(null);
  const { user, isMembro, isAdmin } = useAuth();

  const load = async () => {
    try {
      const { data: top } = await api.get(`/topicos/${id}`);
      setTopico(top);
      const { data: resp } = await api.get(`/topicos/${id}/respostas`);
      setRespostas(resp);
    } catch (err) {
      setError(err.response?.data?.detail || 'Erro ao carregar');
    }
  };

  useEffect(() => {
    load();
  }, [id]);

  const handleCreateResposta = async (e) => {
    e.preventDefault();
    try {
      await api.post(`/topicos/${id}/respostas`, { corpo });
      setCorpo('');
      load();
    } catch (err) {
      setError(err.response?.data?.detail || 'Erro ao responder');
    }
  };

  const handleDeleteResposta = async (respostaId) => {
    if (!window.confirm('Excluir resposta?')) return;
    try {
      await api.delete(`/respostas/${respostaId}`);
      load();
    } catch (err) {
      setError(err.response?.data?.detail || 'Erro ao excluir');
    }
  };

  const handleUpdateResposta = async (e) => {
    e.preventDefault();
    try {
      await api.put(`/respostas/${editResposta.id}`, { corpo: editResposta.corpo });
      setEditResposta(null);
      load();
    } catch (err) {
      setError(err.response?.data?.detail || 'Erro ao editar');
    }
  };

  const handleAceitar = async (respostaId, aceita) => {
    try {
      await api.patch(`/respostas/${respostaId}/aceitar`, { aceita });
      load();
    } catch (err) {
      setError(err.response?.data?.detail || 'Erro ao marcar resposta');
    }
  };

  const canModify = (autorId) => isAdmin || user?.id === autorId;
  const podeAceitar = topico && (isAdmin || user?.id === topico.autor_id);

  if (!topico && !error) return <Layout><p>Carregando...</p></Layout>;

  return (
    <Layout>
      {topico && (
        <>
          <Link to={`/comunidades/${topico.comunidade_slug}`}>← Voltar</Link>
          <h1>{topico.titulo} {topico.fixado && <span className="badge">Fixado</span>}</h1>
          <div className="topico-header">
            <VoteButtons alvoTipo="TOPICO" alvoId={topico.id} votosIniciais={topico.votos} onUpdate={load} autorId={topico.autor_id} />
            <div>
              <p>{topico.corpo}</p>
              <small>Por <Link to={`/perfil/${topico.autor_id}`}>{topico.autor_nome}</Link></small>
            </div>
          </div>
        </>
      )}

      {error && <p className="error">{typeof error === 'string' ? error : JSON.stringify(error)}</p>}

      {isMembro && topico && !topico.fechado && (
        <form className="card form" onSubmit={handleCreateResposta}>
          <h2>Responder</h2>
          <textarea placeholder="Sua resposta" value={corpo} onChange={(e) => setCorpo(e.target.value)} required />
          <button type="submit">Enviar</button>
        </form>
      )}

      <h2>Respostas ({respostas.length})</h2>
      <ul className="list">
        {respostas.map((r) => (
          <li key={r.id} className={`card${r.aceita ? ' card-aceita' : ''}`}>
            {r.aceita && <span className="badge badge-aceita">Melhor resposta</span>}
            <div className="resposta-row">
              <VoteButtons alvoTipo="RESPOSTA" alvoId={r.id} votosIniciais={r.votos} onUpdate={load} autorId={r.autor_id} />
              <div className="resposta-body">
                <p>{r.corpo}</p>
                <small>Por <Link to={`/perfil/${r.autor_id}`}>{r.autor_nome}</Link></small>
                <div className="actions">
                  {podeAceitar && (
                    r.aceita
                      ? <button type="button" className="btn-aceita" onClick={() => handleAceitar(r.id, false)}>Remover solução</button>
                      : <button type="button" className="btn-aceita" onClick={() => handleAceitar(r.id, true)}>Marcar como solução</button>
                  )}
                  {canModify(r.autor_id) && (
                    <>
                      <button type="button" onClick={() => setEditResposta({ id: r.id, corpo: r.corpo })}>Editar</button>
                      <button type="button" className="danger" onClick={() => handleDeleteResposta(r.id)}>Excluir</button>
                    </>
                  )}
                </div>
              </div>
            </div>
          </li>
        ))}
      </ul>

      {editResposta && (
        <form className="card form overlay" onSubmit={handleUpdateResposta}>
          <h2>Editar resposta</h2>
          <textarea value={editResposta.corpo} onChange={(e) => setEditResposta({ ...editResposta, corpo: e.target.value })} required />
          <div className="actions">
            <button type="submit">Salvar</button>
            <button type="button" onClick={() => setEditResposta(null)}>Cancelar</button>
          </div>
        </form>
      )}
    </Layout>
  );
}
