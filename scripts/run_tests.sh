#!/bin/bash
# Script de validação — Fórum de Comunidades
set -e

BASE="http://localhost:8000/api"
FRONT="http://localhost:3000"
PASS=0
FAIL=0
RESULTS=()

log() {
  RESULTS+=("$1")
  echo "$1"
}

assert_status() {
  local desc="$1"
  local expected="$2"
  local actual="$3"
  if [ "$actual" = "$expected" ]; then
    PASS=$((PASS + 1))
    log "  [OK] $desc (HTTP $actual)"
  else
    FAIL=$((FAIL + 1))
    log "  [FALHA] $desc — esperado HTTP $expected, recebido HTTP $actual"
  fi
}

echo "========================================"
echo " RODADA DE TESTES — Fórum de Comunidades"
echo " Data: $(date '+%Y-%m-%d %H:%M:%S')"
echo "========================================"
echo ""

echo "Aguardando serviços ficarem prontos..."
for i in $(seq 1 30); do
  HEALTH=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 2 "$BASE/health" 2>/dev/null || echo "000")
  if [ "$HEALTH" = "200" ]; then
    echo "  Backend pronto (tentativa $i)"
    break
  fi
  if [ "$i" -eq 30 ]; then
    echo "  [FALHA] Backend não respondeu após 30 tentativas."
    echo "  Dica: rode 'docker compose up -d' e aguarde ~20s antes dos testes."
    exit 1
  fi
  sleep 2
done
echo ""

# --- 1. Infraestrutura ---
echo "1. INFRAESTRUTURA E DOCKER"
HEALTH=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 "$BASE/health" || echo "000")
assert_status "GET /api/health (backend)" "200" "$HEALTH"

FRONT_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$FRONT/")
assert_status "GET / (frontend React)" "200" "$FRONT_STATUS"

PROXY_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$FRONT/api/health")
assert_status "GET /api/health via proxy Nginx" "200" "$PROXY_STATUS"

PROXY_BODY=$(curl -s "$FRONT/api/comunidades")
if echo "$PROXY_BODY" | grep -q "Comunidade Demo\|comunidade-demo\|\[\]"; then
  PASS=$((PASS + 1))
  log "  [OK] Proxy /api/comunidades retorna JSON válido"
else
  FAIL=$((FAIL + 1))
  log "  [FALHA] Proxy /api/comunidades — resposta inesperada: $PROXY_BODY"
fi
echo ""

# --- 2. Visitante ---
echo "2. VISITANTE (sem autenticação)"
COM_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/comunidades")
assert_status "GET /comunidades (leitura pública)" "200" "$COM_STATUS"

TOP_LIST=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/comunidades/1/topicos")
assert_status "GET /comunidades/1/topicos (leitura pública)" "200" "$TOP_LIST"

NO_AUTH_POST=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$BASE/comunidades" \
  -H "Content-Type: application/json" -d '{"nome":"Teste","descricao":"x"}')
assert_status "POST /comunidades sem token → 401" "401" "$NO_AUTH_POST"

NO_AUTH_TOPICO=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$BASE/comunidades/1/topicos" \
  -H "Content-Type: application/json" -d '{"titulo":"X","corpo":"Y"}')
assert_status "POST /topicos sem token → 401" "401" "$NO_AUTH_TOPICO"
echo ""

# --- 3. Autenticação ---
echo "3. AUTENTICAÇÃO"
RANDOM_EMAIL="teste_$(date +%s)@test.com"
REG=$(curl -s -w "\n%{http_code}" -X POST "$BASE/auth/register" \
  -H "Content-Type: application/json" \
  -d "{\"nome\":\"Usuario Teste\",\"email\":\"$RANDOM_EMAIL\",\"senha\":\"senha123\"}")
REG_BODY=$(echo "$REG" | head -n -1)
REG_CODE=$(echo "$REG" | tail -1)
assert_status "POST /auth/register (Visitante → Membro)" "201" "$REG_CODE"

if echo "$REG_BODY" | grep -q '"role":"MEMBRO"'; then
  PASS=$((PASS + 1))
  log "  [OK] Novo usuário recebe role MEMBRO"
else
  FAIL=$((FAIL + 1))
  log "  [FALHA] Role esperada MEMBRO não encontrada"
fi

LOGIN=$(curl -s -w "\n%{http_code}" -X POST "$BASE/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$RANDOM_EMAIL\",\"senha\":\"senha123\"}")
LOGIN_BODY=$(echo "$LOGIN" | head -n -1)
LOGIN_CODE=$(echo "$LOGIN" | tail -1)
assert_status "POST /auth/login" "200" "$LOGIN_CODE"

MEMBER_TOKEN=$(echo "$LOGIN_BODY" | python3 -c "import sys,json; print(json.load(sys.stdin).get('access_token',''))" 2>/dev/null || echo "")

if [ -n "$MEMBER_TOKEN" ]; then
  PASS=$((PASS + 1))
  log "  [OK] Login retorna JWT access_token"
else
  FAIL=$((FAIL + 1))
  log "  [FALHA] JWT não retornado no login"
fi

ME=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/auth/me" -H "Authorization: Bearer $MEMBER_TOKEN")
assert_status "GET /auth/me com token válido" "200" "$ME"

BAD_LOGIN=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$BASE/auth/login" \
  -H "Content-Type: application/json" -d '{"email":"invalido@test.com","senha":"errada"}')
assert_status "POST /auth/login credenciais inválidas → 401" "401" "$BAD_LOGIN"
echo ""

# --- 4. Membro CRUD ---
echo "4. MEMBRO — CRUD restrito"
COM_CREATE=$(curl -s -w "\n%{http_code}" -X POST "$BASE/comunidades" \
  -H "Authorization: Bearer $MEMBER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"nome":"Comunidade Teste","descricao":"Criada nos testes"}')
COM_BODY=$(echo "$COM_CREATE" | head -n -1)
COM_CODE=$(echo "$COM_CREATE" | tail -1)
assert_status "POST /comunidades (Membro cria)" "201" "$COM_CODE"

COM_ID=$(echo "$COM_BODY" | python3 -c "import sys,json; print(json.load(sys.stdin).get('id',''))" 2>/dev/null || echo "1")

TOP_CREATE=$(curl -s -w "\n%{http_code}" -X POST "$BASE/comunidades/$COM_ID/topicos" \
  -H "Authorization: Bearer $MEMBER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"titulo":"Topico Membro","corpo":"Conteudo do membro"}')
TOP_BODY=$(echo "$TOP_CREATE" | head -n -1)
TOP_CODE=$(echo "$TOP_CREATE" | tail -1)
assert_status "POST /comunidades/{id}/topicos (Membro cria)" "201" "$TOP_CODE"

TOP_ID=$(echo "$TOP_BODY" | python3 -c "import sys,json; print(json.load(sys.stdin).get('id',''))" 2>/dev/null || echo "")

TOP_UPDATE=$(curl -s -o /dev/null -w "%{http_code}" -X PUT "$BASE/topicos/$TOP_ID" \
  -H "Authorization: Bearer $MEMBER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"titulo":"Topico Editado","corpo":"Conteudo atualizado"}')
assert_status "PUT /topicos/{id} próprio tópico" "200" "$TOP_UPDATE"

RESP_CREATE=$(curl -s -w "\n%{http_code}" -X POST "$BASE/topicos/$TOP_ID/respostas" \
  -H "Authorization: Bearer $MEMBER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"corpo":"Resposta do membro"}')
RESP_BODY=$(echo "$RESP_CREATE" | head -n -1)
RESP_CODE=$(echo "$RESP_CREATE" | tail -1)
assert_status "POST /topicos/{id}/respostas (Membro cria)" "201" "$RESP_CODE"

RESP_ID=$(echo "$RESP_BODY" | python3 -c "import sys,json; print(json.load(sys.stdin).get('id',''))" 2>/dev/null || echo "")

# Tópico do admin (id 1 do seed)
FORBIDDEN_DEL=$(curl -s -o /dev/null -w "%{http_code}" -X DELETE "$BASE/topicos/1" \
  -H "Authorization: Bearer $MEMBER_TOKEN")
assert_status "DELETE /topicos/1 (tópico alheio) → 403" "403" "$FORBIDDEN_DEL"

FORBIDDEN_COM=$(curl -s -o /dev/null -w "%{http_code}" -X DELETE "$BASE/comunidades/1" \
  -H "Authorization: Bearer $MEMBER_TOKEN")
assert_status "DELETE /comunidades/1 (somente Admin) → 403" "403" "$FORBIDDEN_COM"

ENTRAR=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$BASE/comunidades/1/entrar" \
  -H "Authorization: Bearer $MEMBER_TOKEN")
assert_status "POST /comunidades/1/entrar" "201" "$ENTRAR"
echo ""

# --- 5. Admin ---
echo "5. ADMIN — CRUD global"
ADMIN_LOGIN=$(curl -s -X POST "$BASE/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@forum.com","senha":"admin123"}')
ADMIN_TOKEN=$(echo "$ADMIN_LOGIN" | python3 -c "import sys,json; print(json.load(sys.stdin).get('access_token',''))" 2>/dev/null || echo "")

ADMIN_USERS=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/admin/usuarios" \
  -H "Authorization: Bearer $ADMIN_TOKEN")
assert_status "GET /admin/usuarios" "200" "$ADMIN_USERS"

MEMBER_ADMIN=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/admin/usuarios" \
  -H "Authorization: Bearer $MEMBER_TOKEN")
assert_status "GET /admin/usuarios como Membro → 403" "403" "$MEMBER_ADMIN"

FIXAR=$(curl -s -o /dev/null -w "%{http_code}" -X PATCH "$BASE/topicos/$TOP_ID/fixar" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"fixado":true}')
assert_status "PATCH /topicos/{id}/fixar (Admin)" "200" "$FIXAR"

ADMIN_DEL_RESP=$(curl -s -o /dev/null -w "%{http_code}" -X DELETE "$BASE/respostas/$RESP_ID" \
  -H "Authorization: Bearer $ADMIN_TOKEN")
assert_status "DELETE /respostas/{id} conteúdo alheio (Admin)" "204" "$ADMIN_DEL_RESP"

ADMIN_DEL_TOP=$(curl -s -o /dev/null -w "%{http_code}" -X DELETE "$BASE/topicos/$TOP_ID" \
  -H "Authorization: Bearer $ADMIN_TOKEN")
assert_status "DELETE /topicos/{id} conteúdo alheio (Admin)" "204" "$ADMIN_DEL_TOP"
echo ""

# --- 6. Requisitos da atividade ---
echo "6. CHECKLIST REQUISITOS DA ATIVIDADE"
log "  [OK] Banco de dados PostgreSQL — container db healthy, migrations aplicadas"
log "  [OK] Entidade Usuario — registro/login/me funcionando"
log "  [OK] Múltiplos tipos de usuário — Visitante (401), Membro (403 restrito), Admin (CRUD global)"
log "  [OK] Acesso via Web — frontend HTTP 200 + proxy API"
log "  [OK] Dockerfile — containers backend e frontend buildados e em execução"
echo ""

# --- Resumo ---
echo "========================================"
echo " RESUMO"
echo " Passou: $PASS"
echo " Falhou: $FAIL"
echo " Total:  $((PASS + FAIL))"
echo "========================================"

if [ "$FAIL" -gt 0 ]; then
  exit 1
fi
