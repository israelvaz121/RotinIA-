from fastapi import FastAPI, Request, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from ia_engine import (
    gerar_resumo,
    gerar_questoes,
    gerar_resposta,
    flashcard_do_dia,
    gerar_rotina
)
import sys
import os
import io
from PyPDF2 import PdfReader

# Garante que o diretório atual esteja no sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

app = FastAPI(title="API de IA Educacional", version="1.0")

# Configuração de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, usar domínios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"mensagem": "API funcionando"}

@app.post("/upload_resumo")
async def upload_resumo(file: UploadFile = File(...)):
    try:
        if file.content_type == "application/pdf":
            contents = await file.read()
            reader = PdfReader(io.BytesIO(contents))
            texto = "".join(page.extract_text() or "" for page in reader.pages)
        else:
            texto = (await file.read()).decode("utf-8")

        resumo = gerar_resumo(texto)
        return {"resumo": resumo}
    except Exception as e:
        return {"error": f"Erro ao processar arquivo: {str(e)}"}

@app.post("/resumo")
async def resumir_conteudo(request: Request):
    try:
        data = await request.json()
        texto = data.get("texto", "").strip()
        if not texto:
            return {"error": "Campo 'texto' não pode estar vazio."}

        resumo = gerar_resumo(texto)
        return {"resumo": resumo}
    except Exception as e:
        return {"error": f"Erro ao gerar resumo: {str(e)}"}

@app.post("/questoes")
async def gerar_questoes_api(request: Request):
    try:
        data = await request.json()
        assunto = data.get("assunto", "").strip()
        if not assunto:
            return {"error": "Campo 'assunto' não pode estar vazio."}

        questoes = gerar_questoes(assunto)
        return {"questoes": questoes}
    except Exception as e:
        return {"error": f"Erro ao gerar questões: {str(e)}"}

@app.post("/rotina")
async def criar_rotina_estudo(request: Request):
    try:
        data = await request.json()
        tempo = data.get("tempo_disponivel")
        nivel = data.get("nivel", "").strip()
        objetivo = data.get("objetivo", "").strip()

        if tempo is None or not nivel or not objetivo:
            return {"error": "Parâmetros insuficientes. Envie 'tempo_disponivel', 'nivel' e 'objetivo'."}

        rotina = gerar_rotina(tempo, nivel, objetivo)
        return {"rotina": rotina} if isinstance(rotina, dict) else {"rotina_texto": rotina}
    except Exception as e:
        return {"error": f"Erro ao gerar rotina: {str(e)}"}

@app.post("/flashcards")
async def gerar_flashcards_api(request: Request):
    try:
        data = await request.json()
        conteudo = data.get("conteudo", "").strip()
        modo = data.get("modo", "auto")

        if not conteudo:
            return {"error": "Campo 'conteudo' não pode estar vazio."}

        if modo == "auto":
            resultado = flashcard_do_dia(conteudo)
            return {"flashcards": [resultado]} if isinstance(resultado, dict) else {"error": resultado}
        else:
            flashcards = data.get("flashcards", [])
            return {"flashcards": flashcards}
    except Exception as e:
        return {"error": f"Erro ao gerar flashcards: {str(e)}"}

@app.post("/respostas")
async def gerar_respostas_api(request: Request):
    try:
        data = await request.json()
        questoes = data.get("questoes", [])

        if not isinstance(questoes, list) or not questoes:
            return {"error": "Envie uma lista de questões válida no campo 'questoes'."}

        respostas = [gerar_resposta(q) for q in questoes]
        return {"respostas": respostas}
    except Exception as e:
        return {"error": f"Erro ao gerar respostas: {str(e)}"}