# Fórum de Comunidades

Aplicação web CRUD de fórum/comunidades com **FastAPI**, **React**, **PostgreSQL** e **Docker**.

## Tipos de usuário

| Papel | Autenticação | Acesso |
|-------|--------------|--------|
| **Visitante** | Não | Leitura pública; registro |
| **Membro** | JWT | CRUD do próprio conteúdo + criar comunidades/tópicos/respostas |
| **Admin** | JWT + role | CRUD global + moderação |

> Visitante não é uma entidade no banco — representa acesso sem autenticação.

## Requisitos atendidos

- Banco de dados PostgreSQL
- Entidade `Usuario` com roles `MEMBRO` e `ADMIN`
- Múltiplos tipos de usuário com permissões diferentes
- Acesso primário via navegador (React)
- Dockerfile para backend e frontend

## Executar com Docker

```bash
cp .env.example .env
docker compose up --build
```

Acesse: **http://localhost:3000**

API docs: **http://localhost:8000/docs**

## Credenciais demo

| Tipo | Email | Senha |
|------|-------|-------|
| Admin | admin@forum.com | admin123 |

Após o primeiro start, existe a comunidade **Comunidade Demo** com um tópico fixado.

## Desenvolvimento local (sem Docker)

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL=postgresql://forum_user:forum_pass@localhost:5432/forum_db
alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Estrutura

```
ativ3/
├── docker-compose.yml
├── backend/          # FastAPI + SQLAlchemy + Alembic
└── frontend/         # React (Vite) + Nginx
```

## Funcionalidades

### Base
- Comunidades (CRUD)
- Tópicos e respostas (CRUD)
- Entrar/sair de comunidades
- Controle de acesso: Visitante / Membro / Admin

### Features v2
- **Votos up/down** — em tópicos e respostas (sem votar no próprio conteúdo)
- **Busca** — por título de tópico ou nome de comunidade (ILIKE, debounce no front)
- **Perfil de usuário** — `/perfil/:id` com tópicos e respostas publicados
- **Melhor resposta** — autor do tópico marca solução; só uma aceita por tópico

## Fluxos de demonstração

1. **Visitante:** abra http://localhost:3000, navegue comunidades e tópicos sem login; use a busca no header
2. **Membro:** registre-se, crie comunidade/tópico/resposta; vote em conteúdo alheio; marque melhor resposta no seu tópico
3. **Admin:** login com admin@forum.com; acesse `/admin` para promover usuários, fixar/excluir conteúdo

## Testes e validação

Documentação completa dos testes executados: [`TESTES.md`](TESTES.md)

Para rodar a suíte automatizada (38 testes):

```bash
./scripts/run_tests.sh
```
