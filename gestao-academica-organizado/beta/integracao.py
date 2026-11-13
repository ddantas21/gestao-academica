"""EQUIPE BETA - gerenciadores de Professor e Disciplina e ponto de integração com a ALFA.

O :class:`SistemaBeta` funciona sozinho (útil para a BETA desenvolver e testar sem a
ALFA). Para validar o código do curso, basta informar um ``validador_curso`` (função que
recebe o código e devolve ``True``/``False``); sem ele, o código do curso é apenas
armazenado. Ver docs/adr/ADR-004.
"""
from pathlib import Path

from nucleo.gerenciador import Gerenciador
from .disciplina import Disciplina
from .professor import Professor


class GerenciadorProfessores(Gerenciador):
    """CRUD e persistência de professores (professores.txt). O CPF não pode se repetir."""
    ROTULO = "professor"
    CLASSE = Professor
    CAMPOS_UNICOS = ("cpf",)


class GerenciadorDisciplinas(Gerenciador):
    """CRUD e persistência de disciplinas (disciplinas.txt), com validação de vínculos (RF14)."""
    ROTULO = "disciplina"
    CLASSE = Disciplina

    def __init__(self, arquivo, gerenciador_professores, validador_curso=None):
        """Cria o gerenciador.

        Args:
            arquivo (str | Path): caminho do disciplinas.txt.
            gerenciador_professores (GerenciadorProfessores): usado para checar o professor.
            validador_curso (Callable[[str], bool] | None): diz se um código de curso existe.
                Sem ele, o curso não é verificado (modo BETA isolado).
        """
        # Precisam existir ANTES do super().__init__, que já chama carregar()
        self.gerenciador_professores = gerenciador_professores
        self.validador_curso = validador_curso
        super().__init__(arquivo)

    def validar_vinculos(self, disciplina):
        """RF14: o professor deve existir e, se houver validador, o curso também.

        Raises:
            ValueError: se o professor ou o curso não existir.
        """
        if self.gerenciador_professores.buscar(disciplina.codigo_professor) is None:
            raise ValueError(f"O professor '{disciplina.codigo_professor}' não existe. "
                             "Cadastre o professor primeiro.")
        if self.validador_curso is not None and not self.validador_curso(disciplina.codigo_curso):
            raise ValueError(f"O curso '{disciplina.codigo_curso}' não existe. Cadastre o curso primeiro.")


class SistemaBeta:
    """Agrupa os gerenciadores da BETA e liga suas regras de integridade internas.

    Attributes:
        professores (GerenciadorProfessores): gerenciador de professores.
        disciplinas (GerenciadorDisciplinas): gerenciador de disciplinas.
    """

    def __init__(self, pasta_dados, validador_curso=None):
        """Carrega professores.txt e disciplinas.txt da pasta informada.

        Args:
            pasta_dados (str | Path): pasta onde estão os arquivos .txt.
            validador_curso (Callable[[str], bool] | None): ver GerenciadorDisciplinas.
        """
        pasta = Path(pasta_dados)
        # Ordem importa: disciplinas dependem de professores
        self.professores = GerenciadorProfessores(pasta / "professores.txt")
        self.disciplinas = GerenciadorDisciplinas(pasta / "disciplinas.txt", self.professores,
                                                  validador_curso)
        # Não deixa excluir professor que ainda leciona; e propaga troca de código (RF04)
        self.professores.dependentes.append((self.disciplinas, "codigo_professor", "disciplina(s)"))

    def conectar_validador_curso(self, validador_curso):
        """Liga (ou troca) o validador de curso depois da criação.

        Args:
            validador_curso (Callable[[str], bool]): função que diz se o curso existe.
        """
        self.disciplinas.validador_curso = validador_curso
