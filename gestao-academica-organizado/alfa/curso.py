"""Entidade Curso — Equipe ALFA (RF07).

Modelo de dados puro. O Curso é a entidade "raiz" dos vínculos: Aluno e Disciplina
apontam para ele pelo ``codigo_curso``.
"""
from nucleo.entidade import Entidade, propriedade
from .validacoes import validar_codigo_curso, validar_modalidade_curso, validar_nome_curso


class Curso(Entidade):
    """Programa oferecido pela instituição.

    Attributes:
        codigo_curso (str): identificador único (chave do cursos.txt).
        nome (str): nome do curso.
        modalidade (str): ``"Presencial"`` ou ``"EAD"``.
    """
    # Ordem dos campos = ordem das colunas no cursos.txt.
    CAMPOS = ("codigo_curso", "nome", "modalidade")

    # Atributos protegidos (_codigo_curso...) com getter/setter via @property
    codigo_curso = propriedade("codigo_curso", "O código do curso", validar_codigo_curso)
    nome = propriedade("nome", "O nome do curso", validar_nome_curso)
    modalidade = propriedade("modalidade", "A modalidade", validar_modalidade_curso)

    def __init__(self, codigo_curso, nome, modalidade):
        """Cria o curso; os setters validam já na criação.

        Raises:
            ValueError: se qualquer campo for inválido.
        """
        self.codigo_curso = codigo_curso
        self.nome = nome
        self.modalidade = modalidade

    def __str__(self):
        """Representação legível usada nas listagens e mensagens."""
        return f"Código: {self.codigo_curso} | Curso: {self.nome} | Modalidade: {self.modalidade}"
