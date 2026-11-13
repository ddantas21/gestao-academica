"""Entidade Professor — Equipe BETA (RF08).

Modelo de dados puro: atributos protegidos expostos por ``@property`` com validação.
"""
from nucleo.entidade import Entidade, propriedade
from .validacoes import (validar_codigo_professor, validar_cpf_professor,
                         validar_especialidade_professor, validar_nome_professor)


class Professor(Entidade):
    """Docente da instituição.

    Attributes:
        codigo_professor (str): identificador único (chave do professores.txt).
        nome (str): nome completo.
        cpf (str): CPF formatado ``000.000.000-00``; único entre professores.
        especialidade (str): área de atuação.
    """
    # Ordem dos campos = ordem das colunas no professores.txt.
    CAMPOS = ("codigo_professor", "nome", "cpf", "especialidade")

    codigo_professor = propriedade("codigo_professor", "O código do professor", validar_codigo_professor)
    nome = propriedade("nome", "O nome do professor", validar_nome_professor)
    cpf = propriedade("cpf", "O CPF", validar_cpf_professor)
    especialidade = propriedade("especialidade", "A especialidade", validar_especialidade_professor)

    def __init__(self, codigo_professor, nome, cpf, especialidade):
        """Cria o professor validando cada campo.

        Raises:
            ValueError: se qualquer campo for inválido.
        """
        self.codigo_professor = codigo_professor
        self.nome = nome
        self.cpf = cpf
        self.especialidade = especialidade

    def __str__(self):
        """Representação legível usada nas listagens e mensagens."""
        return (f"Código: {self.codigo_professor} | Professor: {self.nome} | CPF: {self.cpf} | "
                f"Especialidade: {self.especialidade}")
