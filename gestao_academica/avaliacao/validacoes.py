"""Regras de validação do módulo de Avaliação (Nota).

Cada função recebe o texto já limpo por :func:`nucleo.entidade.propriedade` e devolve o
valor normalizado (``Decimal`` para notas e pesos) ou levanta ``ValueError`` com mensagem
pronta para o usuário.

Decisões:
  * Usa-se ``Decimal`` (e não ``float``) para a média não sofrer erros de arredondamento
    binário, o que poderia aprovar ou reprovar um aluno por 0,000001.
  * A vírgula decimal (``8,5``) é aceita na entrada e gravada com ponto (``8.5``), que é
    o formato do ``notas.txt`` (RF20).

Arquitetura: depende somente de ``nucleo`` (ver docs/adr/ADR-011).
"""
import re
from decimal import Decimal

from nucleo.entidade import validar_codigo

NOTA_MINIMA = Decimal("0.0")
NOTA_MAXIMA = Decimal("10.0")
_NUMERO = re.compile(r"[0-9]+(?:[.,][0-9]+)?")


def _para_decimal(texto, mensagem):
    """Converte ``"8,5"`` ou ``"8.5"`` em ``Decimal``; recusa qualquer outro formato.

    Raises:
        ValueError: com ``mensagem`` se o texto não for um número decimal simples
            (sem sinal, sem notação científica, sem ``nan``/``inf``).
    """
    if not _NUMERO.fullmatch(texto):
        raise ValueError(mensagem)
    return Decimal(texto.replace(",", "."))


def validar_matricula_nota(valor, rotulo="Matrícula do aluno"):
    """Valida o formato da matrícula usada como vínculo com ``alunos.txt`` (RF19)."""
    return validar_codigo(valor, rotulo)


def validar_codigo_disciplina_nota(valor, rotulo="Código da disciplina"):
    """Valida o formato do código usado como vínculo com ``disciplinas.txt`` (RF19)."""
    return validar_codigo(valor, rotulo)


def validar_nota(valor, rotulo="A nota"):
    """RF22: a nota deve estar entre 0.0 e 10.0 (inclusive).

    Returns:
        Decimal: a nota, sem alterar a quantidade de casas digitadas.

    Raises:
        ValueError: se não for número ou estiver fora do intervalo.
    """
    nota = _para_decimal(valor, f"{rotulo} deve ser um número entre 0.0 e 10.0 (ex.: 8.5).")
    if not NOTA_MINIMA <= nota <= NOTA_MAXIMA:
        raise ValueError(f"{rotulo} deve estar entre 0.0 e 10.0.")
    return nota


def validar_peso(valor, rotulo="O peso"):
    """Valida o peso de uma nota: número maior ou igual a zero.

    Raises:
        ValueError: se não for número ou for negativo.
    """
    return _para_decimal(valor, f"{rotulo} deve ser um número maior ou igual a zero (ex.: 2).")
