from transformers import pipeline
from datetime import date
import random
import importlib

# Verifica se o PyTorch está instalado
try:
    torch_spec = importlib.util.find_spec("torch")
    if torch_spec is None:
        raise ImportError("PyTorch não está instalado. Use: pip install torch")
except ImportError as e:
    raise RuntimeError(str(e))

# Inicializa os modelos
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
generator = pipeline("text2text-generation", model="google/flan-t5-base")

_flashcard_cache = {}

def gerar_resumo(texto):
    try:
        resultado = summarizer(texto, max_length=150, min_length=30, do_sample=False)
        return resultado[0]['summary_text']
    except Exception as e:
        return f"Erro ao gerar resumo: {str(e)}"

def gerar_questoes(conteudo):
    try:
        prompt = f"Gere 3 perguntas sobre o seguinte conteúdo:\n{conteudo}"
        resultado = generator(prompt, max_length=256, do_sample=False)
        perguntas = resultado[0]['generated_text'].split("\n")
        return [p.strip() for p in perguntas if p.strip()]
    except Exception as e:
        return [f"Erro ao gerar questões: {str(e)}"]

def gerar_flashcards(conteudo):
    try:
        prompt = f"Crie 5 flashcards com perguntas e respostas curtas sobre:\n{conteudo}"
        resultado = generator(prompt, max_length=512, do_sample=False)
        linhas = resultado[0]['generated_text'].strip().split("\n")
        flashcards = []
        for i in range(0, len(linhas), 2):
            pergunta = linhas[i].strip() if i < len(linhas) else ""
            resposta = linhas[i+1].strip() if (i+1) < len(linhas) else ""
            if pergunta and resposta:
                flashcards.append({"pergunta": pergunta, "resposta": resposta})
        return flashcards
    except Exception as e:
        return [{"erro": f"Erro ao gerar flashcards: {str(e)}"}]

def flashcard_do_dia(conteudo):
    hoje = str(date.today())
    if conteudo not in _flashcard_cache or _flashcard_cache[conteudo]["data"] != hoje:
        flashcards = gerar_flashcards(conteudo)
        if flashcards:
            escolhido = random.choice(flashcards)
            _flashcard_cache[conteudo] = {
                "data": hoje,
                "flashcard": escolhido
            }
        else:
            return "Nenhum flashcard gerado."
    return _flashcard_cache[conteudo]["flashcard"]

def gerar_resposta(pergunta, contexto=None):
    try:
        prompt = f"Responda de forma clara e objetiva: {pergunta}"
        if contexto:
            prompt = f"Baseado no seguinte contexto, responda: {contexto}\nPergunta: {pergunta}"
        resultado = generator(prompt, max_length=256, do_sample=False)
        return resultado[0]['generated_text'].strip()
    except Exception as e:
        return f"Erro ao gerar resposta: {str(e)}"

def gerar_rotina(tempo_disponivel, nivel, objetivo):
    try:
        tempo_str = str(tempo_disponivel).strip()
        if not tempo_str or not nivel or not objetivo:
            return "Parâmetros inválidos."

        prompt = (
            f"Crie uma rotina de estudos para um tempo disponível de {tempo_str} horas por dia, "
            f"com nível {nivel} e objetivo {objetivo}. "
            "Divida por dias da semana e liste as tarefas."
        )

        resultado = generator(prompt, max_length=512, do_sample=False)
        texto = resultado[0]['generated_text'].strip()

        rotina = {}
        for linha in texto.split("\n"):
            if ":" in linha:
                dia, tarefas = linha.split(":", 1)
                lista_tarefas = [t.strip("- ").strip() for t in tarefas.split("-") if t.strip()]
                rotina[dia.strip()] = lista_tarefas

        if not rotina:
            return texto  # Fallback para texto puro

        return rotina
    except Exception as e:
        return f"Erro ao gerar rotina: {str(e)}"
