# Referência da API

> ⚙️ **Arquivo gerado automaticamente** por `ferramentas/gerar_referencia_api.py` a partir das docstrings.
> Não edite à mão: altere a docstring no código e rode o script novamente.

## Módulos

- [`nucleo/entidade.py`](#nucleoentidadepy)
- [`nucleo/gerenciador.py`](#nucleogerenciadorpy)
- [`alfa/validacoes.py`](#alfavalidacoespy)
- [`alfa/curso.py`](#alfacursopy)
- [`alfa/aluno.py`](#alfaalunopy)
- [`alfa/gerenciadores.py`](#alfagerenciadorespy)
- [`beta/validacoes.py`](#betavalidacoespy)
- [`beta/professor.py`](#betaprofessorpy)
- [`beta/disciplina.py`](#betadisciplinapy)
- [`beta/integracao.py`](#betaintegracaopy)
- [`relatorios.py`](#relatoriospy)
- [`sistema.py`](#sistemapy)
- [`demonstracao.py`](#demonstracaopy)
- [`menu_console.py`](#menu_consolepy)
- [`interface_grafica.py`](#interface_graficapy)
- [`main.py`](#mainpy)

---

## `nucleo/entidade.py`

Ferramentas compartilhadas pelas entidades das equipes ALFA e BETA.

* :func:`propriedade` — cria um atributo protegido (``_nome``) acessado por ``@property``
  (getter + setter com validação), como pede o enunciado (Seção 4.A).
* ``validar_*`` — regras genéricas de formato, especializadas em ``alfa/validacoes.py``
  e ``beta/validacoes.py``.
* :func:`normalizar` — texto sem acentos e em minúsculas, para as pesquisas.
* :class:`Entidade` — base dos modelos de dados.

Convenção das funções ``validar_*``: recebem ``(texto, rotulo)``, devolvem o valor
normalizado e levantam ``ValueError`` com uma mensagem pronta para o usuário.

### `propriedade(nome, rotulo, validar=None)`

```text
Cria uma ``property`` com atributo protegido e validação no setter.

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
```

### `validar_codigo(texto, rotulo='Código')`

```text
Regra de identificadores: 1 a 24 caracteres ``[A-Za-z0-9_-]``, começando por letra ou número.

Returns:
    str: o próprio código.

Raises:
    ValueError: se o formato for inválido.
```

### `validar_nome(texto, rotulo='Nome')`

```text
Regra de nomes: 1 a 120 caracteres com ao menos uma letra.

Raises:
    ValueError: se a regra for violada.
```

### `validar_especialidade(texto, rotulo='Especialidade')`

```text
Regra da especialidade do professor: 1 a 120 caracteres com ao menos uma letra.

Raises:
    ValueError: se a regra for violada.
```

### `validar_cpf(texto, rotulo='CPF')`

```text
Exige 11 dígitos (com ou sem pontuação) e guarda sempre como 000.000.000-00.
```

### `validar_email(texto, rotulo='E-mail')`

```text
Valida o formato ``local@dominio.tld`` (até 254 caracteres, limite da RFC 5321).

Não verifica se a caixa postal existe; apenas o formato.

Raises:
    ValueError: se o formato for inválido.
```

### `validar_modalidade(texto, rotulo='Modalidade')`

```text
Aceita "presencial"/"ead" em qualquer caixa.

Returns:
    str: ``"Presencial"`` ou ``"EAD"`` (forma canônica gravada no .txt).

Raises:
    ValueError: para qualquer outro valor.
```

### `validar_carga_horaria(texto, rotulo='Carga horária')`

```text
Converte a carga horária para inteiro positivo.

Returns:
    int: número de horas.

Raises:
    ValueError: se não for inteiro maior que zero.
```

### `normalizar(texto)`

```text
Minúsculas e sem acentos, para pesquisas tolerantes.
```

### class `Entidade`

```text
Base das entidades: apenas modelo de dados.

Cada subclasse declara em CAMPOS a ordem dos seus atributos, que também é a ordem
das colunas no .txt. A entidade NÃO sabe ler nem gravar arquivos: isso é papel do
Gerenciador (dica do enunciado: regras nas classes gerenciadoras).
```

---

## `nucleo/gerenciador.py`

Gerenciador genérico: CRUD + persistência em .txt (usado por ALFA e BETA).

Padrão de erros (igual para todas as entidades):
  * ValueError  -> dado inválido, código duplicado ou regra de integridade violada
  * LookupError -> registro não encontrado

### class `Gerenciador`

```text
Repositório genérico de uma entidade, persistido em um arquivo .txt.

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
```

#### `__init__(self, arquivo)`

```text
Cria o gerenciador e já carrega o arquivo (RF11).

Args:
    arquivo (str | Path): caminho do .txt desta entidade.
```

#### `@property arquivo(self)`

```text
Path: caminho do arquivo .txt (somente leitura).
```

#### `@property chave(self)`

```text
Nome do campo identificador (sempre o primeiro campo do arquivo).
```

#### `identificador(self, obj)`

```text
Valor que identifica o registro (por padrão, o primeiro campo).

Subclasses com chave composta (ex.: notas = matrícula + disciplina) sobrescrevem
este gancho, :meth:`_normalizar_id` e :meth:`_texto_id`.
```

#### `_normalizar_id(self, codigo)`

```text
Converte o que o usuário informou na mesma forma devolvida por :meth:`identificador`.
```

#### `_texto_id(self, codigo)`

```text
Texto do identificador para mensagens de erro.
```

#### `_para_linha(self, obj)`

```text
Objeto -> 'campo;campo;campo\n', na ordem definida em CLASSE.CAMPOS.
```

#### `_de_linha(self, linha)`

```text
Linha do .txt -> objeto. Levanta ValueError se a linha estiver malformada.
```

#### `carregar(self)`

```text
Lê o .txt e converte cada linha em objeto. Linhas ruins vão para linhas_ignoradas.
```

#### `salvar(self)`

```text
Regrava o arquivo inteiro de forma segura (arquivo temporário + substituição).
```

#### `validar_vinculos(self, obj)`

```text
Verifica referências a outras entidades (ex.: o curso do aluno existe?).
```

#### `buscar(self, codigo)`

```text
Devolve o objeto ou None.
```

#### `obter(self, codigo)`

```text
Devolve o objeto ou levanta LookupError.
```

#### `listar(self)`

```text
RF02: devolve uma CÓPIA da lista de registros.

A cópia impede que quem chama altere a lista interna sem passar pelas regras.
```

#### `pesquisar(self, termo)`

```text
Pesquisa pelo código (exato) ou por pedaço do nome (sem diferenciar acentos).
```

#### `_checar_unicos(self, obj, ignorar=None)`

```text
Garante que os campos de CAMPOS_UNICOS não se repetem.

Args:
    obj: registro candidato.
    ignorar: registro a desconsiderar (o próprio, numa alteração).

Raises:
    ValueError: se já houver outro registro com o mesmo valor.
```

#### `cadastrar(self, obj)`

```text
RF01: valida, adiciona e grava um novo registro.

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
```

#### `alterar(self, codigo, **novos_dados)`

```text
RF04: altera qualquer atributo, inclusive o código. Tudo ou nada.

Se o código mudar, os registros que o referenciam (self.dependentes) são
atualizados juntos. Ex.: curso 10 -> 15 também troca o codigo_curso dos alunos e
das disciplinas que usavam 10. Assim nenhum vínculo fica órfão.
```

#### `_trocas_de_referencia(self, campo, antigo, novo)`

```text
Lista (gerenciador, índice, objeto novo) para os registros que usam `antigo` em `campo`.
```

#### `@staticmethod _desfazer(copias)`

```text
Volta a memória ao estado anterior e tenta regravar os arquivos (melhor esforço).
```

#### `excluir(self, codigo)`

```text
RF05: remove o registro pelo identificador e grava o arquivo.

Args:
    codigo (str): identificador do registro.

Returns:
    o objeto removido.

Raises:
    LookupError: se o código não existir.
    ValueError: se algum dependente ainda usar este código.
    OSError: falha ao gravar (o registro volta para a memória).
```

---

## `alfa/validacoes.py`

Regras de validação da equipe ALFA (Aluno e Curso).

Cada função recebe o texto já limpo por :func:`nucleo.entidade.propriedade` e devolve o
valor normalizado ou levanta ``ValueError`` com mensagem pronta para o usuário.
Especializam as regras genéricas de :mod:`nucleo.entidade` com rótulos próprios.

Arquitetura: depende somente de ``nucleo`` (ver docs/arquitetura/arc42.md, seção 5).

### `validar_matricula(valor, rotulo='Matrícula')`

```text
Valida a matrícula do aluno (1 a 24 caracteres alfanuméricos, ``_`` ou ``-``).

Raises:
    ValueError: se o formato for inválido.
```

### `validar_codigo_curso(valor, rotulo='Código do curso')`

```text
Valida o formato do código de curso (chave do Curso e vínculo do Aluno, RF13).
```

### `validar_nome_aluno(valor, rotulo='Nome do aluno')`

```text
Valida o nome do aluno (1 a 120 caracteres, ao menos uma letra).
```

### `validar_nome_curso(valor, rotulo='Nome do curso')`

```text
Valida o nome do curso (1 a 120 caracteres, ao menos uma letra).
```

### `validar_cpf_aluno(valor, rotulo='CPF')`

```text
Valida e formata o CPF do aluno.

Returns:
    str: CPF no formato ``000.000.000-00``.
```

### `validar_email_aluno(valor, rotulo='E-mail')`

```text
Valida o formato do e-mail (``nome@dominio.ext``, até 254 caracteres).
```

### `validar_modalidade_curso(valor, rotulo='Modalidade')`

```text
Valida a modalidade do curso.

Returns:
    str: ``"Presencial"`` ou ``"EAD"`` (normaliza maiúsculas/minúsculas).
```

---

## `alfa/curso.py`

Entidade Curso — Equipe ALFA (RF07).

Modelo de dados puro. O Curso é a entidade "raiz" dos vínculos: Aluno e Disciplina
apontam para ele pelo ``codigo_curso``.

### class `Curso`(Entidade)

```text
Programa oferecido pela instituição.

Attributes:
    codigo_curso (str): identificador único (chave do cursos.txt).
    nome (str): nome do curso.
    modalidade (str): ``"Presencial"`` ou ``"EAD"``.
```

#### `__init__(self, codigo_curso, nome, modalidade)`

```text
Cria o curso; os setters validam já na criação.

Raises:
    ValueError: se qualquer campo for inválido.
```

#### `__str__(self)`

```text
Representação legível usada nas listagens e mensagens.
```

---

## `alfa/aluno.py`

Entidade Aluno — Equipe ALFA (RF06).

Modelo de dados puro: guarda e valida os atributos. A existência do curso (RF13) é
verificada pelo GerenciadorAlunos, não aqui.

### class `Aluno`(Entidade)

```text
Discente matriculado em um curso.

Attributes:
    matricula (str): identificador único (chave do alunos.txt).
    nome (str): nome completo.
    cpf (str): CPF formatado ``000.000.000-00``; único entre alunos.
    email (str): e-mail de contato.
    codigo_curso (str): vínculo com Curso (RF13).
```

#### `__init__(self, matricula, nome, cpf, email, codigo_curso)`

```text
Cria o aluno validando cada campo.

Raises:
    ValueError: se qualquer campo for inválido.
```

#### `__str__(self)`

```text
Representação legível usada nas listagens e mensagens.
```

---

## `alfa/gerenciadores.py`

EQUIPE ALFA - gerenciadores (lógica de arquivo e listas) de Curso e Aluno.

Toda a mecânica de CRUD e persistência é herdada de :class:`nucleo.gerenciador.Gerenciador`;
aqui ficam apenas as configurações e regras específicas de cada entidade.

### class `GerenciadorCursos`(Gerenciador)

```text
CRUD e persistência de cursos (cursos.txt).

Os dependentes (alunos e disciplinas) são registrados pelo SistemaIntegrado, pois
a ALFA não conhece a BETA.
```

### class `GerenciadorAlunos`(Gerenciador)

```text
CRUD e persistência de alunos (alunos.txt), com validação do curso (RF13).

O CPF não pode se repetir entre alunos.
```

#### `__init__(self, arquivo, gerenciador_cursos)`

```text
Cria o gerenciador.

Args:
    arquivo (str | Path): caminho do alunos.txt.
    gerenciador_cursos (GerenciadorCursos): usado para checar se o curso existe.
```

#### `validar_vinculos(self, aluno)`

```text
RF13: o curso do aluno precisa existir.

Raises:
    ValueError: se o curso não estiver cadastrado.
```

---

## `beta/validacoes.py`

Regras de validação da equipe BETA (Professor e Disciplina).

Cada função recebe o texto já limpo (sem espaços nas pontas, sem ``;`` e sem caracteres
de controle, garantido por :func:`nucleo.entidade.propriedade`) e devolve o valor
normalizado ou levanta ``ValueError`` com uma mensagem pronta para o usuário.

As funções apenas especializam as regras genéricas de :mod:`nucleo.entidade` com um
rótulo próprio. Manter este arquivo por equipe permite que a BETA endureça uma regra
(ex.: formato do código do professor) sem afetar a ALFA.

Arquitetura: este módulo depende somente de ``nucleo``. A BETA NÃO importa nada da
ALFA (ver docs/adr/ADR-004).

### `validar_codigo_professor(valor, rotulo='Código do professor')`

```text
Valida o identificador do professor (1 a 24 caracteres alfanuméricos, ``_`` ou ``-``).

Returns:
    str: o próprio código.

Raises:
    ValueError: se o formato for inválido.
```

### `validar_codigo_disciplina(valor, rotulo='Código da disciplina')`

```text
Valida o identificador da disciplina (mesma regra de :func:`validar_codigo_professor`).
```

### `validar_codigo_curso(valor, rotulo='Código do curso')`

```text
Valida o FORMATO do código de curso usado como vínculo na Disciplina (RF14).

A existência do curso não é verificada aqui (a entidade não conhece outras
entidades); isso é feito por ``GerenciadorDisciplinas.validar_vinculos``.
```

### `validar_nome_professor(valor, rotulo='Nome do professor')`

```text
Valida o nome do professor (1 a 120 caracteres, ao menos uma letra).
```

### `validar_nome_disciplina(valor, rotulo='Nome da disciplina')`

```text
Valida o nome da disciplina (1 a 120 caracteres, ao menos uma letra).
```

### `validar_cpf_professor(valor, rotulo='CPF')`

```text
Valida e formata o CPF do professor.

Returns:
    str: CPF no formato ``000.000.000-00``.
```

### `validar_especialidade_professor(valor, rotulo='Especialidade')`

```text
Valida a especialidade do professor (1 a 120 caracteres, ao menos uma letra).
```

### `validar_carga_horaria_disciplina(valor, rotulo='Carga horária')`

```text
Valida a carga horária da disciplina.

Returns:
    int: número de horas (sempre maior que zero).
```

---

## `beta/professor.py`

Entidade Professor — Equipe BETA (RF08).

Modelo de dados puro: atributos protegidos expostos por ``@property`` com validação.

### class `Professor`(Entidade)

```text
Docente da instituição.

Attributes:
    codigo_professor (str): identificador único (chave do professores.txt).
    nome (str): nome completo.
    cpf (str): CPF formatado ``000.000.000-00``; único entre professores.
    especialidade (str): área de atuação.
```

#### `__init__(self, codigo_professor, nome, cpf, especialidade)`

```text
Cria o professor validando cada campo.

Raises:
    ValueError: se qualquer campo for inválido.
```

#### `__str__(self)`

```text
Representação legível usada nas listagens e mensagens.
```

---

## `beta/disciplina.py`

Entidade Disciplina — Equipe BETA (RF09).

Modelo de dados puro: guarda e valida os atributos, mas não sabe ler/gravar arquivos
nem verificar se o professor ou o curso existem (isso é do GerenciadorDisciplinas).

### class `Disciplina`(Entidade)

```text
Componente curricular ministrado por um professor dentro de um curso.

Attributes:
    codigo_disciplina (str): identificador único (chave do disciplinas.txt).
    nome (str): nome da disciplina.
    carga_horaria (int): total de horas, maior que zero.
    codigo_professor (str): vínculo com Professor (RF14).
    codigo_curso (str): vínculo com Curso da equipe ALFA (RF14).
```

#### `__init__(self, codigo_disciplina, nome, carga_horaria, codigo_professor, codigo_curso)`

```text
Cria a disciplina; cada atribuição passa pelo setter e é validada.

Raises:
    ValueError: se qualquer campo for inválido.
```

#### `__str__(self)`

```text
Representação legível usada nas listagens e mensagens.
```

---

## `beta/integracao.py`

EQUIPE BETA - gerenciadores de Professor e Disciplina e ponto de integração com a ALFA.

O :class:`SistemaBeta` funciona sozinho (útil para a BETA desenvolver e testar sem a
ALFA). Para validar o código do curso, basta informar um ``validador_curso`` (função que
recebe o código e devolve ``True``/``False``); sem ele, o código do curso é apenas
armazenado. Ver docs/adr/ADR-004.

### class `GerenciadorProfessores`(Gerenciador)

```text
CRUD e persistência de professores (professores.txt). O CPF não pode se repetir.
```

### class `GerenciadorDisciplinas`(Gerenciador)

```text
CRUD e persistência de disciplinas (disciplinas.txt), com validação de vínculos (RF14).
```

#### `__init__(self, arquivo, gerenciador_professores, validador_curso=None)`

```text
Cria o gerenciador.

Args:
    arquivo (str | Path): caminho do disciplinas.txt.
    gerenciador_professores (GerenciadorProfessores): usado para checar o professor.
    validador_curso (Callable[[str], bool] | None): diz se um código de curso existe.
        Sem ele, o curso não é verificado (modo BETA isolado).
```

#### `validar_vinculos(self, disciplina)`

```text
RF14: o professor deve existir e, se houver validador, o curso também.

Raises:
    ValueError: se o professor ou o curso não existir.
```

### class `SistemaBeta`

```text
Agrupa os gerenciadores da BETA e liga suas regras de integridade internas.

Attributes:
    professores (GerenciadorProfessores): gerenciador de professores.
    disciplinas (GerenciadorDisciplinas): gerenciador de disciplinas.
```

#### `__init__(self, pasta_dados, validador_curso=None)`

```text
Carrega professores.txt e disciplinas.txt da pasta informada.

Args:
    pasta_dados (str | Path): pasta onde estão os arquivos .txt.
    validador_curso (Callable[[str], bool] | None): ver GerenciadorDisciplinas.
```

#### `conectar_validador_curso(self, validador_curso)`

```text
Liga (ou troca) o validador de curso depois da criação.

Args:
    validador_curso (Callable[[str], bool]): função que diz se o curso existe.
```

---

## `relatorios.py`

RF15 - Relatório Integrado Completo.

Seguindo a dica do enunciado, a regra de negócio do relatório fica numa classe
gerenciadora própria (GerenciadorRelatorios). As entidades continuam sendo apenas
modelos de dados, e o SistemaIntegrado só faz a "costura" entre as equipes.

Por que dicionários? Antes, cada linha do relatório chamava `buscar()`, que percorre a
lista inteira (O(n)). Montando índices {codigo: objeto} uma única vez, cada consulta
passa a custar O(1), e o relatório inteiro fica O(alunos + disciplinas).

### class `LinhaRelatorio`

```text
Uma relação Aluno -> Curso -> Disciplina -> Professor já resolvida em nomes.
```

#### `@property frase(self)`

```text
Frase exatamente no formato exigido pelo RF15.
```

### class `GerenciadorRelatorios`

```text
Gera a listagem consolidada que relaciona as quatro entidades.
```

#### `__init__(self, cursos, alunos, professores, disciplinas)`

```text
Recebe os gerenciadores já carregados (injeção de dependência).

Args:
    cursos, alunos, professores, disciplinas: gerenciadores de cada entidade.
```

#### `gerar(self)`

```text
Devolve a lista de LinhaRelatorio, sempre a partir dos dados atuais em memória.
```

#### `frases(self)`

```text
Atalho usado pelas interfaces: só o texto de cada linha.
```

---

## `sistema.py`

Integração final: junta ALFA (Curso/Aluno) e BETA (Professor/Disciplina).

É a única peça que conhece as duas equipes. As interfaces (console e gráfica) só
conversam com o SistemaIntegrado, nunca diretamente com os arquivos .txt.

### class `SistemaIntegrado`

```text
Fachada (*Facade*) que monta e conecta os módulos ALFA e BETA.

É o único objeto que as interfaces usam. Cria os gerenciadores na ordem de
dependência, liga o validador de curso da BETA à ALFA e registra os dependentes
de cada entidade (integridade referencial entre equipes).

Attributes:
    cursos, alunos, professores, disciplinas: gerenciadores de cada entidade.
    beta (SistemaBeta): núcleo da equipe BETA.
    relatorios (GerenciadorRelatorios): gerador do relatório integrado (RF15).
    notas (GerenciadorNotas): notas e pesos por aluno e disciplina (RF19-RF20).
    rendimento (GerenciadorRendimento): relatório de rendimento escolar (RF23).
```

#### `__init__(self, pasta_dados=PASTA_DADOS)`

```text
Carrega todos os .txt da pasta e conecta as equipes (RF11).

Args:
    pasta_dados (str | Path): pasta com os quatro arquivos .txt.
```

#### `gerenciadores(self)`

```text
Lista os quatro gerenciadores na ordem de exibição.

Returns:
    list[Gerenciador]: cursos, alunos, professores e disciplinas.
```

#### `avisos_de_carga(self)`

```text
Mensagens sobre linhas dos .txt que não puderam ser lidas.
```

#### `relatorio(self)`

```text
RF15: frases do relatório integrado (a regra mora em GerenciadorRelatorios).
```

#### `relatorio_rendimento(self)`

```text
RF23: linhas do relatório de rendimento escolar (média recalculada a cada chamada).
```

#### `gerenciador(self, chave)`

```text
Devolve o gerenciador de uma entidade a partir da chave usada em ENTIDADES.
```

#### `resumo_encerramento(self)`

```text
RF18: texto exibido ao sair. Como o RF12 grava a cada operação, nada fica pendente.
```

---

## `demonstracao.py`

Integração Final (Seção 5 do enunciado) - demonstração guiada.

Executa, na ordem exigida, o fluxo completo de cadastro e depois mostra o relatório e o
conteúdo dos .txt (entregável "Demonstração": dados persistidos no arquivo de texto).

    python main.py --demo

Os registros usam códigos com prefixo DEMO para ficarem fáceis de identificar e excluir.
Rodar de novo não duplica nada: o que já existe é reaproveitado.
Toda gravação passa pelos gerenciadores, exatamente como no menu (nenhum atalho).

### `executar_demonstracao(sistema, saida=print, mostrar_arquivos=True)`

```text
Roda as quatro etapas. Devolve True se tudo deu certo, False se alguma falhou.
```

---

## `menu_console.py`

RF17 / RF18 - Menu de navegação via console e encerramento controlado.

O menu é genérico: lê os metadados de ENTIDADES (sistema.py) e funciona para as
quatro entidades sem repetir código. Toda regra de negócio continua nos
gerenciadores; aqui só existe "perguntar, chamar o gerenciador e mostrar o resultado".

`entrada` e `saida` são injetadas no construtor (por padrão input/print). Isso permite
testar o menu inteiro com respostas simuladas, sem ninguém digitando.

### class `MenuConsole`

```text
Interface de terminal (RF17) sobre o SistemaIntegrado.

Cada opção do menu é uma tupla (rótulo, função) num dicionário: adicionar uma
opção nova é acrescentar uma entrada, sem mexer no laço principal.
```

#### `__init__(self, sistema, entrada=input, saida=print)`

```text
Cria o menu.

Args:
    sistema (SistemaIntegrado): fachada com os gerenciadores.
    entrada (Callable[[str], str]): lê uma resposta (padrão ``input``).
    saida (Callable[[str], None]): exibe uma linha (padrão ``print``).
```

#### `_perguntar(self, texto)`

```text
Lê uma resposta do usuário já sem espaços nas pontas.
```

#### `_confirmar(self, texto)`

```text
Pergunta sim/não. Só ``s`` ou ``sim`` confirmam (padrão seguro = não).
```

#### `_titulo(self, texto)`

```text
Imprime um cabeçalho de seção.
```

#### `_escolher(self, titulo, opcoes)`

```text
Mostra um menu numerado e devolve a tecla escolhida (ou None se inválida).
```

#### `_tabela(self, meta, registros)`

```text
Imprime os registros alinhados em colunas (largura calculada pelo maior valor).
```

#### `@staticmethod _cortar(texto, largura)`

```text
Corta textos maiores que a coluna, indicando o corte com reticências.
```

#### `_dica_vinculo(self, campo, indice)`

```text
Para campos de vínculo (RF13/RF14), mostra os códigos disponíveis.
```

#### `executar(self)`

```text
Laço principal. Devolve 0 ao sair (código de saída do programa).
```

#### `_opcoes_principais(self)`

```text
Monta o menu principal a partir de ENTIDADES.

Returns:
    dict[str, tuple[str, Callable]]: tecla -> (rótulo, ação).
```

#### `_menu_entidade(self, chave)`

```text
Submenu de CRUD de uma entidade; volta ao menu principal com 0.
```

#### `cadastrar(self, chave)`

```text
RF01: pergunta todos os campos e cadastra pelo gerenciador.
```

#### `listar(self, chave)`

```text
RF02: lista todos os registros da entidade em tabela.
```

#### `pesquisar(self, chave)`

```text
RF03: pesquisa por código exato ou parte do nome.
```

#### `alterar(self, chave)`

```text
RF04: localiza pelo código e pergunta cada campo (Enter mantém o valor).

Só os campos efetivamente modificados são enviados ao gerenciador.
```

#### `excluir(self, chave)`

```text
RF05: localiza pelo código, mostra o registro e exclui após confirmação.
```

#### `_menu_notas(self)`

```text
Submenu do Módulo de Avaliação; volta ao menu principal com 0.
```

#### `_perguntar_identificacao_nota(self, acao)`

```text
Pergunta matrícula e disciplina (o par identifica o registro de notas).
```

#### `_tabela_notas(self, notas)`

```text
Tabela com notas, pesos e a média calculada agora (RF21).
```

#### `cadastrar_nota(self)`

```text
RF19/RF20: lança as três notas e pesos de um aluno em uma disciplina.
```

#### `listar_notas(self)`

```text
RF02/RF21: lista todas as notas com a média recalculada.
```

#### `pesquisar_notas(self)`

```text
Pesquisa notas pela matrícula ou pelo código da disciplina.
```

#### `alterar_nota(self)`

```text
RF24: altera notas e pesos (Enter mantém); a média é recalculada na hora.
```

#### `excluir_nota(self)`

```text
Exclui o registro de notas após confirmação.
```

#### `rendimento(self)`

```text
RF23: relatório de rendimento escolar (aluno, disciplina, notas, média e status).
```

#### `relatorio(self)`

```text
RF15: imprime o relatório integrado numerado.
```

#### `sair(self)`

```text
RF18: pede confirmação e encerra o laço principal.
```

#### `_finalizar(self)`

```text
Encerra o laço e informa que os dados já estão gravados.
```

---

## `interface_grafica.py`

RF17 - Painel acadêmico em Tkinter; reutiliza exclusivamente os gerenciadores do sistema.

Execução recomendada: python main.py (RF16). Necessita ambiente gráfico com Tkinter;
sem ele, o main.py abre automaticamente o menu de console.

### class `AplicacaoAcademica`(tk.Tk)

```text
Interface de CRUD generica, com menu lateral e relatorio integrado.
```

#### `__init__(self, sistema=None)`

```text
Monta a janela principal.

Args:
    sistema (SistemaIntegrado | None): fachada com os dados; se None, cria uma
        com a pasta padrão.

Raises:
    tkinter.TclError: se não houver ambiente gráfico.
```

#### `_estilizar(self)`

```text
Configura o tema ttk (tabela, cabeçalho, barra de rolagem e combobox).
```

#### `_texto(self, parent, value, size=11, color=INK, bold=False, **kwargs)`

```text
Atalho para criar um Label com a tipografia do sistema.
```

#### `_botao(self, parent, rotulo, callback, cor=ACCENT, fg=WHITE, **kwargs)`

```text
Atalho para criar um botão plano com as cores do sistema.
```

#### `_montar_estrutura(self)`

```text
Cria o layout fixo: barra lateral de navegação, topo e área de conteúdo.
```

#### `_limpar(self, titulo)`

```text
Remove o conteúdo atual da área central e troca o título do topo.
```

#### `_cartao(self, parent, **kwargs)`

```text
Cria um painel branco com borda (componente visual base).
```

#### `mostrar_inicio(self)`

```text
Tela 'Visão geral': contadores por entidade e atalhos.
```

#### `rodar_demonstracao(self)`

```text
Seção 5 do enunciado: roda o fluxo completo e abre o relatório com o resultado.
```

#### `mostrar_entidade(self, chave)`

```text
Tela de CRUD de uma entidade (RF01-RF05): busca, tabela e ações.

Args:
    chave (str): chave em ENTIDADES ("curso", "aluno", "professor", "disciplina").
```

#### `_atualizar_tabela(self)`

```text
Recarrega a tabela a partir da memória, aplicando o filtro de busca (RF02/RF03).
```

#### `_selecionar_acao(self, acao)`

```text
Executa 'alterar' ou 'excluir' sobre a linha selecionada.

Args:
    acao (str): ``"alterar"`` ou ``"excluir"``.
```

#### `_formulario(self, chave, registro=None)`

```text
Abre o formulário modal de cadastro (RF01) ou edição (RF04).

Campos de vínculo viram combobox com os códigos existentes, o que evita digitar
um código inválido. A validação definitiva continua nas entidades/gerenciadores.

Args:
    chave (str): chave em ENTIDADES.
    registro: registro a editar; None para um novo cadastro.
```

#### `mostrar_relatorio(self)`

```text
Tela do relatório integrado (RF15), somente leitura.
```

#### `mostrar_notas(self)`

```text
Tela de notas: tabela com a média recalculada a cada exibição (RF21/RF24).
```

#### `_atualizar_notas(self)`

```text
Relê o notas.txt (RF24) e recarrega a tabela com a média recalculada.
```

#### `_acao_nota(self, acao)`

```text
Edita ou exclui a nota selecionada na tabela.

Args:
    acao (str): ``"alterar"`` ou ``"excluir"``.
```

#### `_formulario_nota(self, registro=None)`

```text
Formulário modal para lançar (RF19) ou alterar (RF24) notas e pesos.

A matrícula e a disciplina viram combobox com os códigos existentes. A validação
definitiva (0.0 a 10.0, pesos, vínculos) continua na entidade e no gerenciador.

Args:
    registro (Nota | None): registro a editar; None para um novo lançamento.
```

#### `mostrar_rendimento(self)`

```text
Tela do relatório de rendimento escolar (RF23), somente leitura.
```

#### `encerrar(self)`

```text
RF18: confirma, informa que os dados já estão gravados e fecha a janela.
```

### `executar(sistema=None)`

```text
Abre a janela. Levanta RuntimeError se não houver ambiente gráfico (main.py trata).
```

---

## `main.py`

RF16 - Ponto de entrada único do Sistema de Gestão Acadêmica (ALFA + BETA).

Uso:
    python main.py              -> abre a interface gráfica (cai no console se não houver tela)
    python main.py --console    -> força o menu de terminal
    python main.py --relatorio  -> imprime o relatório integrado (RF15) e sai
    python main.py --rendimento -> imprime o relatório de rendimento escolar (RF23) e sai
    python main.py --demo       -> roda a Integração Final da Seção 5 do enunciado e sai

O SistemaIntegrado é criado UMA vez aqui (RF11: carrega todos os .txt para a memória)
e entregue pronto para a interface escolhida. Isso é injeção de dependência: as
interfaces não sabem de onde vêm os dados, só recebem o objeto que os gerencia.

### `criar_parser()`

```text
Monta o parser da linha de comando.

Returns:
    argparse.ArgumentParser: com os modos --console, --relatorio, --rendimento, --demo e a opção --dados.
```

### `abrir_interface_grafica(sistema)`

```text
Tenta abrir a GUI. Devolve False se o ambiente não suportar Tkinter.
```

### `main(argv=None)`

```text
Executa o sistema no modo pedido.

Args:
    argv (list[str] | None): argumentos (None = ``sys.argv``). Útil nos testes.

Returns:
    int: código de saída do processo (0 = sucesso).
```
