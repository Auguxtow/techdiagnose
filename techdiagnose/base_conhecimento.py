import json
from pathlib import Path

PASTA_DADOS = Path(__file__).resolve().parent.parent / "dados"


class ErroBaseConhecimento(Exception):
    pass


def ler_json(caminho: Path):
    try:
        with open(caminho, encoding="utf-8") as arquivo:
            return json.load(arquivo)
    except FileNotFoundError:
        raise ErroBaseConhecimento(f"Arquivo não encontrado: {caminho}")
    except json.JSONDecodeError as erro:
        raise ErroBaseConhecimento(
            f"JSON inválido em {caminho.name}, linha {erro.lineno}: {erro.msg}"
        )


def carregar_base(pasta=PASTA_DADOS):
    """Devolve (regras, perguntas). perguntas é um dicionário fato -> pergunta."""
    pasta = Path(pasta)
    regras = ler_json(pasta / "regras.json")
    perguntas = ler_json(pasta / "perguntas.json")
    return regras, {p["fato"]: p for p in perguntas}
