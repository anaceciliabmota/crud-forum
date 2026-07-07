import { useEffect, useState } from 'react';
import { Navigate } from 'react-router-dom';
import api from '../api/client';
import Layout from '../components/Layout';
import { useAuth } from '../context/AuthContext';

export default function AdminPage() {
  const { isAdmin, loading } = useAuth();
  const [usuarios, setUsuarios] = useState([]);
  const [comunidades, setComunidades] = useState([]);
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');

  const load = async () => {
    try {
      const [usersRes, comRes] = await Promise.all([
        api.get('/admin/usuarios'),
        api.get('/comunidades'),
      ]);
      setUsuarios(usersRes.data);
      setComunidades(comRes.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Erro ao carregar painel admin');
    }
  };

  useEffect(() => {
    if (isAdmin) load();
  }, [isAdmin]);

  const handleRoleChange = async (usuarioId, role) => {
    try {
      await api.patch(`/admin/usuarios/${usuarioId}/role`, { role });
      setMessage('Role atualizada com sucesso');
      load();
    } catch (err) {
      setError(err.response?.data?.detail || 'Erro ao atualizar role');
    }
  };

  const handleDeleteComunidade = async (id) => {
    if (!window.confirm('Excluir comunidade?')) return;
    try {
      await api.delete(`/comunidades/${id}`);
      setMessage('Comunidade excluída');
      load();
    } catch (err) {
      setError(err.response?.data?.detail || 'Erro ao excluir comunidade');
    }
  };

  const handleFixarTopico = async (comunidadeId, topicoId, fixado) => {
    try {
      await api.patch(`/topicos/${topicoId}/fixar`, { fixado });
      setMessage(fixado ? 'Tópico fixado' : 'Tópico desfixado');
      load();
    } catch (err) {
      setError(err.response?.data?.detail || 'Erro ao fixar tópico');
    }
  };

  const [topicosPorComunidade, setTopicosPorComunidade] = useState({});

  const loadTopicos = async (comunidadeId) => {
    const { data } = await api.get(`/comunidades/${comunidadeId}/topicos`);
    setTopicosPorComunidade((prev) => ({ ...prev, [comunidadeId]: data }));
  };

  useEffect(() => {
    comunidades.forEach((c) => loadTopicos(c.id));
  }, [comunidades]);

  if (loading) return <Layout><p>Carregando...</p></Layout>;
  if (!isAdmin) return <Navigate to="/" replace />;

  return (
    <Layout>
      <h1>Painel Admin</h1>
      {error && <p className="error">{typeof error === 'string' ? error : JSON.stringify(error)}</p>}
      {message && <p className="success">{message}</p>}

      <section className="card">
        <h2>Usuários</h2>
        <table>
          <thead>
            <tr>
              <th>Nome</th>
              <th>Email</th>
              <th>Role</th>
              <th>Ação</th>
            </tr>
          </thead>
          <tbody>
            {usuarios.map((u) => (
              <tr key={u.id}>
                <td>{u.nome}</td>
                <td>{u.email}</td>
                <td>{u.role}</td>
                <td>
                  <select
                    value={u.role}
                    onChange={(e) => handleRoleChange(u.id, e.target.value)}
                  >
                    <option value="MEMBRO">MEMBRO</option>
                    <option value="ADMIN">ADMIN</option>
                  </select>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      <section className="card">
        <h2>Comunidades e moderação</h2>
        {comunidades.map((c) => (
          <div key={c.id} className="admin-block">
            <h3>{c.nome}</h3>
            <button type="button" className="danger" onClick={() => handleDeleteComunidade(c.id)}>
              Excluir comunidade
            </button>
            <ul>
              {(topicosPorComunidade[c.id] || []).map((t) => (
                <li key={t.id}>
                  {t.titulo} {t.fixado && '(fixado)'}
                  <button type="button" onClick={() => handleFixarTopico(c.id, t.id, !t.fixado)}>
                    {t.fixado ? 'Desfixar' : 'Fixar'}
                  </button>
                  <button
                    type="button"
                    className="danger"
                    onClick={async () => {
                      if (!window.confirm('Excluir tópico?')) return;
                      await api.delete(`/topicos/${t.id}`);
                      loadTopicos(c.id);
                    }}
                  >
                    Excluir tópico
                  </button>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </section>
    </Layout>
  );
}
