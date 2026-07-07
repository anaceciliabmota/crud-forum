# Relatório de uso de LLM no projeto — Fórum de Comunidades

## Modelo e ferramenta

A conversa foi feita no **Cursor**, com o assistente **Composer** (modelo de linguagem integrado ao editor). O fluxo combinou modo de perguntas/planejamento (Ask/Plan) com modo de implementação (Agent), onde a LLM pôde ler o workspace, propor arquitetura e, depois, gerar código e rodar comandos.

---

## Como a conversa aconteceu

### 1. Definição do domínio (maior parte da conversa)

A conversa começou bem aberta: foi pedido ideias para uma aplicação CRUD no domínio de **redes sociais**. A LLM listou várias opções (microblog, fotos, LinkedIn lite, fórum, eventos, reviews, nichos) com entidades e operações CRUD de cada uma.

A escolha foi **fórum e comunidade**. Em seguida veio uma segunda rodada só de **exploração do produto**: Reddit lite, fórum clássico, fórum de turma, Q&A estilo Stack Overflow, comunidades de nicho etc. — sempre com exemplos concretos de entidades, fluxos e cenários de uso.

Ou seja, **a maior parte do tempo foi desenhando o que a aplicação seria**, não escrevendo código.

### 2. Papéis de usuário

Depois entrou a necessidade de **mais de um tipo de usuário**. A LLM sugeriu quatro papéis (Visitante, Membro, Moderador, Admin) com matriz de permissões. A decisão final simplificou para **Visitante, Membro e Admin** — e a conversa fechou esse modelo antes de qualquer implementação.

### 3. Plano de trabalho

Só então entraram os **requisitos formais da atividade** (banco, entidade Usuário, tipos de usuário, acesso web, Dockerfile). A stack escolhida foi **FastAPI + React + PostgreSQL**, com API + interface básica. A LLM montou o plano completo: arquitetura, modelo de dados, endpoints, fases e checklist.

**Até aqui, praticamente 100% definição de produto e arquitetura.**

### 4. Desenvolvimento (parte menor, mais concentrada)

Com o plano aprovado, a implementação foi feita em sequência: backend, frontend, Docker, seed, README. Foi a fase mais “mão na massa”, mas **ocupou menos turnos** do que a definição.

### 5. Validação e dúvidas operacionais

Por fim: rodada de testes, documentação em `TESTES.md`, script `run_tests.sh`, e dúvidas sobre:

- saída incompleta dos testes (backend ainda subindo);
- `docker compose up -d` “não rodar nada” no terminal (comportamento normal em background).

---

## Papel da LLM em cada fase

| Fase | Papel da LLM |
|------|----------------|
| Ideação | Sugerir domínios e comparar complexidade |
| Refinamento | Detalhar fórum/comunidade com exemplos e CRUD |
| Requisitos | Traduzir regras da atividade em arquitetura |
| Papéis de usuário | Propor e simplificar Visitante / Membro / Admin |
| Plano | Estruturar stack, entidades, Docker, cronograma |
| Implementação | Gerar código, containers e documentação |
| Testes | Executar validações e registrar em relatório |

---

## Conclusão

Faz sentido enfatizar que **a conversa foi majoritariamente de definição da aplicação**: o que construir, para quem, com quais entidades e permissões, e qual stack usar. O desenvolvimento em si veio **depois**, como execução de um plano já acordado — o que reduziu idas e vindas durante a codificação.

A LLM funcionou mais como **parceira de product/design** nas primeiras etapas e como **implementadora** na fase final, com as decisões principais tomadas pelo usuário (fórum vs. outras redes, três papéis de usuário, FastAPI + React).

---

*Relatório baseado no histórico da conversa no Cursor (julho/2026).*
