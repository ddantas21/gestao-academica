"""EQUIPE ALFA - gerenciadores (lógica de arquivo e listas) de Curso e Aluno.

Toda a mecânica de CRUD e persistência é herdada de :class:`nucleo.gerenciador.Gerenciador`;
aqui ficam apenas as configurações e regras específicas de cada entidade.
"""
from nucleo.gerenciador import Gerenciador
from .aluno import Aluno
from .curso import Curso


class GerenciadorCursos(Gerenciador):
    """CRUD e persistência de cursos (cursos.txt).

    Os dependentes (alunos e disciplinas) são registrados pelo SistemaIntegrado, pois
    a ALFA não conhece a BETA.
    """
    ROTULO = "curso"
    CLASSE = Curso


class GerenciadorAlunos(Gerenciador):
    """CRUD e persistência de alunos (alunos.txt), com validação do curso (RF13).

    O CPF não pode se repetir entre alunos.
    """
    ROTULO = "aluno"
    CLASSE = Aluno
    CAMPOS_UNICOS = ("cpf",)

    def __init__(self, arquivo, gerenciador_cursos):
        """Cria o gerenciador.

        Args:
            arquivo (str | Path): caminho do alunos.txt.
            gerenciador_cursos (GerenciadorCursos): usado para checar se o curso existe.
        """
        self.gerenciador_cursos = gerenciador_cursos   # precisa existir antes do carregar()
        super().__init__(arquivo)

    def validar_vinculos(self, aluno):
        """RF13: o curso do aluno precisa existir.

        Raises:
            ValueError: se o curso não estiver cadastrado.
        """
        if self.gerenciador_cursos.buscar(aluno.codigo_curso) is None:
            raise ValueError(f"O curso '{aluno.codigo_curso}' não existe. Cadastre o curso primeiro.")
