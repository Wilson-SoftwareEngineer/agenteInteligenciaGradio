import os
import gradio as gr
from dotenv import load_dotenv
import rag_core

# ── Tema e CSS ────────────────────────────────────────────────────────────────

THEME = gr.themes.Base(
    primary_hue=gr.themes.colors.orange,
    secondary_hue=gr.themes.colors.slate,
    neutral_hue=gr.themes.colors.slate,
    font=[gr.themes.GoogleFont("Inter"), "ui-sans-serif", "sans-serif"],
    font_mono=[gr.themes.GoogleFont("JetBrains Mono"), "ui-monospace", "monospace"],
).set(
    # Fundo geral
    body_background_fill="#0f172a",
    body_background_fill_dark="#0f172a",
    body_text_color="#e2e8f0",
    body_text_color_dark="#e2e8f0",
    body_text_size="15px",

    # Blocos / painéis
    block_background_fill="#1e293b",
    block_background_fill_dark="#1e293b",
    block_border_color="#334155",
    block_border_width="1px",
    block_label_text_color="#94a3b8",
    block_label_text_color_dark="#94a3b8",
    block_label_background_fill="#1e293b",
    block_label_background_fill_dark="#1e293b",
    block_title_text_color="#cbd5e1",
    block_title_text_color_dark="#cbd5e1",
    block_radius="10px",
    block_shadow="0 4px 24px 0 rgba(0,0,0,0.4)",

    # Inputs
    input_background_fill="#0f172a",
    input_background_fill_dark="#0f172a",
    input_border_color="#334155",
    input_border_color_dark="#334155",
    input_border_color_focus="#0ee2f1",
    input_border_color_focus_dark="#0ee2f1",
    input_placeholder_color="#475569",
    input_placeholder_color_dark="#475569",

    # Botão primário
    button_primary_background_fill="#0ee2f1",
    button_primary_background_fill_dark="#0ee2f1",
    button_primary_background_fill_hover="#09c4d4",
    button_primary_background_fill_hover_dark="#09c4d4",
    button_primary_text_color="#0a2a2e",
    button_primary_text_color_dark="#0a2a2e",
    button_primary_border_color="#0ee2f1",
    button_primary_border_color_dark="#0ee2f1",

    # Botão secundário
    button_secondary_background_fill="#1e293b",
    button_secondary_background_fill_dark="#1e293b",
    button_secondary_background_fill_hover="#334155",
    button_secondary_background_fill_hover_dark="#334155",
    button_secondary_text_color="#94a3b8",
    button_secondary_text_color_dark="#94a3b8",
    button_secondary_border_color="#334155",
    button_secondary_border_color_dark="#334155",

    # Bordas e raios gerais
    border_color_primary="#334155",
    border_color_primary_dark="#334155",
    button_large_radius="8px",
    button_large_padding="12px 24px",
)

CSS = """
/* Container principal */
.gradio-container {
    max-width: 1400px !important;
    margin: 0 auto !important;
}

/* Header / título */
.gradio-container > .main > .wrap > .markdown h1 {
    color: #f1f5f9 !important;
    font-weight: 700 !important;
    font-size: 1.6rem !important;
    letter-spacing: -0.02em;
}
.gradio-container > .main > .wrap > .markdown p,
.gradio-container > .main > .wrap > .markdown strong {
    color: #0ee2f1 !important;
    font-size: 0.9rem !important;
}

/* Abas */
.tabs > .tab-nav {
    background-color: #1e293b !important;
    border-bottom: 1px solid #334155 !important;
    border-radius: 10px 10px 0 0 !important;
    padding: 0 8px !important;
}
.tabs > .tab-nav > button {
    color: #64748b !important;
    font-weight: 500 !important;
    padding: 12px 20px !important;
    border-bottom: 2px solid transparent !important;
    transition: all 0.2s ease !important;
}
.tabs > .tab-nav > button:hover {
    color: #cbd5e1 !important;
}
.tabs > .tab-nav > button.selected {
    color: #0ee2f1 !important;
    border-bottom: 2px solid #0ee2f1 !important;
    background: transparent !important;
}

/* Scrollbar */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #1e293b; }
::-webkit-scrollbar-thumb { background: #475569; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #64748b; }

/* Chatbot bolhas */
.message.user { background-color: #1d4ed8 !important; color: #fff !important; }
.message.bot  { background-color: #1e293b !important; color: #e2e8f0 !important; border: 1px solid #334155 !important; }

/* Ocultar footer Gradio */
footer { display: none !important; }
"""

load_dotenv()

GRADIO_USER = os.getenv("GRADIO_USER", "admin")
GRADIO_PASS = os.getenv("GRADIO_PASS", "admin")


# ── Aba 1: Chat ───────────────────────────────────────────────────────────────

def enviar(pergunta, historico):
    if not pergunta.strip():
        yield historico, ""
        return
    historico = historico or []
    historico = historico + [
        {"role": "user",      "content": pergunta},
        {"role": "assistant", "content": ""},
    ]
    for chunk in rag_core.chat_stream(pergunta, historico):
        historico[-1]["content"] = chunk
        yield historico, ""


def limpar_chat():
    return [], ""


# ── Aba 2: Consulta avançada ──────────────────────────────────────────────────

def consulta_avancada_stream(cpf, nome, vulgo, endereco):
    cpf      = cpf.strip()
    nome     = nome.strip()
    vulgo    = vulgo.strip()
    endereco = endereco.strip()
    if not any([cpf, nome, vulgo, endereco]):
        yield "Preencha ao menos um campo para iniciar a busca."
        return
    for parcial in rag_core.consulta_avancada_stream(
        cpf=cpf, nome=nome, vulgo=vulgo, endereco=endereco
    ):
        yield parcial


def limpar_consulta():
    return "", "", "", "", ""


# ── Aba 3: Upload de PDFs ─────────────────────────────────────────────────────

def processar_pdfs(arquivos, progress=gr.Progress()):
    if not arquivos:
        return "Nenhum arquivo selecionado."
    resultados = []
    total = len(arquivos)
    for i, arquivo in enumerate(arquivos):
        progress(i / total, desc=f"Processando ({i+1}/{total})")
        if isinstance(arquivo, str):
            caminho = arquivo
        elif hasattr(arquivo, "path"):    # Gradio 4.x
            caminho = arquivo.path
        else:                             # fallback legado
            caminho = arquivo.name
        resultado = rag_core.ingerir_documento(caminho)
        if resultado["sucesso"]:
            resultados.append(
                f"OK  {resultado['arquivo']} — "
                f"{resultado['paginas']} págs, {resultado['chunks']} chunks."
            )
        else:
            resultados.append(f"ERRO  {os.path.basename(caminho)} — {resultado['mensagem']}")
    progress(1.0, desc="Concluído")
    return "\n".join(resultados)


# ── Aba 4: Status ─────────────────────────────────────────────────────────────

def carregar_status():
    s = rag_core.get_status()
    if s["status"] == "online":
        return (
            "Online",
            str(s["documentos"]),
            str(s["dimensoes"]),
            s["colecao"],
            s["modelo_llm"],
            str(s["porta_qdrant"]),
        )
    return "Offline — " + s.get("mensagem", ""), "-", "-", "-", "-", "-"


# ── Layout ────────────────────────────────────────────────────────────────────

with gr.Blocks(title="Agente de I", theme=THEME, css=CSS) as demo:

    gr.Markdown("# Agente de Inteligência Investigativa\n**Sistema RAG** | Qdrant + GPT-4.1, by wilsondev")

    with gr.Tabs():

        # ── Aba 1 ─────────────────────────────────────────────────────────────
        with gr.Tab("Chat Investigativo"):
            gr.Markdown("Faça perguntas sobre os relatórios. O agente busca documentos relevantes e responde com base neles.")
            chatbot = gr.Chatbot(
                height=500,
                placeholder="Pesquise o termo desejado abaixo...",
                layout="bubble",
                buttons=["copy"],
                show_label=False,
            )
            txt_msg = gr.Textbox(
                placeholder="Ex: Fale sobre o indivíduo Fulano de Tal.",
                lines=2,
                label="Pergunta",
            )
            with gr.Row():
                btn_enviar  = gr.Button("Enviar",          variant="primary",   scale=3)
                btn_limpar1 = gr.Button("Limpar conversa", variant="secondary", scale=1)

            btn_enviar.click(
                fn=enviar,
                inputs=[txt_msg, chatbot],
                outputs=[chatbot, txt_msg],
            )
            txt_msg.submit(
                fn=enviar,
                inputs=[txt_msg, chatbot],
                outputs=[chatbot, txt_msg],
            )
            btn_limpar1.click(fn=limpar_chat, outputs=[chatbot, txt_msg])

        # ── Aba 2 ─────────────────────────────────────────────────────────────
        with gr.Tab("Consulta Avançada"):
            gr.Markdown("Busca por campos específicos. O sistema recupera os documentos e gera um relatório de inteligência estruturado.")
            with gr.Row():
                inp_cpf      = gr.Textbox(label="CPF",      placeholder="000.000.000-00", scale=2)
                inp_nome     = gr.Textbox(label="Nome",     placeholder="Nome completo",  scale=3)
                inp_vulgo    = gr.Textbox(label="Vulgo",    placeholder="Apelido",        scale=2)
                inp_endereco = gr.Textbox(label="Endereço", placeholder="Rua, bairro...", scale=3)
            with gr.Row():
                btn_buscar = gr.Button("Buscar", variant="primary",   scale=3)
                btn_limpar = gr.Button("Limpar", variant="secondary", scale=1)
            out_relatorio = gr.Textbox(
                label="Relatório de Inteligência",
                interactive=False,
                lines=25,
            )
            btn_buscar.click(
                fn=consulta_avancada_stream,
                inputs=[inp_cpf, inp_nome, inp_vulgo, inp_endereco],
                outputs=[out_relatorio],
            )
            btn_limpar.click(
                fn=limpar_consulta,
                outputs=[inp_cpf, inp_nome, inp_vulgo, inp_endereco, out_relatorio],
            )

        # ── Aba 3 ─────────────────────────────────────────────────────────────
        with gr.Tab("Upload de PDFs"):
            gr.Markdown("Adicione novos relatórios à base. Os PDFs serão processados e indexados automaticamente.")
            inp_arquivos  = gr.File(
                label="Selecione os PDFs",
                file_count="multiple",
                file_types=[".pdf", ".docx"],
            )
            btn_processar = gr.Button("Processar e Indexar", variant="primary")
            out_log       = gr.Textbox(label="Log de processamento", lines=8, interactive=False)
            btn_processar.click(
                fn=processar_pdfs,
                inputs=[inp_arquivos],
                outputs=[out_log],
            )

        # ── Aba 4 ─────────────────────────────────────────────────────────────
        with gr.Tab("Status do Sistema"):
            gr.Markdown("Informações sobre o banco vetorial e o modelo em uso.")
            with gr.Row():
                out_status = gr.Textbox(label="Qdrant",      interactive=False, scale=1)
                out_docs   = gr.Textbox(label="Documentos",  interactive=False, scale=1)
                out_dim    = gr.Textbox(label="Dimensões",   interactive=False, scale=1)
            with gr.Row():
                out_col   = gr.Textbox(label="Coleção",      interactive=False, scale=2)
                out_llm   = gr.Textbox(label="Modelo LLM",   interactive=False, scale=2)
                out_porta = gr.Textbox(label="Porta Qdrant", interactive=False, scale=1)
            btn_refresh = gr.Button("Atualizar status", variant="secondary")
            btn_refresh.click(
                fn=carregar_status,
                outputs=[out_status, out_docs, out_dim, out_col, out_llm, out_porta],
            )
            demo.load(
                fn=carregar_status,
                outputs=[out_status, out_docs, out_dim, out_col, out_llm, out_porta],
            )


# ── Inicialização ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        auth=(GRADIO_USER, GRADIO_PASS),
        show_error=True,
        share=True,
    )