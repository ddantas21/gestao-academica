"""Ferramentas compartilhadas pelas entidades das equipes ALFA e BETA.

* :func:`propriedade` — cria um atributo protegido (``_nome``) acessado por ``@property``
  (getter + setter com validação), como pede o enunciado (Seção 4.A).
* ``validar_*`` — regras genéricas de formato, especializadas em ``alfa/validacoes.py``
  e ``beta/validacoes.py``.
* :func:`normalizar` — texto sem acentos e em minúsculas, para as pesquisas.
* :class:`Entidade` — base dos modelos de dados.

Convenção das funções ``validar_*``: recebem ``(texto, rotulo)``, devolvem o valor
normalizado e levantam ``ValueError`` com uma mensagem pronta para o usuário.
"""
import re
import unicodedata

# Separador do .txt (RF10). Fica aqui porque a validação dos campos precisa recusá-lo;
# o Gerenciador importa a mesma constante para ler e gravar os arquivos.
SEPARADOR = ";"

# Regras comuns às quatro entidades: centralizadas para terminal e GUI.
LIMITE_CODIGO = 24
LIMITE_NOME = 120
LIMITE_ESPECIALIDADE = 120


def propriedade(nome, rotulo, validar=None):
    """Cria uma ``property`` com atributo protegido e validação no setter.

    O valor fica guardado em ``self._<nome>``. A cada atribuição, o setter:

    1. converte para ``str`` e remove espaços nas pontas;
    2. recusa vazio, caracteres de controle (código < 32 ou 127) e o ``SEPARADOR``;
    3. aplica ``validar(texto, rotulo)``, se informado, e guarda o que ela devolver
       (é assim que o CPF ganha máscara e a carga horária vira ``int``).

    Args:
        nome (str): nome público do atributo (ex.: ``"cpf"``).
        rotulo (str): texto usado nas mensagens de erro (ex.: ``"O CPF"``).
        validar (Callable[[str, str], object] | None): regra específica do campo.

    Returns:
        property: para ser atribuída como atributo de classe.

    Raises:
        ValueError: (no setter) quando o valor viola alguma regra.

    Example:
        >>> class Exemplo:
        ...     nome = propriedade("nome", "O nome")
        >>> e = Exemplo(); e.nome = "  Ana  "; e.nome, e._nome
        ('Ana', 'Ana')
    """
    atributo = "_" + nome

    def getter(self):
        """Devolve o valor guardado no atributo protegido."""
        return getattr(self, atributo)

    def setter(self, valor):
        """Limpa, aplica as regras comuns e a regra específica, e guarda o valor."""
        texto = str(valor).strip()
        if texto == "":
            raise ValueError(f"{rotulo} não pode ficar vazio.")
        # Bloqueia TODOS os caracteres de controle (inclui ESC, usado em sequências ANSI que
        # poderiam manipular o terminal ao listar dados) e não só \n, \r e \x00.
        if any(ord(c) < 32 or ord(c) == 127 for c in texto):
            raise ValueError(f"{rotulo}: não use quebras de linha ou caracteres de controle.")
        if SEPARADOR in texto:
            raise ValueError(f"{rotulo}: não use '{SEPARADOR}' (é o separador do arquivo).")
        # `validar` pode converter o valor (ex.: formatar CPF, converter para int)
        setattr(self, atributo, validar(texto, rotulo) if validar else texto)

    return property(getter, setter)


def validar_codigo(texto, rotulo="Código"):
    """Regra de identificadores: 1 a 24 caracteres ``[A-Za-z0-9_-]``, começando por letra ou número.

    Returns:
        str: o próprio código.

    Raises:
        ValueError: se o formato for inválido.
    """
    if len(texto) > LIMITE_CODIGO or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]*", texto):
        raise ValueError(f"{rotulo}: use de 1 a {LIMITE_CODIGO} letras, números, _ ou -, começando por letra ou número.")
    return texto


def validar_nome(texto, rotulo="Nome"):
    """Regra de nomes: 1 a 120 caracteres com ao menos uma letra.

    Raises:
        ValueError: se a regra for violada.
    """
    if len(texto) < 1 or len(texto) > LIMITE_NOME or not any(c.isalpha() for c in texto):
        raise ValueError(f"{rotulo}: use de 1 a {LIMITE_NOME} caracteres, com pelo menos uma letra.")
    if any(ord(c) < 32 for c in texto):
        raise ValueError(f"{rotulo}: contém caracteres inválidos.")
    return texto


def validar_especialidade(texto, rotulo="Especialidade"):
    """Regra da especialidade do professor: 1 a 120 caracteres com ao menos uma letra.

    Raises:
        ValueError: se a regra for violada.
    """
    if len(texto) < 1 or len(texto) > LIMITE_ESPECIALIDADE or not any(c.isalpha() for c in texto):
        raise ValueError(f"{rotulo}: use de 1 a {LIMITE_ESPECIALIDADE} caracteres e pelo menos uma letra.")
    return texto


def validar_cpf(texto, rotulo="CPF"):
    """Exige 11 dígitos (com ou sem pontuação) e guarda sempre como 000.000.000-00."""
    if not re.fullmatch(r"(?:[0-9]{11}|[0-9]{3}\.[0-9]{3}\.[0-9]{3}-[0-9]{2})", texto):
        raise ValueError(f"{rotulo}: informe 11 dígitos ou 000.000.000-00.")
    numeros = "".join(c for c in texto if c.isdigit())
    if len(numeros) != 11:
        raise ValueError(f"{rotulo} inválido! Precisa ter 11 números.")
    return f"{numeros[0:3]}.{numeros[3:6]}.{numeros[6:9]}-{numeros[9:11]}"


def validar_email(texto, rotulo="E-mail"):
    """Valida o formato ``local@dominio.tld`` (até 254 caracteres, limite da RFC 5321).

    Não verifica se a caixa postal existe; apenas o formato.

    Raises:
        ValueError: se o formato for inválido.
    """
    if len(texto) > 254 or not re.fullmatch(r"[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)+", texto):
        raise ValueError(f"{rotulo} inválido! Exemplo: nome@email.com")
    return texto


def validar_modalidade(texto, rotulo="Modalidade"):
    """Aceita "presencial"/"ead" em qualquer caixa.

    Returns:
        str: ``"Presencial"`` ou ``"EAD"`` (forma canônica gravada no .txt).

    Raises:
        ValueError: para qualquer outro valor.
    """
    if texto.lower() == "presencial":
        return "Presencial"
    if texto.lower() == "ead":
        return "EAD"
    raise ValueError("A modalidade deve ser Presencial ou EAD.")


def validar_carga_horaria(texto, rotulo="Carga horária"):
    """Converte a carga horária para inteiro positivo.

    Returns:
        int: número de horas.

    Raises:
        ValueError: se não for inteiro maior que zero.
    """
    if not texto.isdigit() or int(texto) <= 0:
        raise ValueError("A carga horária deve ser um número inteiro maior que zero.")
    return int(texto)


def normalizar(texto):
    """Minúsculas e sem acentos, para pesquisas tolerantes."""
    sem_acento = unicodedata.normalize("NFD", str(texto))
    return "".join(c for c in sem_acento if not unicodedata.combining(c)).lower().strip()


class Entidade:
    """Base das entidades: apenas modelo de dados.

    Cada subclasse declara em CAMPOS a ordem dos seus atributos, que também é a ordem
    das colunas no .txt. A entidade NÃO sabe ler nem gravar arquivos: isso é papel do
    Gerenciador (dica do enunciado: regras nas classes gerenciadoras).
    """
    CAMPOS = ()
