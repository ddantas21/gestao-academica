# Changelog

Todas as mudanças relevantes deste projeto. Formato baseado em
[Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/) e versionamento
[SemVer](https://semver.org/lang/pt-BR/).

## [Não lançado]

_Nada ainda._

## [1.3.0] — 2026-11-09 — Módulo de Avaliação Acadêmica (RF19–RF24)

### Adicionado
- Pacote `avaliacao/` com a entidade `Nota` (matrícula, código da disciplina, três notas e
  três pesos), validações, `media_ponderada`/`status`, `GerenciadorNotas` e
  `GerenciadorRendimento` (ADR-011).
- Arquivo `dados/notas.txt` no formato `matricula;codigo_disciplina;nota1;peso1;nota2;peso2;nota3;peso3`.
- Média ponderada calculada na hora (nunca gravada), com `Decimal`, arredondada a 2 casas e
  limitada a 10.00; notas fora de 0.0–10.0 são recusadas; a vírgula decimal é aceita.
- Relatório de rendimento escolar: nome do aluno e da disciplina, notas e pesos, média final
  e status (Aprovado se média ≥ 7.0). Disponível em `python main.py --rendimento`, no menu
  de console (opções 7 e 8) e na GUI (telas "Notas" e "Rendimento escolar").
- Releitura do `notas.txt` antes de listar e de gravar: editar o arquivo à mão vale na
  leitura seguinte (RF24).
- 29 testes novos (`TestAvaliacao`) e a camada `avaliacao` nas fitness functions.

### Alterado
- `Gerenciador` ganhou os ganchos `identificador`, `_normalizar_id` e `_texto_id` para
  suportar chave composta; o comportamento das demais entidades não mudou.
- Aluno ou disciplina que já tenha notas não pode ser excluído; trocar a matrícula ou o
  código da disciplina atualiza o `notas.txt` junto (ADR-006).
- Menu de console: novas opções 7 (Notas e avaliação) e 8 (Rendimento escolar); a numeração
  anterior foi mantida.

## [1.2.0] — 2026-10-26 — Documentação técnica e reforço arquitetural

### Adicionado
- Documentação técnica completa em `docs/`: arc42 com diagramas C4 e UML, 10 ADRs,
  especificação de requisitos com rastreabilidade, modelo de dados, modelo de classes,
  guia de manutenção com receitas, estratégia de testes, registro de riscos e débito
  técnico, e glossário.
- `CONTRIBUTING.md` com padrões de código, docstrings, testes e versionamento.
- Referência da API gerada das docstrings (`ferramentas/gerar_referencia_api.py` →
  `docs/api/referencia.md`).
- Fitness functions em `testes/test_arquitetura.py`: regras de dependência, entidades
  como modelos de dados, cobertura de docstrings, existência dos documentos e
  atualização da referência; mais os doctests.
- Docstrings (Google Style) em 100% dos módulos, classes e funções de produção.
- Teste de leitura de arquivo com BOM.

### Corrigido
- **Acoplamento BETA → ALFA:** `beta/disciplina.py` importava `alfa.validacoes`. A BETA
  agora tem o seu próprio `validar_codigo_curso` (ADR-004).
- Arquivos `.txt` salvos com BOM (ex.: Bloco de Notas do Windows) tinham a primeira
  linha ignorada. A leitura agora usa `utf-8-sig`.

## [1.1.0] — 2026-10-26 — Novos requisitos RF01–RF18

### Adicionado
- `menu_console.py`: menu de terminal completo (RF17) com encerramento controlado (RF18),
  inclusive com Ctrl+C e Ctrl+D.
- `relatorios.py`: `GerenciadorRelatorios` (RF15), com índices em dicionário.
- `demonstracao.py`: Integração Final da Seção 5 do enunciado (`--demo`, opção 6 do
  console e botão na GUI).
- `main.py` com os modos `--console`, `--relatorio`, `--demo` e `--dados`, e fallback
  automático para o console sem Tkinter (RF16).
- Botão "Sair do sistema", confirmação no "X" da janela e Ctrl+Q na GUI (RF18).
- Alteração do código com **cascata** para os dependentes e rollback em falha de disco (RF04).
- Suíte de testes `testes/test_requisitos.py`.

### Alterado
- A conversão objeto ↔ linha do `.txt` saiu da `Entidade` e foi para o `Gerenciador`
  (ADR-008).
- O relatório saiu do `SistemaIntegrado` e foi para o `GerenciadorRelatorios` (ADR-009).

### Segurança
- Todos os caracteres de controle (incluindo ESC/ANSI) passaram a ser recusados em
  qualquer campo.

### Removido
- `Entidade.para_linha()`, substituído por `Gerenciador._para_linha()`.

## [1.0.0] — 2026-10-19 — Versão inicial (base recebida)

### Adicionado
- Entidades Aluno, Curso (ALFA), Professor e Disciplina (BETA) com `@property`.
- `Gerenciador` genérico com CRUD e persistência atômica em `.txt`.
- Vínculos Aluno → Curso e Disciplina → Professor/Curso, com bloqueio de exclusão.
- `SistemaIntegrado` e interface gráfica Tkinter.
