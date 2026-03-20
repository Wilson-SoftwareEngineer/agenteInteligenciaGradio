# Agente de Inteligência Investigativa

Sistema RAG (Retrieval-Augmented Generation) com interface web para consulta de relatórios investigativos. Combina busca vetorial semântica no banco Qdrant com geração de respostas estruturadas pelo modelo GPT-4.1 da OpenAI.

---

## Funcionalidades

- **Chat Investigativo** — perguntas em linguagem natural com resposta em streaming
- **Consulta Avançada** — busca estruturada por CPF, Nome, Vulgo e Endereço com síntese LLM
- **Upload de Documentos** — ingestão de arquivos PDF e DOCX com OCR em imagens embutidas
- **Status do Sistema** — monitoramento em tempo real do banco vetorial e do modelo LLM

---

## Arquitetura

```
Interface Web (Gradio — porta 7860)
        │
        ▼
   rag_core.py
   ┌──────────────────────────────────┐
   │  search()  busca_avancada()      │
   │  chat_stream()  ingerir_doc()    │
   └───────────┬──────────────────────┘
               │
       ┌───────┴────────┐
       ▼                ▼
  Qdrant (Docker)   OpenAI GPT-4.1
  porta 6334        API com streaming
       │
       ▼
  HuggingFace Embeddings
  paraphrase-multilingual-MiniLM-L12-v2
  384 dimensões — CPU — multilíngue
```

---

## Requisitos

### Sistema
- Python 3.12+
- Docker
- tesseract-ocr (para OCR em imagens de DOCX)

```bash
sudo apt install tesseract-ocr tesseract-ocr-por
```

### Hardware mínimo
| Recurso | Mínimo |
|---|---|
| RAM | 4 GB livres |
| Disco | 2 GB (modelo ~500 MB + banco) |
| CPU | 2 núcleos |

---

## Instalação

```bash
# 1. Clonar o repositório
git clone https://github.com/Wilson-SoftwareEngineer/agenteInteligenciaGradio.git
cd agenteInteligenciaGradio

# 2. Criar e ativar o ambiente virtual
python3.12 -m venv venv
source venv/bin/activate

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Configurar variáveis de ambiente
cp .env.example .env
# Edite o .env com suas credenciais
```

---

## Configuração — `.env`

Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:

```env
OPENAI_API_KEY=sua-chave-aqui
OPENAI_MODEL=gpt-4.1
QDRANT_HOST=localhost
QDRANT_PORT=6334
COLLECTION_NAME=relatorios
GRADIO_USER=seu-usuario
GRADIO_PASS=sua-senha
EMBEDDINGS_PATH=/caminho/para/modelo_embeddings
```

| Variável | Descrição | Padrão |
|---|---|---|
| `OPENAI_API_KEY` | Chave da API OpenAI | **obrigatório** |
| `OPENAI_MODEL` | Modelo LLM | `gpt-4o` |
| `QDRANT_HOST` | Host do Qdrant | `localhost` |
| `QDRANT_PORT` | Porta do Qdrant | `6334` |
| `COLLECTION_NAME` | Nome da coleção | `relatorios` |
| `GRADIO_USER` | Usuário de acesso à interface | `admin` |
| `GRADIO_PASS` | Senha de acesso à interface | `admin` |
| `EMBEDDINGS_PATH` | Caminho do modelo local | `./modelo_embeddings` |

---

## Inicialização

```bash
bash start.sh
```

O script executa automaticamente:
1. Verifica se o container Qdrant já está rodando
2. Sobe o container Docker caso necessário, montando o volume de persistência
3. Aguarda o Qdrant ficar disponível (timeout: 30s)
4. Ativa o `venv` e inicia a interface em `http://localhost:7860`

---

## Como usar

### Chat Investigativo
Digite perguntas em linguagem natural sobre os relatórios indexados.

```
Fale sobre o indivíduo João da Silva.
Quem são os comparsas de vulgo Ciclone?
Quais relatórios mencionam o CPF 000.000.000-00?
```

A resposta é gerada em streaming no formato:

```
📌 RESUMO DE INTELIGÊNCIA
─────────────────────────
👤 ALVO: NOME COMPLETO
🆔 CPF: 000.000.000-00
🪪 RG: 0000000
🎂 NASCIMENTO: dd/mm/aaaa
👩 MÃE: Nome da mãe
🏠 ENDEREÇO: Rua, bairro, cidade
📞 TELEFONE: (00) 00000-0000
🚗 VÍNCULOS: comparsas, placas

📂 HISTÓRICO OPERACIONAL:
• Fato 1 — Fonte: relatório.docx, pág. 3
• Fato 2 — Fonte: relatório.pdf, pág. 7

⚠️ NOTAS OPERACIONAIS: análise consolidada
─────────────────────────
Fonte: Base Integrada de Relatórios
```

### Consulta Avançada
Preencha um ou mais campos (CPF, Nome, Vulgo, Endereço) e clique em **Buscar**.
O sistema recupera todos os trechos relevantes e sintetiza um Relatório de Inteligência completo.

> **CPF** é buscado com filtro exato (com e sem formatação) antes da busca vetorial — máxima precisão.

### Upload de Documentos
1. Selecione arquivos `.pdf` ou `.docx`
2. Clique em **Processar e Indexar**
3. Acompanhe o log de processamento

**Pipeline de ingestão:**
```
PDF  → pypdf extrai texto por página
DOCX → python-docx + OCR (pytesseract) em imagens embutidas
     ↓
RecursiveCharacterTextSplitter (chunk: 1200 / overlap: 200)
     ↓
HuggingFace embed_query() → vetor de 384 dimensões
     ↓
Qdrant upsert() em batches de 50 — IDs determinísticos (sem duplicatas)
```

### Status do Sistema
Exibe em tempo real: status do Qdrant, total de chunks indexados, dimensões do vetor, coleção ativa, modelo LLM e porta de conexão.

---

## Estrutura do Projeto

```
agenteInteligenciaGradio/
├── app.py              # Interface web Gradio (4 abas + tema visual)
├── rag_core.py         # Motor RAG: busca, LLM, ingestão de documentos
├── requirements.txt    # Dependências Python
├── start.sh            # Script de inicialização (Docker + venv + Gradio)
├── .gitignore          # Arquivos excluídos do versionamento
└── README.md           # Esta documentação
```

> Não versionados (via `.gitignore`): `.env`, `venv/`, `qdrant_storage/`, `modelo_embeddings/`

---

## Busca Híbrida

O sistema combina dois métodos para maximizar cobertura e precisão:

| Método | Mecanismo | Resultado |
|---|---|---|
| **Keyword** | Scroll com `MatchText` no Qdrant | Termos exatos nos documentos |
| **Vetorial** | `similarity_search_with_score` — COSINE | Similaridade semântica |

Resultados são deduplificados por conteúdo. O LLM recebe até 40 chunks únicos por consulta.

---

## Dependências

```
gradio>=4.0                   Interface web
qdrant-client>=1.7.0          Cliente banco vetorial
langchain>=0.2.0              Orquestração LLM
langchain-openai>=0.1.0       Integração OpenAI
langchain-community>=0.2.0    Componentes LangChain
langchain-text-splitters       Chunking de texto
openai>=1.0.0                 SDK OpenAI
sentence-transformers>=2.2.0  Modelo de embeddings
pypdf>=3.0.0                  Leitura de PDFs
python-docx>=1.1.0            Leitura de DOCX
pytesseract>=0.3.10           OCR em imagens
Pillow>=10.0.0                Manipulação de imagens
python-dotenv>=1.0.0          Variáveis de ambiente
pandas>=2.0.0                 Manipulação de dados
```

---

## Segurança

- Acesso protegido por autenticação HTTP Basic (usuário/senha via `.env`)
- Credenciais nunca hardcoded no código
- `.env` excluído do Git via `.gitignore`
- Para produção: alterar `share=False` e `server_name="127.0.0.1"` no `demo.launch()`

---

## Deploy em Produção (Hostinger VPS)

Requer **VPS KVM 2+** (8 GB RAM, 4 vCPU).

```bash
# Instalar Nginx e Certbot
apt install nginx certbot python3-certbot-nginx

# Criar serviço systemd
# /etc/systemd/system/agente.service
systemctl enable agente && systemctl start agente

# Configurar reverse proxy Nginx (porta 7860 → 443)
# Emitir certificado SSL
certbot --nginx -d seudominio.com.br
```

Arquitetura de produção:
```
Internet → Nginx (443 HTTPS + SSL) → Gradio (:7860) → Qdrant (Docker)
```

---

## Licença

Uso interno. Todos os direitos reservados.
