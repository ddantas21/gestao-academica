"""Regras de validação da equipe ALFA (Aluno e Curso).

Cada função recebe o texto já limpo por :func:`nucleo.entidade.propriedade` e devolve o
valor normalizado ou levanta ``ValueError`` com mensagem pronta para o usuário.
Especializam as regras genéricas de :mod:`nucleo.entidade` com rótulos próprios.

Arquitetura: depende somente de ``nucleo`` (ver docs/arquitetura/arc42.md, seção 5).
"""
from nucleo.entidade import (validar_codigo, validar_cpf, validar_email, validar_modalidade,
                             validar_nome)


def validar_matricula(valor, rotulo="Matrícula"):
    """Valida a matrícula do aluno (1 a 24 caracteres alfanuméricos, ``_`` ou ``-``).

    Raises:
        ValueError: se o formato for inválido.
    """
    return validar_codigo(valor, rotulo)


def validar_codigo_curso(valor, rotulo="Código do curso"):
    """Valida o formato do código de curso (chave do Curso e vínculo do Aluno, RF13)."""
    return validar_codigo(valor, rotulo)


def validar_nome_aluno(valor, rotulo="Nome do aluno"):
    """Valida o nome do aluno (1 a 120 caracteres, ao menos uma letra)."""
    return validar_nome(valor, rotulo)


def validar_nome_curso(valor, rotulo="Nome do curso"):
    """Valida o nome do curso (1 a 120 caracteres, ao menos uma letra)."""
    return validar_nome(valor, rotulo)


def validar_cpf_aluno(valor, rotulo="CPF"):
    """Valida e formata o CPF do aluno.

    Returns:
        str: CPF no formato ``000.000.000-00``.
    """
    return validar_cpf(valor, rotulo)


def validar_email_aluno(valor, rotulo="E-mail"):
    """Valida o formato do e-mail (``nome@dominio.ext``, até 254 caracteres)."""
    return validar_email(valor, rotulo)


def validar_modalidade_curso(valor, rotulo="Modalidade"):
    """Valida a modalidade do curso.

    Returns:
        str: ``"Presencial"`` ou ``"EAD"`` (normaliza maiúsculas/minúsculas).
    """
    return validar_modalidade(valor, rotulo)
