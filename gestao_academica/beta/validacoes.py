"""Regras de validação da equipe BETA (Professor e Disciplina).

Cada função recebe o texto já limpo (sem espaços nas pontas, sem ``;`` e sem caracteres
de controle, garantido por :func:`nucleo.entidade.propriedade`) e devolve o valor
normalizado ou levanta ``ValueError`` com uma mensagem pronta para o usuário.

As funções apenas especializam as regras genéricas de :mod:`nucleo.entidade` com um
rótulo próprio. Manter este arquivo por equipe permite que a BETA endureça uma regra
(ex.: formato do código do professor) sem afetar a ALFA.

Arquitetura: este módulo depende somente de ``nucleo``. A BETA NÃO importa nada da
ALFA (ver docs/adr/ADR-004).
"""
from nucleo.entidade import (validar_carga_horaria, validar_codigo, validar_cpf,
                             validar_especialidade, validar_nome)


def validar_codigo_professor(valor, rotulo="Código do professor"):
    """Valida o identificador do professor (1 a 24 caracteres alfanuméricos, ``_`` ou ``-``).

    Returns:
        str: o próprio código.

    Raises:
        ValueError: se o formato for inválido.
    """
    return validar_codigo(valor, rotulo)


def validar_codigo_disciplina(valor, rotulo="Código da disciplina"):
    """Valida o identificador da disciplina (mesma regra de :func:`validar_codigo_professor`)."""
    return validar_codigo(valor, rotulo)


def validar_codigo_curso(valor, rotulo="Código do curso"):
    """Valida o FORMATO do código de curso usado como vínculo na Disciplina (RF14).

    A existência do curso não é verificada aqui (a entidade não conhece outras
    entidades); isso é feito por ``GerenciadorDisciplinas.validar_vinculos``.
    """
    return validar_codigo(valor, rotulo)


def validar_nome_professor(valor, rotulo="Nome do professor"):
    """Valida o nome do professor (1 a 120 caracteres, ao menos uma letra)."""
    return validar_nome(valor, rotulo)


def validar_nome_disciplina(valor, rotulo="Nome da disciplina"):
    """Valida o nome da disciplina (1 a 120 caracteres, ao menos uma letra)."""
    return validar_nome(valor, rotulo)


def validar_cpf_professor(valor, rotulo="CPF"):
    """Valida e formata o CPF do professor.

    Returns:
        str: CPF no formato ``000.000.000-00``.
    """
    return validar_cpf(valor, rotulo)


def validar_especialidade_professor(valor, rotulo="Especialidade"):
    """Valida a especialidade do professor (1 a 120 caracteres, ao menos uma letra)."""
    return validar_especialidade(valor, rotulo)


def validar_carga_horaria_disciplina(valor, rotulo="Carga horária"):
    """Valida a carga horária da disciplina.

    Returns:
        int: número de horas (sempre maior que zero).
    """
    return validar_carga_horaria(valor, rotulo)
