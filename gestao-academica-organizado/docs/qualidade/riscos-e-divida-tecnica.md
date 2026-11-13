# Riscos e Débito Técnico

Escalas: **P** = probabilidade, **I** = impacto (Baixo / Médio / Alto).
Revise este registro a cada versão (ver o [CHANGELOG](../../CHANGELOG.md)).

## 1. Riscos

| ID | Risco | P | I | Mitigação atual | Ação recomendada |
|----|-------|---|---|-----------------|------------------|
| R1 | **Duas instâncias abertas** sobre a mesma pasta: cada uma regrava o arquivo inteiro a partir da sua memória, e a última vence (*lost update*) | M | A | Documentado; uso previsto é monousuário | Arquivo de trava (`dados/.lock`) criado ao abrir e removido ao sair; ou migrar para SQLite (E1) |
| R2 | Queda de energia **entre** a gravação de dois arquivos numa alteração de código em cascata: o `cursos.txt` fica com o código novo e o `alunos.txt` com o antigo | B | M | Cada arquivo é atômico (ADR-005); a janela de risco é de milissegundos | Diário de transação (gravar a intenção antes e confirmar depois) ou SQLite |
| R3 | Edição manual dos `.txt` com erro | M | M | Linhas inválidas são ignoradas com aviso e `.bak` | Orientar o usuário a editar só pelo sistema |
| R4 | **Dados pessoais** (CPF, e-mail) em texto puro: exposição conforme a LGPD | M | A | Nenhuma além das permissões do sistema operacional | Restringir as permissões da pasta `dados/`; não versionar dados reais no Git; em produção, criptografia em repouso |
| R5 | Tkinter ausente ou sem servidor gráfico | M | B | Fallback automático para o console (ADR-007) | — |
| R6 | Endurecer uma validação faz linhas antigas serem ignoradas | M | M | Aviso na abertura + `.bak` | Seguir o alerta da receita 3 do guia de manutenção |

## 2. Débito técnico

| ID | Débito | Onde | Impacto | Correção sugerida | Esforço |
|----|--------|------|---------|-------------------|---------|
| D1 | Cada escrita regrava o arquivo inteiro (imposto pelo RF12) | `Gerenciador.salvar` | O(n) por escrita; perceptível acima de cerca de 100 mil registros | SQLite (E1) ou arquivo só de acréscimo com compactação | M |
| D2 | `buscar()` é linear | `Gerenciador.buscar` | O(n) por consulta; irrelevante no volume acadêmico | Índice `dict` {código: objeto} mantido junto com `_registros` | P |
| D3 | `sistema.ENTIDADES` repete os nomes de `Classe.CAMPOS` | `sistema.py` | Esquecer um dos dois causa um campo que não aparece na interface ou um `TypeError` no cadastro | Gerar `campos` a partir de `CAMPOS` + dicionário de rótulos, ou um teste que compare os dois | P |
| D4 | A GUI tem pontos fixos por entidade: navegação, cartões da visão geral e combobox de vínculos. O console tem um ponto, na dica de vínculo | `interface_grafica.py` (`_montar_estrutura`, `mostrar_inicio`, `_formulario`), `menu_console._dica_vinculo` | Uma nova entidade exige editar a GUI | Acrescentar a `ENTIDADES` as chaves `icone`, `descricao` e `vinculos: {campo: chave_entidade}` e gerar esses pontos a partir delas | M |
| D5 | O CPF valida só o formato, não os dígitos verificadores | `nucleo/entidade.validar_cpf` | Aceita CPFs inexistentes | Implementar o cálculo dos dígitos. **Atenção:** a massa de exemplo usa CPFs fictícios e precisaria ser trocada | P |
| D6 | `interface_grafica.py` concentra todas as telas numa classe (cerca de 450 linhas) | `AplicacaoAcademica` | Mais difícil de navegar | Separar em classes de tela (`TelaInicio`, `TelaEntidade`, `TelaRelatorio`) | M |
| D7 | Não há log de operações | — | Difícil auditar quem mudou o quê | Módulo `logging` gravando em `dados/operacoes.log` | P |
| D8 | A cascata acessa `_registros` de outro gerenciador | `Gerenciador.alterar` | Acoplamento interno, aceitável na mesma hierarquia | Manter; não replicar o padrão fora do `Gerenciador` | — |

Esforço: **P** = horas · **M** = 1 a 2 dias · **G** = mais que isso.

## 3. Evoluções possíveis (fora do escopo atual)

| ID | Evolução | Observação |
|----|----------|------------|
| E1 | Persistência em SQLite (`sqlite3`, biblioteca padrão) | Resolve R1, R2, D1 e D2 e dá chaves estrangeiras reais. Exige um ADR substituindo o ADR-001 e uma camada de migração |
| E2 | Matrícula individual de aluno em disciplina (tabela associativa) | Hoje o aluno "assiste" a todas as disciplinas do curso (RF15) |
| E3 | Exportar o relatório para CSV ou PDF | `GerenciadorRelatorios.gerar()` já devolve dados estruturados |
| E4 | Autenticação e perfis de acesso | Necessária se houver mais de um usuário |
