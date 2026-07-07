import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import Layout from '../components/Layout';
import { useAuth } from '../context/AuthContext';

export default function Register() {
  const [nome, setNome] = useState('');
  const [email, setEmail] = useState('');
  const [senha, setSenha] = useState('');
  const [error, setError] = useState('');
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      await register(nome, email, senha);
      navigate('/');
    } catch (err) {
      setError(err.response?.data?.detail || 'Erro ao registrar');
    }
  };

  return (
    <Layout>
      <form className="card form narrow" onSubmit={handleSubmit}>
        <h1>Registrar</h1>
        {error && <p className="error">{typeof error === 'string' ? error : JSON.stringify(error)}</p>}
        <input placeholder="Nome" value={nome} onChange={(e) => setNome(e.target.value)} required />
        <input type="email" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} required />
        <input type="password" placeholder="Senha" value={senha} onChange={(e) => setSenha(e.target.value)} required minLength={6} />
        <button type="submit">Criar conta</button>
        <p>
          Já tem conta? <Link to="/login">Entrar</Link>
        </p>
      </form>
    </Layout>
  );
}
