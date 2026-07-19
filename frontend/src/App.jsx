import { BrowserRouter, Route, Routes } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import AdminPage from './pages/AdminPage';
import BuscaPage from './pages/BuscaPage';
import ComunidadePage from './pages/ComunidadePage';
import Home from './pages/Home';
import Login from './pages/Login';
import PerfilPage from './pages/PerfilPage';
import Register from './pages/Register';
import TopicoPage from './pages/TopicoPage';

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/comunidades/:slug" element={<ComunidadePage />} />
          <Route path="/topicos/:id" element={<TopicoPage />} />
          <Route path="/admin" element={<AdminPage />} />
          <Route path="/perfil/:id" element={<PerfilPage />} />
          <Route path="/busca" element={<BuscaPage />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
