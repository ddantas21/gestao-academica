"""Entidade Aluno — Equipe ALFA (RF06).

Modelo de dados puro: guarda e valida os atributos. A existência do curso (RF13) é
verificada pelo GerenciadorAlunos, não aqui.
"""
from nucleo.entidade import Entidade, propriedade
from .validacoes import (validar_codigo_curso, validar_cpf_aluno, validar_email_aluno,
                         validar_matricula, validar_nome_aluno)


class Aluno(Entidade):
    """Discente matriculado em um curso.

    Attributes:
        matricula (str): identificador único (chave do alunos.txt).
        nome (str): nome completo.
        cpf (str): CPF formatado ``000.000.000-00``; único entre alunos.
        email (str): e-mail de contato.
        codigo_curso (str): vínculo com Curso (RF13).
    """
    # Ordem dos campos = ordem das colunas no alunos.txt.
    CAMPOS = ("matricula", "nome", "cpf", "email", "codigo_curso")

    matricula = propriedade("matricula", "A matrícula", validar_matricula)
    nome = propriedade("nome", "O nome do aluno", validar_nome_aluno)
    cpf = propriedade("cpf", "O CPF", validar_cpf_aluno)
    email = propriedade("email", "O e-mail", validar_email_aluno)
    codigo_curso = propriedade("codigo_curso", "O código do curso", validar_codigo_curso)

    def __init__(self, matricula, nome, cpf, email, codigo_curso):
        """Cria o aluno validando cada campo.

        Raises:
            ValueError: se qualquer campo for inválido.
        """
        self.matricula = matricula
        self.nome = nome
        self.cpf = cpf
        self.email = email
        self.codigo_curso = codigo_curso

    def __str__(self):
        """Representação legível usada nas listagens e mensagens."""
        return (f"Matrícula: {self.matricula} | Nome: {self.nome} | CPF: {self.cpf} | "
                f"E-mail: {self.email} | Curso: {self.codigo_curso}")
