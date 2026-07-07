#!/bin/sh
set -e

echo "Aguardando banco de dados..."
until python -c "
import sys, time
from sqlalchemy import create_engine, text
import os
url = os.environ.get('DATABASE_URL')
for i in range(30):
    try:
        engine = create_engine(url)
        with engine.connect() as conn:
            conn.execute(text('SELECT 1'))
        sys.exit(0)
    except Exception:
        time.sleep(1)
sys.exit(1)
"; do
  echo "Banco indisponível, tentando novamente..."
  sleep 2
done

echo "Executando migrations..."
alembic upgrade head

echo "Executando seed..."
python -m app.seed

echo "Iniciando servidor..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
