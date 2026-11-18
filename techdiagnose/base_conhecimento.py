import json
from pathlib import Path

PASTA_DADOS = Path(__file__).resolve().parent.parent / "dados"

CAMPOS_REGRA = ["id", "categoria", "se", "entao", "cf", "tipo", "descricao"]
CAMPOS_DIAGNOSTICO = ["solucao", "encaminhamento"]
CAMPOS_PERGUNTA = ["fato", "categoria", "texto"]
TIPOS = ["intermediario", "diagnostico"]


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


def exigir_campos(item, campos, nome):
    if not isinstance(item, dict):
        raise ErroBaseConhecimento(f"{nome} não é um objeto JSON")
    faltando = [c for c in campos if c not in item]
    if faltando:
        raise ErroBaseConhecimento(f"{nome} sem o(s) campo(s): {', '.join(faltando)}")


def validar_regras(regras):
    if not isinstance(regras, list) or not regras:
        raise ErroBaseConhecimento("regras.json deve ser uma lista com pelo menos uma regra")
    ids = set()
    for i, regra in enumerate(regras, start=1):
        exigir_campos(regra, CAMPOS_REGRA, f"Regra na posição {i}")
        nome = f"Regra {regra['id']}"
        if regra["id"] in ids:
            raise ErroBaseConhecimento(f"{nome} está repetida")
        ids.add(regra["id"])

        if regra["tipo"] not in TIPOS:
            raise ErroBaseConhecimento(f"{nome}: tipo deve ser intermediario ou diagnostico")
        if regra["tipo"] == "diagnostico":
            exigir_campos(regra, CAMPOS_DIAGNOSTICO, nome)
        if not isinstance(regra["se"], list) or not regra["se"]:
            raise ErroBaseConhecimento(f"{nome}: 'se' deve ser uma lista com premissas")

        cf = regra["cf"]
        if not isinstance(cf, (int, float)) or not 0 <= cf <= 1:
            raise ErroBaseConhecimento(f"{nome}: cf deve ser um número entre 0 e 1")


def validar_perguntas(perguntas):
    if not isinstance(perguntas, list):
        raise ErroBaseConhecimento("perguntas.json deve ser uma lista de perguntas")
    fatos = set()
    for i, pergunta in enumerate(perguntas, start=1):
        exigir_campos(pergunta, CAMPOS_PERGUNTA, f"Pergunta na posição {i}")
        if pergunta["fato"] in fatos:
            raise ErroBaseConhecimento(f"Pergunta repetida para o fato {pergunta['fato']}")
        fatos.add(pergunta["fato"])


def validar_fatos(regras, perguntas):
    # todo fato usado como premissa precisa vir de uma pergunta ou de outra regra
    conhecidos = {p["fato"] for p in perguntas} | {r["entao"] for r in regras}
    for regra in regras:
        for fato in regra["se"]:
            if fato not in conhecidos:
                raise ErroBaseConhecimento(
                    f"Regra {regra['id']} usa o fato '{fato}', que não tem pergunta "
                    "nem regra que o produza"
                )


def carregar_base(pasta=PASTA_DADOS):
    """Devolve (regras, perguntas). perguntas é um dicionário fato -> pergunta."""
    pasta = Path(pasta)
    regras = ler_json(pasta / "regras.json")
    perguntas = ler_json(pasta / "perguntas.json")
    validar_regras(regras)
    validar_perguntas(perguntas)
    validar_fatos(regras, perguntas)
    return regras, {p["fato"]: p for p in perguntas}
