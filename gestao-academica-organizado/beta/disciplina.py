"""Entidade Disciplina — Equipe BETA (RF09).

Modelo de dados puro: guarda e valida os atributos, mas não sabe ler/gravar arquivos
nem verificar se o professor ou o curso existem (isso é do GerenciadorDisciplinas).
"""
from nucleo.entidade import Entidade, propriedade
from .validacoes import (validar_carga_horaria_disciplina, validar_codigo_curso,
                         validar_codigo_disciplina, validar_codigo_professor,
                         validar_nome_disciplina)


class Disciplina(Entidade):
    """Componente curricular ministrado por um professor dentro de um curso.

    Attributes:
        codigo_disciplina (str): identificador único (chave do disciplinas.txt).
        nome (str): nome da disciplina.
        carga_horaria (int): total de horas, maior que zero.
        codigo_professor (str): vínculo com Professor (RF14).
        codigo_curso (str): vínculo com Curso da equipe ALFA (RF14).
    """
    # Ordem dos campos = ordem das colunas no disciplinas.txt. NÃO reordene sem migrar o arquivo.
    CAMPOS = ("codigo_disciplina", "nome", "carga_horaria", "codigo_professor", "codigo_curso")

    codigo_disciplina = propriedade("codigo_disciplina", "O código da disciplina", validar_codigo_disciplina)
    nome = propriedade("nome", "O nome da disciplina", validar_nome_disciplina)
    carga_horaria = propriedade("carga_horaria", "A carga horária", validar_carga_horaria_disciplina)
    codigo_professor = propriedade("codigo_professor", "O código do professor", validar_codigo_professor)
    codigo_curso = propriedade("codigo_curso", "O código do curso", validar_codigo_curso)

    def __init__(self, codigo_disciplina, nome, carga_horaria, codigo_professor, codigo_curso):
        """Cria a disciplina; cada atribuição passa pelo setter e é validada.

        Raises:
            ValueError: se qualquer campo for inválido.
        """
        self.codigo_disciplina = codigo_disciplina
        self.nome = nome
        self.carga_horaria = carga_horaria
        self.codigo_professor = codigo_professor
        self.codigo_curso = codigo_curso

    def __str__(self):
        """Representação legível usada nas listagens e mensagens."""
        return (f"Código: {self.codigo_disciplina} | Disciplina: {self.nome} | "
                f"Carga: {self.carga_horaria}h | Professor: {self.codigo_professor} | "
                f"Curso: {self.codigo_curso}")
