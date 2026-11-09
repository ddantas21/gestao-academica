"""RF15 - Relatório Integrado Completo.

Seguindo a dica do enunciado, a regra de negócio do relatório fica numa classe
gerenciadora própria (GerenciadorRelatorios). As entidades continuam sendo apenas
modelos de dados, e o SistemaIntegrado só faz a "costura" entre as equipes.

Por que dicionários? Antes, cada linha do relatório chamava `buscar()`, que percorre a
lista inteira (O(n)). Montando índices {codigo: objeto} uma única vez, cada consulta
passa a custar O(1), e o relatório inteiro fica O(alunos + disciplinas).
"""
from collections import defaultdict
from dataclasses import dataclass


@dataclass(frozen=True)
class LinhaRelatorio:
    """Uma relação Aluno -> Curso -> Disciplina -> Professor já resolvida em nomes."""
    aluno: str
    curso: str
    disciplina: str | None = None
    professor: str | None = None

    @property
    def frase(self):
        """Frase exatamente no formato exigido pelo RF15."""
        if self.disciplina is None:
            return (f"O Aluno {self.aluno} está matriculado no curso {self.curso}, "
                    "sem disciplinas cadastradas.")
        return (f"O Aluno {self.aluno} está matriculado no curso {self.curso}, "
                f"assistindo a disciplina {self.disciplina} com o professor {self.professor}")


class GerenciadorRelatorios:
    """Gera a listagem consolidada que relaciona as quatro entidades."""

    def __init__(self, cursos, alunos, professores, disciplinas):
        """Recebe os gerenciadores já carregados (injeção de dependência).

        Args:
            cursos, alunos, professores, disciplinas: gerenciadores de cada entidade.
        """
        # Recebendo os gerenciadores prontos, a classe pode ser testada com dados de
        # qualquer pasta, sem depender de caminhos fixos.
        self._cursos = cursos
        self._alunos = alunos
        self._professores = professores
        self._disciplinas = disciplinas

    def gerar(self):
        """Devolve a lista de LinhaRelatorio, sempre a partir dos dados atuais em memória."""
        cursos = {c.codigo_curso: c for c in self._cursos.listar()}
        professores = {p.codigo_professor: p for p in self._professores.listar()}

        # Agrupa disciplinas por curso uma única vez (defaultdict evita checar "if chave in")
        disciplinas_por_curso = defaultdict(list)
        for disciplina in self._disciplinas.listar():
            disciplinas_por_curso[disciplina.codigo_curso].append(disciplina)

        linhas = []
        for aluno in self._alunos.listar():
            curso = cursos.get(aluno.codigo_curso)
            nome_curso = curso.nome if curso else f"(curso {aluno.codigo_curso} não encontrado)"
            disciplinas = disciplinas_por_curso.get(aluno.codigo_curso, [])
            if not disciplinas:
                linhas.append(LinhaRelatorio(aluno.nome, nome_curso))
                continue
            for disciplina in disciplinas:
                professor = professores.get(disciplina.codigo_professor)
                nome_prof = (professor.nome if professor
                             else f"(professor {disciplina.codigo_professor} não encontrado)")
                linhas.append(LinhaRelatorio(aluno.nome, nome_curso, disciplina.nome, nome_prof))
        return linhas

    def frases(self):
        """Atalho usado pelas interfaces: só o texto de cada linha."""
        return [linha.frase for linha in self.gerar()]
