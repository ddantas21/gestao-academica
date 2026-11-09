"""Gerenciador genérico: CRUD + persistência em .txt (usado por ALFA e BETA).

Padrão de erros (igual para todas as entidades):
  * ValueError  -> dado inválido, código duplicado ou regra de integridade violada
  * LookupError -> registro não encontrado
"""
import os
from pathlib import Path

from .entidade import SEPARADOR, normalizar


class Gerenciador:
    """Repositório genérico de uma entidade, persistido em um arquivo .txt.

    Implementa RF01-RF05 (CRUD), RF10-RF12 (persistência) e a integridade referencial.
    Usa o padrão *Template Method*: o fluxo de ``cadastrar``/``alterar`` é fixo e as
    subclasses personalizam apenas o gancho :meth:`validar_vinculos`.

    Subclasses devem definir:
        ROTULO (str): nome da entidade nas mensagens (ex.: "aluno").
        CLASSE (type): classe da entidade (subclasse de Entidade).
        CAMPOS_UNICOS (tuple[str]): campos além da chave que não podem repetir.

    Attributes:
        dependentes (list[tuple[Gerenciador, str, str]]): quem referencia esta entidade,
            como (gerenciador, campo_de_vinculo, rótulo). Usado para bloquear exclusões
            e propagar a troca de código.
        linhas_ignoradas (list[str]): linhas do .txt que não puderam ser lidas.
    """
    ROTULO = "registro"      # usado nas mensagens
    CLASSE = None            # classe da entidade
    CAMPOS_UNICOS = ()       # campos além da chave que não podem repetir (ex.: cpf)

    def __init__(self, arquivo):
        """Cria o gerenciador e já carrega o arquivo (RF11).

        Args:
            arquivo (str | Path): caminho do .txt desta entidade.
        """
        self._arquivo = Path(arquivo)
        self._registros = []
        self.linhas_ignoradas = []   # linhas do .txt que não puderam ser lidas
        # Lista de (gerenciador, campo, rótulo): quem depende deste. Impede exclusões que
        # deixariam registros "órfãos" (ex.: excluir curso que ainda tem alunos).
        self.dependentes = []
        self.carregar()

    # ---------- propriedades ----------
    @property
    def arquivo(self):
        """Path: caminho do arquivo .txt (somente leitura)."""
        return self._arquivo

    @property
    def chave(self):
        """Nome do campo identificador (sempre o primeiro campo do arquivo)."""
        return self.CLASSE.CAMPOS[0]

    # ---------- identificação (ganchos para chaves compostas) ----------
    def identificador(self, obj):
        """Valor que identifica o registro (por padrão, o primeiro campo).

        Subclasses com chave composta (ex.: notas = matrícula + disciplina) sobrescrevem
        este gancho, :meth:`_normalizar_id` e :meth:`_texto_id`.
        """
        return getattr(obj, self.chave)

    def _normalizar_id(self, codigo):
        """Converte o que o usuário informou na mesma forma devolvida por :meth:`identificador`."""
        return str(codigo).strip()

    def _texto_id(self, codigo):
        """Texto do identificador para mensagens de erro."""
        return str(self._normalizar_id(codigo))

    # ---------- conversão objeto <-> linha do .txt (RF10) ----------
    def _para_linha(self, obj):
        """Objeto -> 'campo;campo;campo\\n', na ordem definida em CLASSE.CAMPOS."""
        return SEPARADOR.join(str(getattr(obj, campo)) for campo in self.CLASSE.CAMPOS) + "\n"

    def _de_linha(self, linha):
        """Linha do .txt -> objeto. Levanta ValueError se a linha estiver malformada."""
        partes = linha.rstrip("\r\n").split(SEPARADOR)
        if len(partes) != len(self.CLASSE.CAMPOS):
            raise ValueError("quantidade de campos diferente do esperado")
        # O construtor da entidade passa cada valor pelos setters, ou seja, valida tudo
        return self.CLASSE(*partes)

    # ---------- persistência (RF11 / RF12) ----------
    def carregar(self):
        """Lê o .txt e converte cada linha em objeto. Linhas ruins vão para linhas_ignoradas."""
        self._registros = []
        self.linhas_ignoradas = []
        if not self._arquivo.exists():
            return
        vistos = set()
        # utf-8-sig aceita arquivos salvos com BOM (ex.: Bloco de Notas do Windows);
        # sem isso, o BOM grudaria no primeiro código e a primeira linha seria ignorada.
        with open(self._arquivo, "r", encoding="utf-8-sig") as arq:
            for linha in arq:
                if linha.strip() == "":
                    continue
                try:
                    obj = self._de_linha(linha)
                    codigo = self.identificador(obj)
                    if codigo in vistos:
                        raise ValueError("código repetido")
                    vistos.add(codigo)
                    self._registros.append(obj)
                except ValueError:
                    self.linhas_ignoradas.append(linha.rstrip("\r\n"))

    def salvar(self):
        """Regrava o arquivo inteiro de forma segura (arquivo temporário + substituição)."""
        self._arquivo.parent.mkdir(parents=True, exist_ok=True)
        if self.linhas_ignoradas and self._arquivo.exists():
            # Para não perder linhas que o programa não entendeu, guarda cópia antes de regravar.
            copia = self._arquivo.with_suffix(self._arquivo.suffix + ".bak")
            if not copia.exists():
                copia.write_bytes(self._arquivo.read_bytes())
        temporario = self._arquivo.with_suffix(self._arquivo.suffix + ".tmp")
        with open(temporario, "w", encoding="utf-8", newline="\n") as arq:
            for obj in self._registros:
                arq.write(self._para_linha(obj))
        os.replace(temporario, self._arquivo)

    # ---------- ganchos para as subclasses ----------
    def validar_vinculos(self, obj):
        """Verifica referências a outras entidades (ex.: o curso do aluno existe?)."""

    # ---------- consultas ----------
    def buscar(self, codigo):
        """Devolve o objeto ou None."""
        codigo = self._normalizar_id(codigo)
        for obj in self._registros:
            if self.identificador(obj) == codigo:
                return obj
        return None

    def obter(self, codigo):
        """Devolve o objeto ou levanta LookupError."""
        obj = self.buscar(codigo)
        if obj is None:
            raise LookupError(f"{self.ROTULO.capitalize()} '{self._texto_id(codigo)}' não encontrado.")
        return obj

    def listar(self):
        """RF02: devolve uma CÓPIA da lista de registros.

        A cópia impede que quem chama altere a lista interna sem passar pelas regras.
        """
        return list(self._registros)

    def pesquisar(self, termo):
        """Pesquisa pelo código (exato) ou por pedaço do nome (sem diferenciar acentos)."""
        termo_n = normalizar(termo)
        if termo_n == "":
            return []
        return [o for o in self._registros
                if normalizar(getattr(o, self.chave)) == termo_n or termo_n in normalizar(o.nome)]

    # ---------- CRUD ----------
    def _checar_unicos(self, obj, ignorar=None):
        """Garante que os campos de CAMPOS_UNICOS não se repetem.

        Args:
            obj: registro candidato.
            ignorar: registro a desconsiderar (o próprio, numa alteração).

        Raises:
            ValueError: se já houver outro registro com o mesmo valor.
        """
        for campo in self.CAMPOS_UNICOS:
            for outro in self._registros:
                if outro is not ignorar and getattr(outro, campo) == getattr(obj, campo):
                    raise ValueError(f"Já existe {self.ROTULO} com este {campo.upper()}: "
                                     f"{getattr(obj, campo)}.")

    def cadastrar(self, obj):
        """RF01: valida, adiciona e grava um novo registro.

        Ordem das checagens: tipo -> código duplicado -> campos únicos -> vínculos.
        Se a gravação falhar, o registro é retirado da memória (memória e disco iguais).

        Args:
            obj: instância de CLASSE já validada pelo construtor.

        Returns:
            o próprio objeto cadastrado.

        Raises:
            TypeError: se ``obj`` não for da classe esperada.
            ValueError: código/campo único duplicado ou vínculo inexistente.
            OSError: falha ao gravar o arquivo.
        """
        if not isinstance(obj, self.CLASSE):
            raise TypeError(f"Esperado objeto {self.CLASSE.__name__}.")
        codigo = self.identificador(obj)
        if self.buscar(codigo) is not None:
            raise ValueError(f"Já existe {self.ROTULO} com o código {self._texto_id(codigo)}.")
        self._checar_unicos(obj)
        self.validar_vinculos(obj)
        self._registros.append(obj)
        try:
            self.salvar()
        except OSError:
            self._registros.pop()
            raise
        return obj

    def alterar(self, codigo, **novos_dados):
        """RF04: altera qualquer atributo, inclusive o código. Tudo ou nada.

        Se o código mudar, os registros que o referenciam (self.dependentes) são
        atualizados juntos. Ex.: curso 10 -> 15 também troca o codigo_curso dos alunos e
        das disciplinas que usavam 10. Assim nenhum vínculo fica órfão.
        """
        atual = self.obter(codigo)
        codigo_antigo = self.identificador(atual)
        desconhecidos = set(novos_dados) - set(self.CLASSE.CAMPOS)
        if desconhecidos:
            raise ValueError(f"Campos desconhecidos: {', '.join(sorted(desconhecidos))}.")
        dados = {campo: getattr(atual, campo) for campo in self.CLASSE.CAMPOS}
        dados.update(novos_dados)
        candidato = self.CLASSE(**dados)          # valida tudo antes de mexer no original
        codigo_novo = self.identificador(candidato)
        if codigo_novo != codigo_antigo and self.buscar(codigo_novo) is not None:
            raise ValueError(f"Já existe {self.ROTULO} com o código {self._texto_id(codigo_novo)}.")
        self._checar_unicos(candidato, ignorar=atual)
        self.validar_vinculos(candidato)

        # Monta TODAS as trocas antes de aplicar qualquer uma: se algo for inválido,
        # o erro acontece aqui e nada na memória ou no disco foi tocado.
        trocas = [(self, self._registros.index(atual), candidato)]
        if codigo_novo != codigo_antigo:
            for ger, campo, _ in self.dependentes:
                trocas += ger._trocas_de_referencia(campo, codigo_antigo, codigo_novo)

        envolvidos = list(dict.fromkeys(ger for ger, _, _ in trocas))   # sem repetir, em ordem
        copias = {ger: list(ger._registros) for ger in envolvidos}
        for ger, indice, novo in trocas:
            ger._registros[indice] = novo
        try:
            for ger in envolvidos:
                ger.salvar()                      # RF12: sincroniza cada arquivo afetado
        except OSError:
            self._desfazer(copias)
            raise
        return candidato

    def _trocas_de_referencia(self, campo, antigo, novo):
        """Lista (gerenciador, índice, objeto novo) para os registros que usam `antigo` em `campo`."""
        trocas = []
        for indice, registro in enumerate(self._registros):
            if getattr(registro, campo) == antigo:
                dados = {c: getattr(registro, c) for c in self.CLASSE.CAMPOS}
                dados[campo] = novo
                trocas.append((self, indice, self.CLASSE(**dados)))
        return trocas

    @staticmethod
    def _desfazer(copias):
        """Volta a memória ao estado anterior e tenta regravar os arquivos (melhor esforço)."""
        for ger, registros in copias.items():
            ger._registros = registros
            try:
                ger.salvar()
            except OSError:
                pass   # o erro original já será propagado para o usuário

    def excluir(self, codigo):
        """RF05: remove o registro pelo identificador e grava o arquivo.

        Args:
            codigo (str): identificador do registro.

        Returns:
            o objeto removido.

        Raises:
            LookupError: se o código não existir.
            ValueError: se algum dependente ainda usar este código.
            OSError: falha ao gravar (o registro volta para a memória).
        """
        obj = self.obter(codigo)
        codigo = self.identificador(obj)
        for ger, campo, rotulo in self.dependentes:
            usados = [r for r in ger.listar() if getattr(r, campo) == codigo]
            if usados:
                raise ValueError(f"Não é possível excluir: {len(usados)} {rotulo} "
                                 f"ainda usa(m) o código {self._texto_id(codigo)}.")
        indice = self._registros.index(obj)
        self._registros.pop(indice)
        try:
            self.salvar()
        except OSError:
            self._registros.insert(indice, obj)
            raise
        return obj
