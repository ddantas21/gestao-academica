"""Entidade Nota — Módulo de Avaliação (RF19).

Modelo de dados puro: guarda e valida os atributos. A existência do aluno e da
disciplina é verificada pelo GerenciadorNotas, e a média é calculada em
:mod:`avaliacao.calculo`, não aqui.
"""
from nucleo.entidade import Entidade, propriedade
from .validacoes import (validar_codigo_disciplina_nota, validar_matricula_nota, validar_nota,
                         validar_peso)


class Nota(Entidade):
    """Desempenho de um aluno em uma disciplina: três notas com seus pesos.

    Attributes:
        matricula (str): vínculo com Aluno (``alunos.txt``).
        codigo_disciplina (str): vínculo com Disciplina (``disciplinas.txt``).
        nota1, nota2, nota3 (Decimal): notas entre 0.0 e 10.0.
        peso1, peso2, peso3 (Decimal): pesos (>= 0); a soma deve ser maior que zero.
    """
    # Ordem dos campos = ordem das colunas no notas.txt (RF20). NÃO reordene sem migrar o arquivo.
    CAMPOS = ("matricula", "codigo_disciplina", "nota1", "peso1", "nota2", "peso2",
              "nota3", "peso3")

    matricula = propriedade("matricula", "A matrícula", validar_matricula_nota)
    codigo_disciplina = propriedade("codigo_disciplina", "O código da disciplina",
                                    validar_codigo_disciplina_nota)
    nota1 = propriedade("nota1", "A nota 1", validar_nota)
    peso1 = propriedade("peso1", "O peso 1", validar_peso)
    nota2 = propriedade("nota2", "A nota 2", validar_nota)
    peso2 = propriedade("peso2", "O peso 2", validar_peso)
    nota3 = propriedade("nota3", "A nota 3", validar_nota)
    peso3 = propriedade("peso3", "O peso 3", validar_peso)

    def __init__(self, matricula, codigo_disciplina, nota1, peso1, nota2, peso2, nota3, peso3):
        """Cria a nota validando cada campo.

        Raises:
            ValueError: se algum campo for inválido ou se a soma dos pesos for zero.
        """
        self.matricula = matricula
        self.codigo_disciplina = codigo_disciplina
        self.nota1 = nota1
        self.peso1 = peso1
        self.nota2 = nota2
        self.peso2 = peso2
        self.nota3 = nota3
        self.peso3 = peso3
        if self.peso1 + self.peso2 + self.peso3 <= 0:
            raise ValueError("A soma dos pesos deve ser maior que zero.")

    def __str__(self):
        """Representação legível usada nas listagens e mensagens."""
        return (f"Matrícula: {self.matricula} | Disciplina: {self.codigo_disciplina} | "
                f"N1: {self.nota1} (peso {self.peso1}) | N2: {self.nota2} (peso {self.peso2}) | "
                f"N3: {self.nota3} (peso {self.peso3})")
