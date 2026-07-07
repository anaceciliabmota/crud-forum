import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Layout({ children }) {
  const { user, logout, isAdmin } = useAuth();

  return (
    <div className="app">
      <header className="header">
        <Link to="/" className="logo">Fórum de Comunidades</Link>
        <nav>
          {user ? (
            <>
              <span className="user-info">Olá, {user.nome} ({user.role})</span>
              {isAdmin && <Link to="/admin">Admin</Link>}
              <button type="button" onClick={logout} className="btn-link">Sair</button>
            </>
          ) : (
            <>
              <Link to="/login">Entrar</Link>
              <Link to="/register">Registrar</Link>
            </>
          )}
        </nav>
      </header>
      <main className="main">{children}</main>
    </div>
  );
}
