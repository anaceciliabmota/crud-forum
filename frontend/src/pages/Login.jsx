import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import Layout from '../components/Layout';
import { useAuth } from '../context/AuthContext';

export default function Login() {
  const [email, setEmail] = useState('');
  const [senha, setSenha] = useState('');
  const [error, setError] = useState('');
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      await login(email, senha);
      navigate('/');
    } catch (err) {
      setError(err.response?.data?.detail || 'Erro ao entrar');
    }
  };

  return (
    <Layout>
      <form className="card form narrow" onSubmit={handleSubmit}>
        <h1>Entrar</h1>
        {error && <p className="error">{error}</p>}
        <input type="email" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} required />
        <input type="password" placeholder="Senha" value={senha} onChange={(e) => setSenha(e.target.value)} required />
        <button type="submit">Entrar</button>
        <p>
          Não tem conta? <Link to="/register">Registrar</Link>
        </p>
      </form>
    </Layout>
  );
}
