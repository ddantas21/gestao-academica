"""RF21 / RF22 - Média ponderada e status de aprovação.

Funções puras (sem arquivo, sem estado): a média nunca é gravada, é calculada a cada
leitura (RF21). Por isso, alterar uma nota ou peso no ``notas.txt`` já aparece na leitura
seguinte (RF24).
"""
from decimal import ROUND_HALF_UP, Decimal

MEDIA_MAXIMA = Decimal("10.00")
MEDIA_APROVACAO = Decimal("7.0")
CASAS = Decimal("0.01")


def media_ponderada(nota):
    """Calcula ``(N1*P1 + N2*P2 + N3*P3) / (P1 + P2 + P3)`` com duas casas decimais.

    O resultado é arredondado para cima em ``.005`` (``ROUND_HALF_UP``) e limitado a
    10.00 (RF22). Com notas validadas entre 0 e 10 a média já não passa de 10; o teto é
    uma segunda barreira caso um objeto seja alterado sem passar pelas validações.

    Args:
        nota (Nota): registro com três notas e três pesos.

    Returns:
        Decimal: média entre 0.00 e 10.00.

    Raises:
        ValueError: se a soma dos pesos não for maior que zero.

    Example:
        >>> from avaliacao import Nota
        >>> str(media_ponderada(Nota("1", "D", "8.5", "2", "7.0", "3", "9.0", "5")))
        '8.30'
    """
    soma_pesos = nota.peso1 + nota.peso2 + nota.peso3
    if soma_pesos <= 0:
        raise ValueError("A soma dos pesos deve ser maior que zero.")
    total = nota.nota1 * nota.peso1 + nota.nota2 * nota.peso2 + nota.nota3 * nota.peso3
    media = (total / soma_pesos).quantize(CASAS, rounding=ROUND_HALF_UP)
    return min(media, MEDIA_MAXIMA)


def status(media):
    """RF23: ``"Aprovado"`` se a média for >= 7.0, senão ``"Reprovado"``.

    Compara a média já arredondada, que é o valor mostrado ao usuário (assim a tela
    nunca exibe 7.00 com status Reprovado).
    """
    return "Aprovado" if media >= MEDIA_APROVACAO else "Reprovado"
