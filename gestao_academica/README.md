# Sistema de Gestão Acadêmica (ALFA + BETA)

Sistema em Python, orientado a objetos, para gerenciar **Alunos, Cursos, Professores e
Disciplinas**. Os dados ficam em arquivos `.txt` e há duas interfaces: gráfica (Tkinter)
e console.

> 📚 **Vai manter ou alterar o código?** Comece pela [documentação técnica](docs/README.md):
> arquitetura (arc42 + C4), decisões (ADRs), modelo de dados e de classes, guia de
> manutenção com receitas passo a passo, e a [referência da API](docs/api/referencia.md).
> Padrões de código em [CONTRIBUTING.md](CONTRIBUTING.md) e histórico em [CHANGELOG.md](CHANGELOG.md).

## Integrantes

> **Preencher antes da entrega.**

| Equipe | Integrante | Responsabilidade |
|--------|------------|------------------|
| ALFA | _Nome completo_ | Módulo Aluno |
| ALFA | _Nome completo_ | Módulo Curso |
| BETA | _Nome completo_ | Módulo Professor |
| BETA | _Nome completo_ | Módulo Disciplina |
| ALFA + BETA | _Nome completo_ | Integração final (`main.py`, interfaces) |

## Como executar

Requer Python 3.10 ou superior. Não há dependências externas.

```bash
python main.py              # interface gráfica (abre o console se não houver Tkinter ou tela)
python main.py --console    # força o menu de terminal
python main.py --demo       # Integração Final: cadastra tudo em ordem e mostra relatório e .txt
python main.py --relatorio  # imprime o relatório integrado e encerra
python main.py --rendimento # imprime o relatório de rendimento escolar (notas e médias) e encerra
python main.py --dados outra_pasta   # usa outra pasta de arquivos .txt
```

Testes automatizados (rodam numa pasta temporária e não alteram `dados/`):

```bash
python -m unittest discover -s testes -v      # requisitos + arquitetura + doctests
python ferramentas/gerar_referencia_api.py    # regenera docs/api/referencia.md
```

## Estrutura

```
gestao_academica/
├── main.py               RF16  ponto de entrada único
├── sistema.py                  integração ALFA + BETA (SistemaIntegrado)
├── relatorios.py         RF15  GerenciadorRelatorios
├── demonstracao.py             Integração Final (Seção 5 do enunciado)
├── menu_console.py       RF17/RF18  menu de terminal
├── interface_grafica.py  RF17/RF18  interface Tkinter (Desafio)
├── nucleo/
│   ├── entidade.py             validações comuns + base Entidade (só dados)
│   └── gerenciador.py    RF01–RF05, RF10–RF12  CRUD genérico + persistência
├── avaliacao/            RF19–RF24  Módulo de Avaliação: Nota, média ponderada,
│                         GerenciadorNotas, GerenciadorRendimento
├── alfa/                 Equipe ALFA: Aluno, Curso, GerenciadorAlunos, GerenciadorCursos
├── beta/                 Equipe BETA: Professor, Disciplina, GerenciadorProfessores,
│                         GerenciadorDisciplinas, SistemaBeta
├── dados/                alunos.txt, cursos.txt, professores.txt, disciplinas.txt, notas.txt
├── testes/
│   ├── test_requisitos.py      RF01–RF24, requisitos técnicos e Integração Final
│   └── test_arquitetura.py     fitness functions (dependências, docstrings, docs) + doctests
├── ferramentas/
│   └── gerar_referencia_api.py gera docs/api/referencia.md das docstrings
├── docs/                 documentação técnica (ver docs/README.md)
├── CONTRIBUTING.md       padrões de código e documentação
└── CHANGELOG.md          histórico de versões
```

### Decisão de arquitetura

As **entidades** (`Aluno`, `Curso`, `Professor`, `Disciplina`) são apenas modelos de
dados. Elas têm `__init__` e `__str__` e guardam atributos protegidos (`_nome`, `_cpf`…),
expostos por `@property` com getter e setter que valida o valor. As entidades não sabem
ler nem gravar arquivos.

Todos os requisitos funcionais ficam nas **classes gerenciadoras**, como pede a dica do
enunciado. A classe base `Gerenciador` reúne o CRUD, a conversão objeto ↔ linha do
`.txt`, a leitura, a gravação e a integridade dos vínculos. `GerenciadorAlunos`,
`GerenciadorCursos`, `GerenciadorProfessores` e `GerenciadorDisciplinas` herdam dela e
acrescentam as regras de cada módulo. O relatório fica no `GerenciadorRelatorios`.

As interfaces só chamam os gerenciadores, por isso console e GUI se comportam exatamente
igual. Detalhes em [docs/arquitetura/arc42.md](docs/arquitetura/arc42.md) e nos
[ADRs](docs/adr/README.md).

## Rastreabilidade dos requisitos

| RF | Requisito | Onde está implementado |
|----|-----------|------------------------|
| RF01 | Cadastrar | `Gerenciador.cadastrar` (`nucleo/gerenciador.py`) |
| RF02 | Listar | `Gerenciador.listar` + tabelas formatadas no console e na GUI |
| RF03 | Pesquisar por código ou nome | `Gerenciador.pesquisar` (código exato ou parte do nome, sem diferenciar acentos) |
| RF04 | Alterar qualquer atributo | `Gerenciador.alterar`, inclusive o código, com atualização em cascata dos vínculos |
| RF05 | Excluir pelo identificador | `Gerenciador.excluir` (bloqueia se houver registros dependentes) |
| RF06 | Aluno: matrícula, nome, CPF, e-mail, código do curso | `alfa/aluno.py` |
| RF07 | Curso: código, nome, modalidade (Presencial/EAD) | `alfa/curso.py` |
| RF08 | Professor: código, nome, CPF, especialidade | `beta/professor.py` |
| RF09 | Disciplina: código, nome, carga horária, cód. professor, cód. curso | `beta/disciplina.py` |
| RF10 | Arquivos `.txt` separados por `;` | `Gerenciador._para_linha` / `_de_linha` + `salvar` |
| RF11 | Carregamento inicial | `Gerenciador.carregar`, chamado no construtor; o `main.py` cria o sistema uma vez |
| RF12 | Sincronização de escrita | `cadastrar`, `alterar` e `excluir` chamam `salvar()` ao terminar |
| RF13 | Aluno ↔ Curso | `GerenciadorAlunos.validar_vinculos` |
| RF14 | Disciplina ↔ Professor e Curso | `GerenciadorDisciplinas.validar_vinculos` |
| RF15 | Relatório integrado | `GerenciadorRelatorios.gerar` (`relatorios.py`) |
| RF16 | Ponto de entrada único | `main.py` |
| RF17 | Menu de navegação | `menu_console.py` e `interface_grafica.py` |
| RF18 | Encerramento controlado | console: opção "0 - Sair" com confirmação, Ctrl+C/Ctrl+D tratados. GUI: botão "Sair", "X" da janela e Ctrl+Q |
| RF19 | Estrutura de notas (matrícula, disciplina, 3 notas e 3 pesos) | `avaliacao/nota.py`, `GerenciadorNotas.validar_vinculos` |
| RF20 | Persistência em `notas.txt` (`matricula;disciplina;n1;p1;n2;p2;n3;p3`) | `Gerenciador._para_linha` / `_de_linha` com `Nota.CAMPOS` |
| RF21 | Média ponderada calculada em tempo de execução | `avaliacao/calculo.py` → `media_ponderada` |
| RF22 | Notas de 0.0 a 10.0 e média limitada a 10.0 | `avaliacao/validacoes.py` e teto em `media_ponderada` |
| RF23 | Relatório de rendimento (nomes, notas, pesos, média, status) | `GerenciadorRendimento.gerar`; `--rendimento`, console (opção 8) e GUI "Rendimento escolar" |
| RF24 | Alteração e recálculo automático | a média não é gravada; `GerenciadorNotas.listar` relê o `notas.txt` |

### Requisitos do enunciado original (PDF)

| Item | Onde está |
|------|-----------|
| 4.A Classes com `__init__` e `__str__` | as quatro entidades |
| 4.A Encapsulamento com `@property` | `nucleo/entidade.py` → função `propriedade` |
| 4.A Classes gerenciadoras | `alfa/gerenciadores.py`, `beta/integracao.py`, `relatorios.py` |
| 4.B Carregar ao iniciar / salvar ao finalizar escrita | RF11 e RF12 |
| 4.C Acordo de IDs entre equipes | `codigo_curso` da ALFA usado pela BETA via `validador_curso` |
| 5 Integração Final no `main.py` | `python main.py --demo`, opção 6 do console ou botão "Executar demonstração" na GUI |
| Desafio: interface gráfica | `interface_grafica.py` |

## Formato escolhido para o `.txt`

Cada arquivo guarda uma entidade, com um registro por linha e os campos separados por
`;`, na ordem definida em `CAMPOS` de cada classe. O dicionário de dados completo está em
[docs/projeto/modelo-de-dados.md](docs/projeto/modelo-de-dados.md).

```
cursos.txt       codigo_curso;nome;modalidade
alunos.txt       matricula;nome;cpf;email;codigo_curso
professores.txt  codigo_professor;nome;cpf;especialidade
disciplinas.txt  codigo_disciplina;nome;carga_horaria;codigo_professor;codigo_curso
```

**Por que esse formato:**

- **Legível:** dá para conferir o arquivo num editor comum durante a demonstração.
- **Fácil de processar:** `split(";")` resolve a leitura.
- **Sem conflito com os dados:** o `;` não aparece em nomes, e-mails ou CPFs, então o
  sistema simplesmente o recusa nos campos.
- **Vínculos por código:** a primeira coluna é sempre o identificador único. Os vínculos
  entre arquivos usam esses códigos, como uma chave estrangeira.
- **Padronização:** o CPF é gravado sempre com máscara (`000.000.000-00`) e a modalidade
  sempre como `Presencial` ou `EAD`, para que buscas e comparações funcionem.
- **Codificação:** UTF-8, para preservar os acentos. Arquivos salvos com BOM também são aceitos.

**Divergência do enunciado:** o exemplo de linha do enunciado
(`202301;João Silva;123.456.789-00;10`) não traz o e-mail, embora o Módulo Aluno e o
RF06 o exijam. Seguimos os atributos obrigatórios, e o `alunos.txt` tem 5 colunas.

**Robustez:** linhas corrompidas são ignoradas na leitura e informadas ao usuário. Antes
da primeira regravação de um arquivo nessa situação, o sistema guarda uma cópia `.bak`. A
gravação usa um arquivo temporário seguido de `os.replace`, então uma queda no meio da
escrita não deixa o `.txt` pela metade.

## Dificuldades encontradas na integração

> **Revisar e adaptar com a experiência real da equipe.** Os pontos abaixo são os
> desafios técnicos que o próprio código resolve e servem de base para o texto final.

1. **Dependência entre as equipes.** A BETA precisa validar o `codigo_curso`, mas o
   Curso pertence à ALFA. Para a BETA funcionar e ser testada sozinha, o `SistemaBeta`
   recebe uma função `validador_curso`, e a ligação com a ALFA só acontece no
   `SistemaIntegrado`.
2. **Ordem de carregamento.** Alunos dependem de cursos, e disciplinas dependem de
   professores e cursos. Os gerenciadores precisam ser criados nessa ordem.
3. **Registros órfãos.** Excluir um curso que ainda tem alunos quebraria o relatório.
   Criamos a lista `dependentes`, que bloqueia essas exclusões.
4. **Troca de código.** Para permitir alterar o código (RF04) sem perder vínculos, a
   alteração atualiza em cascata os arquivos dependentes. Se a gravação falhar no meio,
   tudo é desfeito.
5. **Padronização dos dados.** CPF com e sem máscara e "ead" em minúsculas geravam
   duplicidades e buscas falhas. A solução foi normalizar o valor no setter.
6. **Duas interfaces com o mesmo comportamento.** Toda regra ficou nos gerenciadores,
   e console e GUI só chamam esses métodos.

## Roteiro para a demonstração

1. Mostre os arquivos de `dados/` abertos num editor.
2. Rode `python main.py`, clique em **Executar demonstração** e mostre o relatório. No
   console, use a opção 6 ou `python main.py --demo`.
3. Reabra os `.txt` e mostre as linhas `DEMO-…` gravadas.
4. Faça um cadastro manual pelo menu e mostre a nova linha no arquivo.
5. Tente excluir o curso `DEMO-C` para mostrar que o sistema bloqueia vínculos órfãos.
6. Saia pelo botão **Sair do sistema** (RF18).

A demonstração pode rodar várias vezes sem duplicar registros. Para limpar, exclua pelo
menu os registros `DEMO-…`, nesta ordem: aluno, disciplina, curso e professor.

## Regras de validação

| Campo | Regra |
|-------|-------|
| Códigos / matrícula | 1 a 24 caracteres: letras, números, `_` ou `-` |
| Nome / especialidade | 1 a 120 caracteres, com pelo menos uma letra |
| CPF | 11 dígitos, com ou sem máscara; gravado como `000.000.000-00`; único por entidade |
| E-mail | formato `nome@dominio.ext` (até 254 caracteres) |
| Modalidade | `Presencial` ou `EAD` (aceita minúsculas) |
| Carga horária | inteiro maior que zero |
| Todos | não pode ficar vazio, conter `;` ou caracteres de controle |

## Segurança e desempenho

- **Injeção no arquivo:** `;`, quebras de linha e qualquer caractere de controle são
  recusados em todos os campos. Assim, ninguém consegue criar colunas ou linhas falsas
  nem enviar sequências ANSI que mexam no terminal.
- **Integridade referencial:** não dá para cadastrar aluno ou disciplina com curso ou
  professor inexistente, nem excluir curso ou professor que ainda tenha vínculos.
- **Alteração atômica:** a alteração monta todas as trocas antes de aplicar a primeira.
  Se a gravação falhar, a memória e os arquivos voltam ao estado anterior.
- **Relatório:** usa índices em dicionário (`{codigo: objeto}`), com custo
  O(alunos + disciplinas) em vez de buscas lineares repetidas.
- **Limitação conhecida:** como pede o RF12, cada escrita regrava o arquivo inteiro.
  Isso é ótimo para centenas ou milhares de registros. Para volumes muito maiores, o
  caminho natural seria um banco de dados como o SQLite.
