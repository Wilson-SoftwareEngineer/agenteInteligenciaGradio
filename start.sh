#!/bin/bash

PROJECT_DIR="/home/kali-agent/IA_Ficco_Gradio"
PYTHON="$PROJECT_DIR/venv/bin/python"
CONTAINER_NAME="qdrant_gradio"
QDRANT_PORT=6334

echo "======================================"
echo " Agente Investigativo FICCO — Gradio"
echo "======================================"

# ── 1. Verificar se o container já está rodando ───────────────────────────────
if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "[OK] Qdrant já está rodando (${CONTAINER_NAME})"
else
    # ── 2. Se existir parado, remover para recriar limpo ─────────────────────
    if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
        echo "[INFO] Removendo container parado anterior..."
        docker rm "${CONTAINER_NAME}"
    fi

    # ── 3. Subir novo container na porta 6334 ─────────────────────────────────
    echo "[INFO] Iniciando Qdrant na porta ${QDRANT_PORT}..."
    docker run -d \
        --name "${CONTAINER_NAME}" \
        -p "${QDRANT_PORT}:6333" \
        -v "${PROJECT_DIR}/qdrant_storage:/qdrant/storage" \
        qdrant/qdrant

    # ── 4. Aguardar Qdrant ficar pronto ───────────────────────────────────────
    echo "[INFO] Aguardando Qdrant inicializar..."
    TENTATIVAS=0
    until curl -sf "http://localhost:${QDRANT_PORT}/readyz" > /dev/null 2>&1; do
        sleep 1
        TENTATIVAS=$((TENTATIVAS + 1))
        if [ $TENTATIVAS -ge 30 ]; then
            echo "[ERRO] Qdrant não respondeu após 30 segundos. Verifique o Docker."
            exit 1
        fi
    done
    echo "[OK] Qdrant pronto (${TENTATIVAS}s)"
fi

# ── 5. Ativar venv e iniciar Gradio ──────────────────────────────────────────
echo "[INFO] Iniciando interface Gradio..."
echo "[INFO] Acesse: http://localhost:7860"
echo "======================================"

cd "${PROJECT_DIR}"
source "${PROJECT_DIR}/venv/bin/activate"
"${PYTHON}" app.py