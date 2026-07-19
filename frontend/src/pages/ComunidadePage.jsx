import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import api from '../api/client';
import Layout from '../components/Layout';
import VoteButtons from '../components/VoteButtons';
import { useAuth } from '../context/AuthContext';

export default function ComunidadePage() {
  const { slug } = useParams();
  const [comunidade, setComunidade] = useState(null);
  const [topicos, setTopicos] = useState([]);
  const [error, setError] = useState('');
  const [form, setForm] = useState({ titulo: '', corpo: '' });
  const [editForm, setEditForm] = useState(null);
  const [jaMembro, setJaMembro] = useState(false);
  const { user, isMembro, isAdmin } = useAuth();

  const load = async () => {
    try {
      const { data: com } = await api.get(`/comunidades/${slug}`);
      setComunidade(com);
      setJaMembro(com.eh_membro ?? false);
      const { data: tops } = await api.get(`/comunidades/${com.id}/topicos`);
      setTopicos(tops);
    } catch (err) {
      setError(err.response?.data?.detail || 'Erro ao carregar');
    }
  };

  useEffect(() => {
    load();
  }, [slug]);

  const handleCreateTopico = async (e) => {
    e.preventDefault();
    try {
      await api.post(`/comunidades/${comunidade.id}/topicos`, form);
      setForm({ titulo: '', corpo: '' });
      load();
    } catch (err) {
      setError(err.response?.data?.detail || 'Erro ao criar tópico');
    }
  };

  const handleDeleteTopico = async (id) => {
    if (!window.confirm('Excluir tópico?')) return;
    try {
      await api.delete(`/topicos/${id}`);
      load();
    } catch (err) {
      setError(err.response?.data?.detail || 'Erro ao excluir');
    }
  };

  const handleUpdateTopico = async (e) => {
    e.preventDefault();
    try {
      await api.put(`/topicos/${editForm.id}`, { titulo: editForm.titulo, corpo: editForm.corpo });
      setEditForm(null);
      load();
    } catch (err) {
      setError(err.response?.data?.detail || 'Erro ao editar');
    }
  };

  const handleEntrar = async () => {
    try {
      await api.post(`/comunidades/${comunidade.id}/entrar`);
      setJaMembro(true);
    } catch (err) {
      const detail = err.response?.data?.detail || '';
      if (typeof detail === 'string' && detail.toLowerCase().includes('já é membro')) {
        setJaMembro(true);
      } else {
        setError(detail || 'Erro ao entrar');
      }
    }
  };
  const canModify = (autorId) => isAdmin || user?.id === autorId;

  if (!comunidade && !error) return <Layout><p>Carregando...</p></Layout>;

  return (
    <Layout>
      {comunidade && (
        <>
          <Link to="/">← Voltar</Link>
          <div className="comunidade-header">
            <h1>{comunidade.nome}</h1>
            <p>{comunidade.descricao}</p>
            {isMembro && (
              jaMembro
                ? <span className="badge-membro">✓ Membro</span>
                : <button type="button" className="btn-entrar" onClick={handleEntrar}>+ Entrar na comunidade</button>
            )}
          </div>
        </>
      )}

      {error && <p className="error">{typeof error === 'string' ? error : JSON.stringify(error)}</p>}

      {isMembro && comunidade && (
        <form className="card form" onSubmit={handleCreateTopico}>
          <h2>Novo tópico</h2>
          <input placeholder="Título" value={form.titulo} onChange={(e) => setForm({ ...form, titulo: e.target.value })} required />
          <textarea placeholder="Conteúdo" value={form.corpo} onChange={(e) => setForm({ ...form, corpo: e.target.value })} required />
          <button type="submit">Publicar</button>
        </form>
      )}

      <h2>Tópicos</h2>
      <ul className="list">
        {topicos.map((t) => (
          <li key={t.id} className="card">
            {t.fixado && <div className="card-flags"><span className="badge">Fixado</span></div>}
            <div className="topico-row">
              <VoteButtons alvoTipo="TOPICO" alvoId={t.id} votosIniciais={t.votos} autorId={t.autor_id} />
              <div>
                <Link to={`/topicos/${t.id}`}><strong>{t.titulo}</strong></Link>
                <p>{t.corpo.slice(0, 150)}{t.corpo.length > 150 ? '...' : ''}</p>
                <small>Por <Link to={`/perfil/${t.autor_id}`}>{t.autor_nome}</Link></small>
                {canModify(t.autor_id) && (
                  <div className="actions">
                    <button type="button" onClick={() => setEditForm({ id: t.id, titulo: t.titulo, corpo: t.corpo })}>Editar</button>
                    <button type="button" className="danger" onClick={() => handleDeleteTopico(t.id)}>Excluir</button>
                  </div>
                )}
              </div>
            </div>
          </li>
        ))}
      </ul>

      {editForm && (
        <form className="card form overlay" onSubmit={handleUpdateTopico}>
          <h2>Editar tópico</h2>
          <input value={editForm.titulo} onChange={(e) => setEditForm({ ...editForm, titulo: e.target.value })} required />
          <textarea value={editForm.corpo} onChange={(e) => setEditForm({ ...editForm, corpo: e.target.value })} required />
          <div className="actions">
            <button type="submit">Salvar</button>
            <button type="button" onClick={() => setEditForm(null)}>Cancelar</button>
          </div>
        </form>
      )}
    </Layout>
  );
}
