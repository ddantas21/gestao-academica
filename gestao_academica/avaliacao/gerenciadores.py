"""Gerenciador de Notas (notas.txt) e relatório de rendimento escolar (RF19–RF24).

Reaproveita o CRUD e a persistência de :class:`nucleo.gerenciador.Gerenciador`. A chave
do registro é composta: (matrícula, código da disciplina), isto é, um aluno tem no
máximo um registro de notas por disciplina.

O módulo não importa ``alfa`` nem ``beta``: recebe os gerenciadores de alunos e de
disciplinas já prontos (injeção de dependência) e só usa ``buscar``/``listar``.
"""
from dataclasses import dataclass
from decimal import Decimal

from nucleo.gerenciador import Gerenciador
from nucleo.entidade import normalizar
from .calculo import media_ponderada, status
from .nota import Nota


class GerenciadorNotas(Gerenciador):
    """CRUD e persistência de notas (notas.txt) com validação de vínculos.

    Identificador: tupla ``(matricula, codigo_disciplina)``. Em ``buscar``, ``obter``,
    ``alterar`` e ``excluir`` o código é informado assim: ``("202301", "D01")``.

    Lê o arquivo de novo antes de listar, pesquisar e de cada gravação, de modo que
    uma edição manual do ``notas.txt`` vale já na operação seguinte (RF24).
    """
    ROTULO = "nota"
    CLASSE = Nota

    def __init__(self, arquivo, gerenciador_alunos, gerenciador_disciplinas):
        """Cria o gerenciador.

        Args:
            arquivo (str | Path): caminho do notas.txt.
            gerenciador_alunos: usado para checar se a matrícula existe.
            gerenciador_disciplinas: usado para checar se a disciplina existe.
        """
        # Precisam existir ANTES do super().__init__, que já chama carregar()
        self.gerenciador_alunos = gerenciador_alunos
        self.gerenciador_disciplinas = gerenciador_disciplinas
        super().__init__(arquivo)

    # ---------- chave composta ----------
    def identificador(self, obj):
        """Chave composta ``(matricula, codigo_disciplina)``."""
        return (obj.matricula, obj.codigo_disciplina)

    def _normalizar_id(self, codigo):
        """Aceita ``(matricula, disciplina)`` ou ``"matricula/disciplina"``.

        Raises:
            ValueError: se não houver exatamente dois componentes.
        """
        if isinstance(codigo, str):
            codigo = codigo.split("/")
        try:
            matricula, disciplina = codigo
        except (TypeError, ValueError):
            raise ValueError("Informe a matrícula e o código da disciplina.") from None
        return (str(matricula).strip(), str(disciplina).strip())

    def _texto_id(self, codigo):
        """Texto ``matricula/disciplina`` para as mensagens de erro."""
        return "/".join(self._normalizar_id(codigo))

    # ---------- vínculos (RF19) ----------
    def validar_vinculos(self, nota):
        """O aluno e a disciplina precisam existir.

        Raises:
            ValueError: se a matrícula ou a disciplina não estiver cadastrada.
        """
        if self.gerenciador_alunos.buscar(nota.matricula) is None:
            raise ValueError(f"O aluno '{nota.matricula}' não existe. Cadastre o aluno primeiro.")
        if self.gerenciador_disciplinas.buscar(nota.codigo_disciplina) is None:
            raise ValueError(f"A disciplina '{nota.codigo_disciplina}' não existe. "
                             "Cadastre a disciplina primeiro.")

    # ---------- leitura sempre atualizada (RF24) ----------
    def listar(self):
        """Relê o arquivo e devolve uma cópia da lista (RF24)."""
        self.carregar()
        return super().listar()

    def pesquisar(self, termo):
        """Pesquisa por matrícula ou código da disciplina (exatos, sem diferenciar caixa)."""
        termo_n = normalizar(termo)
        if termo_n == "":
            return []
        return [n for n in self.listar()
                if termo_n in (normalizar(n.matricula), normalizar(n.codigo_disciplina))]

    def cadastrar(self, obj):
        """Relê o arquivo e cadastra (não sobrescreve edições manuais recentes)."""
        self.carregar()
        return super().cadastrar(obj)

    def alterar(self, codigo, **novos_dados):
        """Relê o arquivo e altera (ver :meth:`nucleo.gerenciador.Gerenciador.alterar`)."""
        self.carregar()
        return super().alterar(codigo, **novos_dados)

    def excluir(self, codigo):
        """Relê o arquivo e exclui (ver :meth:`nucleo.gerenciador.Gerenciador.excluir`)."""
        self.carregar()
        return super().excluir(codigo)

    def _trocas_de_referencia(self, campo, antigo, novo):
        """Relê o arquivo antes de propagar a troca de matrícula/disciplina (RF24)."""
        self.carregar()
        return super()._trocas_de_referencia(campo, antigo, novo)

    # ---------- cálculo (RF21) ----------
    @staticmethod
    def media(nota):
        """Média ponderada de uma nota, calculada na hora (RF21/RF22)."""
        return media_ponderada(nota)


@dataclass(frozen=True)
class LinhaRendimento:
    """Uma linha do relatório de rendimento escolar (RF23), já com nomes resolvidos."""
    matricula: str
    aluno: str
    codigo_disciplina: str
    disciplina: str
    notas: tuple           # ((nota1, peso1), (nota2, peso2), (nota3, peso3))
    media: Decimal
    situacao: str

    @property
    def texto_notas(self):
        """Notas e pesos individuais, ex.: ``8.5 (peso 2) | 7.0 (peso 3) | 9.0 (peso 5)``."""
        return " | ".join(f"{n} (peso {p})" for n, p in self.notas)

    @property
    def frase(self):
        """Linha completa do relatório em uma frase."""
        return (f"{self.aluno} — {self.disciplina}: {self.texto_notas} "
                f"=> Média {self.media} — {self.situacao}")


class GerenciadorRendimento:
    """RF23: gera o relatório de rendimento escolar a partir das notas atuais."""

    def __init__(self, notas, alunos, disciplinas):
        """Recebe os gerenciadores já carregados (injeção de dependência).

        Args:
            notas (GerenciadorNotas): origem das notas.
            alunos, disciplinas: gerenciadores usados só para resolver os nomes.
        """
        self._notas = notas
        self._alunos = alunos
        self._disciplinas = disciplinas

    def gerar(self):
        """Devolve a lista de :class:`LinhaRendimento` com a média recalculada agora."""
        alunos = {a.matricula: a for a in self._alunos.listar()}
        disciplinas = {d.codigo_disciplina: d for d in self._disciplinas.listar()}
        linhas = []
        for nota in self._notas.listar():     # listar() relê o arquivo (RF24)
            aluno = alunos.get(nota.matricula)
            disciplina = disciplinas.get(nota.codigo_disciplina)
            media = media_ponderada(nota)
            linhas.append(LinhaRendimento(
                matricula=nota.matricula,
                aluno=aluno.nome if aluno else f"(aluno {nota.matricula} não encontrado)",
                codigo_disciplina=nota.codigo_disciplina,
                disciplina=(disciplina.nome if disciplina
                            else f"(disciplina {nota.codigo_disciplina} não encontrada)"),
                notas=((nota.nota1, nota.peso1), (nota.nota2, nota.peso2), (nota.nota3, nota.peso3)),
                media=media,
                situacao=status(media)))
        return linhas
