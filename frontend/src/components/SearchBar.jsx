import { useEffect, useRef, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import api from '../api/client';

export default function SearchBar() {
  const [query, setQuery] = useState('');
  const [resultados, setResultados] = useState(null);
  const [aberto, setAberto] = useState(false);
  const containerRef = useRef(null);
  const navigate = useNavigate();

  useEffect(() => {
    if (query.length < 2) {
      setResultados(null);
      return;
    }
    const timer = setTimeout(async () => {
      try {
        const { data } = await api.get(`/busca?q=${encodeURIComponent(query)}`);
        setResultados(data);
        setAberto(true);
      } catch {
        setResultados(null);
      }
    }, 300);
    return () => clearTimeout(timer);
  }, [query]);

  useEffect(() => {
    const handler = (e) => {
      if (containerRef.current && !containerRef.current.contains(e.target)) {
        setAberto(false);
      }
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (query.length >= 2) {
      setAberto(false);
      navigate(`/busca?q=${encodeURIComponent(query)}`);
    }
  };

  const total = resultados ? resultados.comunidades.length + resultados.topicos.length : 0;

  return (
    <div className="searchbar-wrap" ref={containerRef}>
      <form onSubmit={handleSubmit} className="searchbar-form">
        <input
          type="search"
          placeholder="Buscar..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onFocus={() => resultados && setAberto(true)}
          className="searchbar-input"
        />
      </form>

      {aberto && resultados && total > 0 && (
        <div className="searchbar-dropdown">
          {resultados.comunidades.length > 0 && (
            <div>
              <p className="dropdown-label">Comunidades</p>
              {resultados.comunidades.map((c) => (
                <Link
                  key={c.id}
                  to={`/comunidades/${c.slug}`}
                  className="dropdown-item"
                  onClick={() => setAberto(false)}
                >
                  {c.nome}
                </Link>
              ))}
            </div>
          )}
          {resultados.topicos.length > 0 && (
            <div>
              <p className="dropdown-label">Tópicos</p>
              {resultados.topicos.map((t) => (
                <Link
                  key={t.id}
                  to={`/topicos/${t.id}`}
                  className="dropdown-item"
                  onClick={() => setAberto(false)}
                >
                  {t.titulo}
                </Link>
              ))}
            </div>
          )}
          <Link
            to={`/busca?q=${encodeURIComponent(query)}`}
            className="dropdown-item dropdown-all"
            onClick={() => setAberto(false)}
          >
            Ver todos os resultados →
          </Link>
        </div>
      )}

      {aberto && resultados && total === 0 && (
        <div className="searchbar-dropdown">
          <p className="dropdown-label">Nenhum resultado encontrado.</p>
        </div>
      )}
    </div>
  );
}
