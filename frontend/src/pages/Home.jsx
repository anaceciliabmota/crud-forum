import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import api from '../api/client';
import Layout from '../components/Layout';
import { useAuth } from '../context/AuthContext';

export default function Home() {
  const [comunidades, setComunidades] = useState([]);
  const [error, setError] = useState('');
  const [form, setForm] = useState({ nome: '', descricao: '' });
  const { isMembro } = useAuth();

  const load = async () => {
    try {
      const { data } = await api.get('/comunidades');
      setComunidades(data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Erro ao carregar comunidades');
    }
  };

  useEffect(() => {
    load();
  }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    try {
      await api.post('/comunidades', form);
      setForm({ nome: '', descricao: '' });
      load();
    } catch (err) {
      setError(err.response?.data?.detail || 'Erro ao criar comunidade');
    }
  };

  return (
    <Layout>
      <h1>Comunidades</h1>
      {error && <p className="error">{typeof error === 'string' ? error : JSON.stringify(error)}</p>}

      {isMembro && (
        <form className="card form" onSubmit={handleCreate}>
          <h2>Criar comunidade</h2>
          <input
            placeholder="Nome"
            value={form.nome}
            onChange={(e) => setForm({ ...form, nome: e.target.value })}
            required
          />
          <textarea
            placeholder="Descrição"
            value={form.descricao}
            onChange={(e) => setForm({ ...form, descricao: e.target.value })}
          />
          <button type="submit">Criar</button>
        </form>
      )}

      {!isMembro && (
        <p className="hint">Visitante: você pode navegar, mas precisa fazer login para criar conteúdo.</p>
      )}

      <ul className="list">
        {comunidades.map((c) => (
          <li key={c.id} className="card">
            <Link to={`/comunidades/${c.slug}`}>
              <strong>{c.nome}</strong>
            </Link>
            <p>{c.descricao}</p>
            <small>Criada por {c.criador_nome}</small>
          </li>
        ))}
      </ul>
    </Layout>
  );
}
