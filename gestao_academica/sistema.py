"""Integração final: junta ALFA (Curso/Aluno) e BETA (Professor/Disciplina).

É a única peça que conhece as duas equipes. As interfaces (console e gráfica) só
conversam com o SistemaIntegrado, nunca diretamente com os arquivos .txt.
"""
from pathlib import Path

from relatorios import GerenciadorRelatorios

from alfa.gerenciadores import GerenciadorAlunos, GerenciadorCursos
from alfa import Aluno, Curso
from avaliacao.gerenciadores import GerenciadorNotas, GerenciadorRendimento
from beta.integracao import SistemaBeta
from beta import Disciplina, Professor

PASTA_DADOS = Path(__file__).parent / "dados"

# Metadados compartilhados pelo menu de console e pela interface gráfica (primeiro campo = código)
ENTIDADES = {
    "curso": dict(titulo="Cursos", gerente="cursos", classe=Curso, campos=[
        ("codigo_curso", "Código do curso"), ("nome", "Nome"), ("modalidade", "Modalidade (Presencial/EAD)")]),
    "aluno": dict(titulo="Alunos", gerente="alunos", classe=Aluno, campos=[
        ("matricula", "Matrícula"), ("nome", "Nome"), ("cpf", "CPF"), ("email", "E-mail"),
        ("codigo_curso", "Código do curso")]),
    "professor": dict(titulo="Professores", gerente="professores", classe=Professor, campos=[
        ("codigo_professor", "Código do professor"), ("nome", "Nome"), ("cpf", "CPF"),
        ("especialidade", "Especialidade")]),
    "disciplina": dict(titulo="Disciplinas", gerente="disciplinas", classe=Disciplina, campos=[
        ("codigo_disciplina", "Código da disciplina"), ("nome", "Nome"),
        ("carga_horaria", "Carga horária (horas)"), ("codigo_professor", "Código do professor"),
        ("codigo_curso", "Código do curso")]),
}


class SistemaIntegrado:
    """Fachada (*Facade*) que monta e conecta os módulos ALFA e BETA.

    É o único objeto que as interfaces usam. Cria os gerenciadores na ordem de
    dependência, liga o validador de curso da BETA à ALFA e registra os dependentes
    de cada entidade (integridade referencial entre equipes).

    Attributes:
        cursos, alunos, professores, disciplinas: gerenciadores de cada entidade.
        beta (SistemaBeta): núcleo da equipe BETA.
        relatorios (GerenciadorRelatorios): gerador do relatório integrado (RF15).
        notas (GerenciadorNotas): notas e pesos por aluno e disciplina (RF19-RF20).
        rendimento (GerenciadorRendimento): relatório de rendimento escolar (RF23).
    """
    def __init__(self, pasta_dados=PASTA_DADOS):
        """Carrega todos os .txt da pasta e conecta as equipes (RF11).

        Args:
            pasta_dados (str | Path): pasta com os quatro arquivos .txt.
        """
        pasta = Path(pasta_dados)
        self.cursos = GerenciadorCursos(pasta / "cursos.txt")
        self.alunos = GerenciadorAlunos(pasta / "alunos.txt", self.cursos)
        # BETA recebe o validador de curso da ALFA: é aqui que as equipes se conectam
        self.beta = SistemaBeta(pasta, validador_curso=lambda codigo: self.cursos.buscar(codigo) is not None)
        self.professores = self.beta.professores
        self.disciplinas = self.beta.disciplinas
        # Curso só pode ser excluído se não tiver alunos nem disciplinas
        self.cursos.dependentes += [(self.alunos, "codigo_curso", "aluno(s)"),
                                    (self.disciplinas, "codigo_curso", "disciplina(s)")]
        # RF15: o relatório recebe os quatro gerenciadores já carregados (RF11)
        self.relatorios = GerenciadorRelatorios(self.cursos, self.alunos,
                                                self.professores, self.disciplinas)
        # Módulo de Avaliação (RF19-RF24): depende de alunos e disciplinas já carregados
        self.notas = GerenciadorNotas(pasta / "notas.txt", self.alunos, self.disciplinas)
        self.rendimento = GerenciadorRendimento(self.notas, self.alunos, self.disciplinas)
        # Aluno ou disciplina com notas lançadas não pode ser excluído; trocar a matrícula
        # ou o código da disciplina atualiza o notas.txt junto (mesma regra do RN05)
        self.alunos.dependentes.append((self.notas, "matricula", "nota(s)"))
        self.disciplinas.dependentes.append((self.notas, "codigo_disciplina", "nota(s)"))

    def gerenciadores(self):
        """Lista os quatro gerenciadores na ordem de exibição.

        Returns:
            list[Gerenciador]: cursos, alunos, professores e disciplinas.
        """
        return [self.cursos, self.alunos, self.professores, self.disciplinas]

    def avisos_de_carga(self):
        """Mensagens sobre linhas dos .txt que não puderam ser lidas."""
        return [f"{g.arquivo.name}: linha ignorada -> {linha}"
                for g in self.gerenciadores() + [self.notas] for linha in g.linhas_ignoradas]

    def relatorio(self):
        """RF15: frases do relatório integrado (a regra mora em GerenciadorRelatorios)."""
        return self.relatorios.frases()

    def relatorio_rendimento(self):
        """RF23: linhas do relatório de rendimento escolar (média recalculada a cada chamada)."""
        return self.rendimento.gerar()

    def gerenciador(self, chave):
        """Devolve o gerenciador de uma entidade a partir da chave usada em ENTIDADES."""
        return getattr(self, ENTIDADES[chave]["gerente"])

    def resumo_encerramento(self):
        """RF18: texto exibido ao sair. Como o RF12 grava a cada operação, nada fica pendente."""
        totais = ", ".join([f"{len(self.gerenciador(c).listar())} {m['titulo'].lower()}"
                            for c, m in ENTIDADES.items()] + [f"{len(self.notas.listar())} notas"])
        return f"Dados já sincronizados nos arquivos .txt ({totais})."
