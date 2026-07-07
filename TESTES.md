# Documentação de Testes — Fórum de Comunidades

Este documento registra a rodada de testes realizada na aplicação, o que foi validado e como reproduzir os testes.

**Data da execução:** 2026-07-03  
**Ambiente:** Docker Compose (`docker compose up --build`)  
**Resultado:** 26 testes passaram, 0 falharam

---

## Como executar os testes

Com a aplicação rodando:

```bash
docker compose up -d
# Aguarde o backend subir (migrations + seed levam ~15–20s)
./scripts/run_tests.sh
```

O script aguarda automaticamente o backend ficar pronto antes de executar os testes.

---

## 1. Infraestrutura e Docker

| Teste | Método | Endpoint | Resultado esperado | Como foi validado |
|-------|--------|----------|-------------------|-------------------|
| Backend saudável | GET | `/api/health` | HTTP 200, `{"status":"ok"}` | Resposta 200 confirmada |
| Frontend acessível | GET | `http://localhost:3000/` | HTTP 200 | Página React servida pelo Nginx |
| Proxy Nginx → API | GET | `http://localhost:3000/api/health` | HTTP 200 | Proxy encaminha `/api` ao backend |
| Proxy retorna JSON | GET | `http://localhost:3000/api/comunidades` | JSON com comunidades | Corpo contém dados do seed |

**Validação adicional manual:**
- `docker compose ps` — containers `db`, `backend` e `frontend` em estado `Up`
- Logs do backend confirmam: migrations Alembic, seed do admin e startup do Uvicorn

---

## 2. Visitante (sem autenticação)

Visitante **não é entidade no banco** — representa acesso sem token JWT.

| Teste | Método | Endpoint | Resultado esperado | Como foi validado |
|-------|--------|----------|-------------------|-------------------|
| Listar comunidades | GET | `/api/comunidades` | HTTP 200 | Visitante lê conteúdo público |
| Listar tópicos | GET | `/api/comunidades/1/topicos` | HTTP 200 | Feed público acessível |
| Criar comunidade sem login | POST | `/api/comunidades` | HTTP 401 | Escrita bloqueada |
| Criar tópico sem login | POST | `/api/comunidades/1/topicos` | HTTP 401 | Escrita bloqueada |

**Critério de aceite:** Visitante navega e lê, mas não consegue publicar conteúdo.

---

## 3. Autenticação

| Teste | Método | Endpoint | Resultado esperado | Como foi validado |
|-------|--------|----------|-------------------|-------------------|
| Registro | POST | `/api/auth/register` | HTTP 201 | Novo usuário criado |
| Role padrão | — | corpo do registro | `"role": "MEMBRO"` | Visitante vira Membro automaticamente |
| Login | POST | `/api/auth/login` | HTTP 200 + JWT | Token `access_token` retornado |
| Perfil autenticado | GET | `/api/auth/me` | HTTP 200 | Token válido retorna dados do usuário |
| Login inválido | POST | `/api/auth/login` | HTTP 401 | Credenciais erradas rejeitadas |

**Credenciais de teste (seed):**
- Admin: `admin@forum.com` / `admin123`
- Membro: criado via registro durante os testes

---

## 4. Membro — CRUD restrito

Membro autenticado pode criar conteúdo, mas só edita/exclui **o que criou**.

| Teste | Método | Endpoint | Resultado esperado | Como foi validado |
|-------|--------|----------|-------------------|-------------------|
| Criar comunidade | POST | `/api/comunidades` | HTTP 201 | Membro cria nova comunidade |
| Criar tópico | POST | `/api/comunidades/{id}/topicos` | HTTP 201 | Publicação permitida |
| Editar próprio tópico | PUT | `/api/topicos/{id}` | HTTP 200 | Autor pode atualizar |
| Criar resposta | POST | `/api/topicos/{id}/respostas` | HTTP 201 | Comentário permitido |
| Excluir tópico alheio | DELETE | `/api/topicos/1` | HTTP 403 | Tópico do admin protegido |
| Excluir comunidade | DELETE | `/api/comunidades/1` | HTTP 403 | Somente Admin pode excluir |
| Entrar na comunidade | POST | `/api/comunidades/1/entrar` | HTTP 201 | Associação N-N criada |

**Critério de aceite:** Membro opera CRUD no próprio conteúdo; recebe 403 ao tentar modificar conteúdo de outro usuário.

---

## 5. Admin — CRUD global

| Teste | Método | Endpoint | Resultado esperado | Como foi validado |
|-------|--------|----------|-------------------|-------------------|
| Listar usuários | GET | `/api/admin/usuarios` | HTTP 200 | Painel admin acessível |
| Acesso negado a Membro | GET | `/api/admin/usuarios` | HTTP 403 | Membro não acessa rotas admin |
| Fixar tópico | PATCH | `/api/topicos/{id}/fixar` | HTTP 200 | Campo `fixado` alterado |
| Excluir resposta alheia | DELETE | `/api/respostas/{id}` | HTTP 204 | Admin remove qualquer conteúdo |
| Excluir tópico alheio | DELETE | `/api/topicos/{id}` | HTTP 204 | Moderação global funciona |

**Critério de aceite:** Admin exclui qualquer conteúdo, fixa tópicos e acessa rotas exclusivas.

---

## 6. Checklist — Requisitos da atividade

| Requisito | Status | Evidência |
|-----------|--------|-----------|
| Usa banco de dados | OK | PostgreSQL 16 no Docker; migrations Alembic aplicadas |
| Entidade Usuário no banco | OK | Tabela `usuarios`; CRUD via auth e admin |
| Mais de um tipo de usuário com acessos diferentes | OK | Visitante (leitura), Membro (CRUD restrito), Admin (CRUD global) |
| Acesso primário via Web | OK | React em `localhost:3000`; proxy `/api` funcional |
| Dockerfile para container | OK | `backend/Dockerfile`, `frontend/Dockerfile`, `docker-compose.yml` |

---

## 7. Matriz de permissões validada

| Ação | Visitante | Membro | Admin |
|------|-----------|--------|-------|
| Ler comunidades/tópicos | 200 | 200 | 200 |
| Criar comunidade/tópico/resposta | 401 | 201 | 201 |
| Editar/excluir próprio conteúdo | 401 | 200/204 | 200/204 |
| Editar/excluir conteúdo alheio | 401 | 403 | 200/204 |
| Excluir comunidade | 401 | 403 | 204 |
| Painel admin | 401 | 403 | 200 |
| Fixar tópico | 401 | 403 | 200 |

---

## 8. Testes manuais recomendados (UI)

Além dos testes automatizados da API, validar no navegador:

1. **Visitante:** abrir `http://localhost:3000`, ver comunidades e tópicos; confirmar ausência de formulários de criação
2. **Membro:** registrar em `/register`, criar comunidade e tópico; editar/excluir só os próprios
3. **Admin:** login com `admin@forum.com`, acessar `/admin`, promover usuário, fixar/excluir conteúdo

---

## 9. Resumo da execução

```
Passou: 26
Falhou: 0
Total:  26
```

Todos os critérios de aceite do plano de trabalho foram atendidos:

1. Visitante vê conteúdo, não publica
2. Membro CRUD restrito com 403 em conteúdo alheio
3. Admin modera globalmente
4. `docker compose up --build` sobe a stack completa

---

## Referências

- Plano de trabalho: `.cursor/plans/forum_crud_web_c720fd41.plan.md`
- Instruções de execução: [`README.md`](README.md)
- Script de testes: [`scripts/run_tests.sh`](scripts/run_tests.sh)
- API interativa: http://localhost:8000/docs
