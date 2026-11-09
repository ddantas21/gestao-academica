"""RF17 / RF18 - Menu de navegação via console e encerramento controlado.

O menu é genérico: lê os metadados de ENTIDADES (sistema.py) e funciona para as
quatro entidades sem repetir código. Toda regra de negócio continua nos
gerenciadores; aqui só existe "perguntar, chamar o gerenciador e mostrar o resultado".

`entrada` e `saida` são injetadas no construtor (por padrão input/print). Isso permite
testar o menu inteiro com respostas simuladas, sem ninguém digitando.
"""
from avaliacao import Nota
from demonstracao import executar_demonstracao
from sistema import ENTIDADES

ERROS_ESPERADOS = (ValueError, LookupError, TypeError, OSError)
LARGURA_MAX_COLUNA = 32


class MenuConsole:
    """Interface de terminal (RF17) sobre o SistemaIntegrado.

    Cada opção do menu é uma tupla (rótulo, função) num dicionário: adicionar uma
    opção nova é acrescentar uma entrada, sem mexer no laço principal.
    """
    def __init__(self, sistema, entrada=input, saida=print):
        """Cria o menu.

        Args:
            sistema (SistemaIntegrado): fachada com os gerenciadores.
            entrada (Callable[[str], str]): lê uma resposta (padrão ``input``).
            saida (Callable[[str], None]): exibe uma linha (padrão ``print``).
        """
        self.sistema = sistema
        self._entrada = entrada
        self._saida = saida
        self._ativo = True

    # ---------- utilitários de E/S ----------
    def _perguntar(self, texto):
        """Lê uma resposta do usuário já sem espaços nas pontas."""
        return self._entrada(texto).strip()

    def _confirmar(self, texto):
        """Pergunta sim/não. Só ``s`` ou ``sim`` confirmam (padrão seguro = não)."""
        return self._perguntar(f"{texto} (s/N): ").lower() in ("s", "sim")

    def _titulo(self, texto):
        """Imprime um cabeçalho de seção."""
        self._saida("\n" + "=" * 60)
        self._saida(f"  {texto}")
        self._saida("=" * 60)

    def _escolher(self, titulo, opcoes):
        """Mostra um menu numerado e devolve a tecla escolhida (ou None se inválida)."""
        self._titulo(titulo)
        for tecla, (rotulo, _) in opcoes.items():
            self._saida(f"  [{tecla}] {rotulo}")
        escolha = self._perguntar("\nEscolha uma opção: ")
        if escolha not in opcoes:
            self._saida("Opção inválida. Digite um dos números do menu.")
            return None
        return escolha

    def _tabela(self, meta, registros):
        """Imprime os registros alinhados em colunas (largura calculada pelo maior valor)."""
        if not registros:
            self._saida("Nenhum registro encontrado.")
            return
        campos = meta["campos"]
        cabecalho = [rotulo.split(" (")[0] for _, rotulo in campos]
        linhas = [[str(getattr(r, campo)) for campo, _ in campos] for r in registros]
        # zip(*matriz) "gira" a tabela: cada tupla vira uma coluna inteira
        larguras = [min(LARGURA_MAX_COLUNA, max(len(v) for v in coluna))
                    for coluna in zip(cabecalho, *linhas)]

        def formatar(valores):
            """Formata uma linha da tabela com as larguras calculadas."""
            return " | ".join(self._cortar(v, w).ljust(w) for v, w in zip(valores, larguras))

        self._saida(formatar(cabecalho))
        self._saida("-+-".join("-" * w for w in larguras))
        for linha in linhas:
            self._saida(formatar(linha))
        self._saida(f"\n{len(registros)} registro(s).")

    @staticmethod
    def _cortar(texto, largura):
        """Corta textos maiores que a coluna, indicando o corte com reticências."""
        return texto if len(texto) <= largura else texto[: largura - 1] + "…"

    def _dica_vinculo(self, campo, indice):
        """Para campos de vínculo (RF13/RF14), mostra os códigos disponíveis."""
        if indice == 0 or campo not in ("codigo_curso", "codigo_professor"):
            return ""
        chave = "curso" if campo == "codigo_curso" else "professor"
        codigos = [getattr(r, self.sistema.gerenciador(chave).chave)
                   for r in self.sistema.gerenciador(chave).listar()]
        return f"  disponíveis: {', '.join(codigos) or 'nenhum cadastrado'}\n"

    # ---------- ciclo principal ----------
    def executar(self):
        """Laço principal. Devolve 0 ao sair (código de saída do programa)."""
        self._saida("\nBem-vindo ao Sistema de Gestão Acadêmica (ALFA + BETA)")
        for aviso in self.sistema.avisos_de_carga():
            self._saida(f"[aviso] {aviso}")
        try:
            while self._ativo:
                opcoes = self._opcoes_principais()
                tecla = self._escolher("MENU PRINCIPAL", opcoes)
                if tecla is not None:
                    opcoes[tecla][1]()
        except (KeyboardInterrupt, EOFError):
            # Ctrl+C ou fim da entrada também encerram de forma controlada (RF18)
            self._saida("\nInterrupção recebida.")
            self._finalizar()
        return 0

    def _opcoes_principais(self):
        """Monta o menu principal a partir de ENTIDADES.

        Returns:
            dict[str, tuple[str, Callable]]: tecla -> (rótulo, ação).
        """
        opcoes = {}
        for numero, (chave, meta) in enumerate(ENTIDADES.items(), start=1):
            # chave=chave "congela" o valor do laço; sem isso todas as lambdas usariam o último
            opcoes[str(numero)] = (meta["titulo"], lambda chave=chave: self._menu_entidade(chave))
        opcoes[str(len(opcoes) + 1)] = ("Relatório integrado", self.relatorio)
        opcoes[str(len(opcoes) + 1)] = ("Demonstração da integração final",
                                        lambda: executar_demonstracao(self.sistema, self._saida))
        # Módulo de Avaliação (RF19-RF24): vem depois, para não mudar a numeração anterior
        opcoes[str(len(opcoes) + 1)] = ("Notas e avaliação", self._menu_notas)
        opcoes[str(len(opcoes) + 1)] = ("Relatório de rendimento escolar", self.rendimento)
        opcoes["0"] = ("Sair do sistema", self.sair)
        return opcoes

    def _menu_entidade(self, chave):
        """Submenu de CRUD de uma entidade; volta ao menu principal com 0."""
        titulo = ENTIDADES[chave]["titulo"]
        opcoes = {
            "1": ("Cadastrar", lambda: self.cadastrar(chave)),
            "2": ("Listar", lambda: self.listar(chave)),
            "3": ("Pesquisar (código ou nome)", lambda: self.pesquisar(chave)),
            "4": ("Alterar", lambda: self.alterar(chave)),
            "5": ("Excluir", lambda: self.excluir(chave)),
            "0": ("Voltar ao menu principal", None),
        }
        while True:
            tecla = self._escolher(titulo.upper(), opcoes)
            if tecla == "0":
                return
            if tecla is not None:
                opcoes[tecla][1]()

    # ---------- RF01 a RF05 ----------
    def cadastrar(self, chave):
        """RF01: pergunta todos os campos e cadastra pelo gerenciador."""
        meta = ENTIDADES[chave]
        self._titulo(f"Cadastrar {meta['titulo'][:-1].lower()}")
        dados = {}
        for indice, (campo, rotulo) in enumerate(meta["campos"]):
            dados[campo] = self._perguntar(f"{self._dica_vinculo(campo, indice)}{rotulo}: ")
        try:
            # A classe valida cada campo (RF06-RF09); o gerenciador valida duplicidade,
            # vínculos (RF13/RF14) e grava o .txt (RF10/RF12).
            registro = self.sistema.gerenciador(chave).cadastrar(meta["classe"](**dados))
        except ERROS_ESPERADOS as erro:
            self._saida(f"Não foi possível cadastrar: {erro}")
        else:
            self._saida(f"Cadastrado com sucesso: {registro}")

    def listar(self, chave):
        """RF02: lista todos os registros da entidade em tabela."""
        meta = ENTIDADES[chave]
        self._titulo(f"Lista de {meta['titulo'].lower()}")
        self._tabela(meta, self.sistema.gerenciador(chave).listar())

    def pesquisar(self, chave):
        """RF03: pesquisa por código exato ou parte do nome."""
        meta = ENTIDADES[chave]
        termo = self._perguntar("Digite o código exato ou parte do nome: ")
        if not termo:
            self._saida("Informe algum termo para pesquisar.")
            return
        self._titulo(f"Resultado da pesquisa por '{termo}'")
        self._tabela(meta, self.sistema.gerenciador(chave).pesquisar(termo))

    def alterar(self, chave):
        """RF04: localiza pelo código e pergunta cada campo (Enter mantém o valor).

        Só os campos efetivamente modificados são enviados ao gerenciador.
        """
        meta = ENTIDADES[chave]
        gerente = self.sistema.gerenciador(chave)
        codigo = self._perguntar(f"{meta['campos'][0][1]} do registro a alterar: ")
        try:
            atual = gerente.obter(codigo)
        except LookupError as erro:
            self._saida(str(erro))
            return
        self._saida(f"Registro atual: {atual}")
        self._saida("Pressione Enter para manter o valor atual de cada campo.")
        self._saida("Se mudar o código, os registros vinculados a ele serão atualizados juntos.")
        mudancas = {}
        # RF04: todos os atributos podem ser alterados, inclusive o próprio código
        for indice, (campo, rotulo) in enumerate(meta["campos"]):
            valor_atual = getattr(atual, campo)
            novo = self._perguntar(f"{self._dica_vinculo(campo, indice)}{rotulo} [{valor_atual}]: ")
            if novo and novo != str(valor_atual):
                mudancas[campo] = novo
        if not mudancas:
            self._saida("Nenhuma alteração informada.")
            return
        try:
            registro = gerente.alterar(codigo, **mudancas)
        except ERROS_ESPERADOS as erro:
            self._saida(f"Não foi possível alterar: {erro}")
        else:
            self._saida(f"Alterado com sucesso: {registro}")

    def excluir(self, chave):
        """RF05: localiza pelo código, mostra o registro e exclui após confirmação."""
        meta = ENTIDADES[chave]
        gerente = self.sistema.gerenciador(chave)
        codigo = self._perguntar(f"{meta['campos'][0][1]} do registro a excluir: ")
        try:
            registro = gerente.obter(codigo)
        except LookupError as erro:
            self._saida(str(erro))
            return
        self._saida(f"Registro: {registro}")
        if not self._confirmar("Confirma a exclusão?"):
            self._saida("Exclusão cancelada.")
            return
        try:
            gerente.excluir(codigo)
        except ERROS_ESPERADOS as erro:
            self._saida(f"Não foi possível excluir: {erro}")
        else:
            self._saida("Registro excluído e arquivo .txt atualizado.")

    # ---------- RF19 a RF24: Módulo de Avaliação ----------
    CAMPOS_NOTA = (("nota1", "Nota 1"), ("peso1", "Peso 1"), ("nota2", "Nota 2"),
                   ("peso2", "Peso 2"), ("nota3", "Nota 3"), ("peso3", "Peso 3"))

    def _menu_notas(self):
        """Submenu do Módulo de Avaliação; volta ao menu principal com 0."""
        opcoes = {
            "1": ("Lançar notas de um aluno em uma disciplina", self.cadastrar_nota),
            "2": ("Listar notas (com média)", self.listar_notas),
            "3": ("Pesquisar (matrícula ou código da disciplina)", self.pesquisar_notas),
            "4": ("Alterar notas ou pesos", self.alterar_nota),
            "5": ("Excluir notas", self.excluir_nota),
            "6": ("Relatório de rendimento escolar", self.rendimento),
            "0": ("Voltar ao menu principal", None),
        }
        while True:
            tecla = self._escolher("NOTAS E AVALIAÇÃO", opcoes)
            if tecla == "0":
                return
            if tecla is not None:
                opcoes[tecla][1]()

    def _perguntar_identificacao_nota(self, acao):
        """Pergunta matrícula e disciplina (o par identifica o registro de notas)."""
        matricula = self._perguntar(f"Matrícula do aluno ({acao}): ")
        disciplina = self._perguntar(f"Código da disciplina ({acao}): ")
        return matricula, disciplina

    def _tabela_notas(self, notas):
        """Tabela com notas, pesos e a média calculada agora (RF21)."""
        if not notas:
            self._saida("Nenhuma nota encontrada.")
            return
        cabecalho = ["Matrícula", "Disciplina", "N1", "P1", "N2", "P2", "N3", "P3", "Média"]
        linhas = [[n.matricula, n.codigo_disciplina, str(n.nota1), str(n.peso1), str(n.nota2),
                   str(n.peso2), str(n.nota3), str(n.peso3), str(self.sistema.notas.media(n))]
                  for n in notas]
        larguras = [max(len(v) for v in coluna) for coluna in zip(cabecalho, *linhas)]
        for valores in [cabecalho, None] + linhas:
            if valores is None:
                self._saida("-+-".join("-" * w for w in larguras))
            else:
                self._saida(" | ".join(v.ljust(w) for v, w in zip(valores, larguras)))
        self._saida(f"\n{len(notas)} registro(s).")

    def cadastrar_nota(self):
        """RF19/RF20: lança as três notas e pesos de um aluno em uma disciplina."""
        self._titulo("Lançar notas")
        alunos = ", ".join(a.matricula for a in self.sistema.alunos.listar()) or "nenhum cadastrado"
        disciplinas = ", ".join(d.codigo_disciplina for d in self.sistema.disciplinas.listar()) \
            or "nenhuma cadastrada"
        self._saida(f"Alunos disponíveis: {alunos}\nDisciplinas disponíveis: {disciplinas}")
        dados = {"matricula": self._perguntar("Matrícula do aluno: "),
                 "codigo_disciplina": self._perguntar("Código da disciplina: ")}
        for campo, rotulo in self.CAMPOS_NOTA:
            dados[campo] = self._perguntar(f"{rotulo}: ")
        try:
            nota = self.sistema.notas.cadastrar(Nota(**dados))
        except ERROS_ESPERADOS as erro:
            self._saida(f"Não foi possível lançar: {erro}")
        else:
            self._saida(f"Lançado com sucesso: {nota}")
            self._saida(f"Média calculada: {self.sistema.notas.media(nota)}")

    def listar_notas(self):
        """RF02/RF21: lista todas as notas com a média recalculada."""
        self._titulo("Lista de notas")
        self._tabela_notas(self.sistema.notas.listar())

    def pesquisar_notas(self):
        """Pesquisa notas pela matrícula ou pelo código da disciplina."""
        termo = self._perguntar("Digite a matrícula ou o código da disciplina: ")
        if not termo:
            self._saida("Informe algum termo para pesquisar.")
            return
        self._titulo(f"Resultado da pesquisa por '{termo}'")
        self._tabela_notas(self.sistema.notas.pesquisar(termo))

    def alterar_nota(self):
        """RF24: altera notas e pesos (Enter mantém); a média é recalculada na hora."""
        identificacao = self._perguntar_identificacao_nota("a alterar")
        try:
            atual = self.sistema.notas.obter(identificacao)
        except (LookupError, ValueError) as erro:
            self._saida(str(erro))
            return
        self._saida(f"Registro atual: {atual}")
        self._saida("Pressione Enter para manter o valor atual de cada campo.")
        mudancas = {}
        for campo, rotulo in self.CAMPOS_NOTA:
            valor_atual = getattr(atual, campo)
            novo = self._perguntar(f"{rotulo} [{valor_atual}]: ")
            if novo and novo != str(valor_atual):
                mudancas[campo] = novo
        if not mudancas:
            self._saida("Nenhuma alteração informada.")
            return
        try:
            nota = self.sistema.notas.alterar(identificacao, **mudancas)
        except ERROS_ESPERADOS as erro:
            self._saida(f"Não foi possível alterar: {erro}")
        else:
            self._saida(f"Alterado com sucesso: {nota}")
            self._saida(f"Nova média: {self.sistema.notas.media(nota)}")

    def excluir_nota(self):
        """Exclui o registro de notas após confirmação."""
        identificacao = self._perguntar_identificacao_nota("a excluir")
        try:
            registro = self.sistema.notas.obter(identificacao)
        except (LookupError, ValueError) as erro:
            self._saida(str(erro))
            return
        self._saida(f"Registro: {registro}")
        if not self._confirmar("Confirma a exclusão?"):
            self._saida("Exclusão cancelada.")
            return
        try:
            self.sistema.notas.excluir(identificacao)
        except ERROS_ESPERADOS as erro:
            self._saida(f"Não foi possível excluir: {erro}")
        else:
            self._saida("Notas excluídas e arquivo .txt atualizado.")

    def rendimento(self):
        """RF23: relatório de rendimento escolar (aluno, disciplina, notas, média e status)."""
        self._titulo("Relatório de rendimento escolar")
        linhas = self.sistema.relatorio_rendimento()
        if not linhas:
            self._saida("Ainda não há notas lançadas.")
            return
        for numero, linha in enumerate(linhas, start=1):
            self._saida(f"{numero:>3}. Aluno: {linha.aluno} | Disciplina: {linha.disciplina}")
            self._saida(f"     Notas: {linha.texto_notas}")
            self._saida(f"     Média final: {linha.media} | Status: {linha.situacao}")

    # ---------- RF15 ----------
    def relatorio(self):
        """RF15: imprime o relatório integrado numerado."""
        self._titulo("Relatório integrado completo")
        frases = self.sistema.relatorio()
        if not frases:
            self._saida("Ainda não há alunos cadastrados para relacionar.")
        for numero, frase in enumerate(frases, start=1):
            self._saida(f"{numero:>3}. {frase}")

    # ---------- RF18 ----------
    def sair(self):
        """RF18: pede confirmação e encerra o laço principal."""
        if self._confirmar("Deseja realmente sair?"):
            self._finalizar()

    def _finalizar(self):
        """Encerra o laço e informa que os dados já estão gravados."""
        self._ativo = False
        self._saida(self.sistema.resumo_encerramento())
        self._saida("Sistema encerrado. Até logo!")
