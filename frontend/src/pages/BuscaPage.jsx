import { useEffect, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import api from '../api/client';
import Layout from '../components/Layout';

export default function BuscaPage() {
  const [searchParams] = useSearchParams();
  const q = searchParams.get('q') || '';
  const [resultados, setResultados] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    if (q.length < 2) return;
    api.get(`/busca?q=${encodeURIComponent(q)}`)
      .then(({ data }) => setResultados(data))
      .catch((err) => setError(err.response?.data?.detail || 'Erro na busca'));
  }, [q]);

  return (
    <Layout>
      <h1>Resultados para &ldquo;{q}&rdquo;</h1>
      {error && <p className="error">{error}</p>}
      {!resultados && q.length >= 2 && <p>Carregando...</p>}
      {q.length < 2 && <p className="hint">Digite pelo menos 2 caracteres para buscar.</p>}

      {resultados && (
        <>
          <section>
            <h2>Comunidades ({resultados.comunidades.length})</h2>
            {resultados.comunidades.length === 0
              ? <p className="hint">Nenhuma comunidade encontrada.</p>
              : (
                <ul className="list">
                  {resultados.comunidades.map((c) => (
                    <li key={c.id} className="card">
                      <Link to={`/comunidades/${c.slug}`}><strong>{c.nome}</strong></Link>
                      <p>{c.descricao}</p>
                    </li>
                  ))}
                </ul>
              )}
          </section>

          <section>
            <h2>Tópicos ({resultados.topicos.length})</h2>
            {resultados.topicos.length === 0
              ? <p className="hint">Nenhum tópico encontrado.</p>
              : (
                <ul className="list">
                  {resultados.topicos.map((t) => (
                    <li key={t.id} className="card">
                      <Link to={`/topicos/${t.id}`}><strong>{t.titulo}</strong></Link>
                      <p>{t.corpo.slice(0, 120)}{t.corpo.length > 120 ? '...' : ''}</p>
                      <small>Por <Link to={`/perfil/${t.autor_id}`}>{t.autor_nome}</Link></small>
                    </li>
                  ))}
                </ul>
              )}
          </section>
        </>
      )}
    </Layout>
  );
}
