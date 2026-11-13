# Guia de Manutenção

Um guia prático para quem vai corrigir ou estender o sistema. Leia antes a
[seção 5 do arc42](../arquitetura/arc42.md#5-visão-de-blocos-de-construção) para
entender as camadas.

## Sumário

- [1. Preparar o ambiente](#1-preparar-o-ambiente)
- [2. Mapa rápido: onde mexer](#2-mapa-rápido-onde-mexer)
- [3. Receitas](#3-receitas)
  - [Receita 1 — Adicionar um campo a uma entidade](#receita-1--adicionar-um-campo-a-uma-entidade)
  - [Receita 2 — Adicionar uma nova entidade](#receita-2--adicionar-uma-nova-entidade)
  - [Receita 3 — Mudar ou criar uma regra de validação](#receita-3--mudar-ou-criar-uma-regra-de-validação)
  - [Receita 4 — Adicionar um vínculo entre entidades](#receita-4--adicionar-um-vínculo-entre-entidades)
  - [Receita 5 — Adicionar uma opção ao menu ou um novo relatório](#receita-5--adicionar-uma-opção-ao-menu-ou-um-novo-relatório)
  - [Receita 6 — Migrar os arquivos .txt](#receita-6--migrar-os-arquivos-txt)
- [4. Solução de problemas](#4-solução-de-problemas)
- [5. Checklist antes de entregar uma mudança](#5-checklist-antes-de-entregar-uma-mudança)

---

## 1. Preparar o ambiente

```bash
python --version          # 3.10 ou superior
cd gestao_academica
python -m unittest discover -s testes -v    # tudo deve passar antes de começar
python main.py --console  # conferir o sistema rodando
```

- **VS Code:** `.vscode/launch.json` já traz três configurações: GUI, Console e Testes.
- **Sem Tkinter no Linux:** `sudo apt install python3-tk`, ou use `--console`.
- **Não trabalhe sobre `dados/` reais** ao experimentar. Use uma cópia:
  `python main.py --dados /tmp/copia_dados`.

## 2. Mapa rápido: onde mexer

| Quero… | Arquivo(s) |
|--------|-----------|
| Mudar uma regra de formato (CPF, e-mail, tamanho do nome) | `nucleo/entidade.py` (genérica) ou `alfa/validacoes.py`, `beta/validacoes.py` (por equipe) |
| Mudar um atributo de uma entidade | `alfa/aluno.py`, `alfa/curso.py`, `beta/professor.py`, `beta/disciplina.py` + `sistema.py` (ENTIDADES) |
| Mudar como o CRUD ou a gravação funcionam | `nucleo/gerenciador.py` (afeta as quatro entidades!) |
| Mudar uma regra de vínculo | `validar_vinculos` em `alfa/gerenciadores.py` ou `beta/integracao.py` |
| Mudar notas, pesos, média ou o critério de aprovação | `avaliacao/validacoes.py` (regras), `avaliacao/calculo.py` (média, `MEDIA_APROVACAO`, teto), `avaliacao/gerenciadores.py` (vínculos e relatório) |
| Mudar quem bloqueia a exclusão de quem | `dependentes` em `sistema.py` e `beta/integracao.py` |
| Mudar o texto do relatório | `relatorios.py` → `LinhaRelatorio.frase` |
| Mudar o menu do terminal | `menu_console.py` |
| Mudar a aparência ou as telas | `interface_grafica.py` (cores nas constantes do topo) |
| Mudar os argumentos de linha de comando | `main.py` → `criar_parser` |
| Mudar os dados da demonstração | `demonstracao.py` → `ETAPAS` |

**Regra de ouro:** as interfaces **não contêm regras de negócio**. Se você está escrevendo
um `if` sobre um dado dentro de `menu_console.py` ou `interface_grafica.py`, ele
provavelmente pertence a um gerenciador ou a uma função `validar_*`.

---

## 3. Receitas

### Receita 1 — Adicionar um campo a uma entidade

Exemplo: adicionar `telefone` ao Aluno.

**1. Regra de validação** (`alfa/validacoes.py`):

```python
import re

def validar_telefone_aluno(valor, rotulo="Telefone"):
    """Valida telefone com DDD: 10 ou 11 dígitos, com ou sem máscara.

    Returns:
        str: apenas os dígitos.

    Raises:
        ValueError: se não tiver 10 ou 11 dígitos.
    """
    digitos = re.sub(r"\D", "", valor)
    if len(digitos) not in (10, 11):
        raise ValueError(f"{rotulo}: informe DDD + número (10 ou 11 dígitos).")
    return digitos
```

**2. Entidade** (`alfa/aluno.py`): o campo novo entra **no fim** de `CAMPOS`, para que a
migração seja só acrescentar uma coluna.

```python
CAMPOS = ("matricula", "nome", "cpf", "email", "codigo_curso", "telefone")
telefone = propriedade("telefone", "O telefone", validar_telefone_aluno)

def __init__(self, matricula, nome, cpf, email, codigo_curso, telefone):
    ...
    self.telefone = telefone
```

Atualize também o `__str__` e a docstring da classe (seção `Attributes`).

**3. Metadados das interfaces** (`sistema.py` → `ENTIDADES["aluno"]["campos"]`):

```python
("telefone", "Telefone"),
```

Pronto: o console e a GUI passam a pedir e exibir o campo. Na GUI, você pode acrescentar
uma dica em `AplicacaoAcademica.DICAS`.

**4. Migre `alunos.txt`** ([receita 6](#receita-6--migrar-os-arquivos-txt)). Sem a
migração, **todas as linhas antigas serão ignoradas** na carga, porque o número de campos
deixa de bater.

**5. Atualize** a demonstração (`demonstracao.py`), os testes que criam `Aluno(...)`, o
[modelo de dados](../projeto/modelo-de-dados.md) e o [CHANGELOG](../../CHANGELOG.md).

> 💡 Se o campo for **único** (como o CPF), acrescente-o a
> `GerenciadorAlunos.CAMPOS_UNICOS`.

### Receita 2 — Adicionar uma nova entidade

Exemplo: `Turma` (código, nome, semestre, código do curso), de responsabilidade da ALFA.

| # | Arquivo | O que fazer |
|---|---------|-------------|
| 1 | `alfa/validacoes.py` | Funções `validar_*` dos campos novos |
| 2 | `alfa/turma.py` | Classe `Turma(Entidade)` com `CAMPOS`, `propriedade(...)`, `__init__` e `__str__` documentados. **Sem outros métodos**: a fitness function `test_entidades_so_definem_init_e_str` cobra isso. Acrescente o arquivo à tupla `ARQUIVOS_DE_ENTIDADE` em `testes/test_arquitetura.py` |
| 3 | `alfa/__init__.py` | `from .turma import Turma` |
| 4 | `alfa/gerenciadores.py` | `class GerenciadorTurmas(Gerenciador)` com `ROTULO`, `CLASSE` e, se houver vínculo, `validar_vinculos` (ver `GerenciadorAlunos`) |
| 5 | `sistema.py` | Criar `self.turmas = GerenciadorTurmas(pasta / "turmas.txt", self.cursos)` **depois** do que ele referencia; registrar o dependente: `self.cursos.dependentes.append((self.turmas, "codigo_curso", "turma(s)"))`; incluir em `gerenciadores()` e em `ENTIDADES` |
| 6 | `interface_grafica.py` | ⚠️ Três pontos ainda fixos (débito D4): o botão em `_montar_estrutura` (lista de navegação), o cartão em `mostrar_inicio` (ajuste `i < 3` para o novo total) e, se a entidade **for referenciada** por outra, o combobox em `_formulario` |
| 7 | `menu_console.py` | Automático via `ENTIDADES`. Se a entidade for **referenciada** por outra, inclua o campo em `_dica_vinculo` |
| 8 | `dados/turmas.txt` | Opcional: o arquivo é criado na primeira gravação |
| 9 | `testes/` | Testes de cadastro, vínculo e exclusão bloqueada |
| 10 | `docs/` | Modelo de dados (ER + dicionário), modelo de classes, especificação e CHANGELOG |

Note que o menu do console fica com uma opção a mais, e os números de "Relatório" e
"Demonstração" mudam. Ajuste os testes do console que usam `"5"` e `"6"`.

### Receita 3 — Mudar ou criar uma regra de validação

- **Regra que vale para todos** (ex.: o nome passa a aceitar até 150 caracteres): altere
  a constante `LIMITE_NOME` em `nucleo/entidade.py`.
- **Regra que vale para uma equipe** (ex.: o código do professor precisa começar com
  `P`): altere apenas a função da equipe.

```python
# beta/validacoes.py
def validar_codigo_professor(valor, rotulo="Código do professor"):
    """..."""
    codigo = validar_codigo(valor, rotulo)
    if not codigo.upper().startswith("P"):
        raise ValueError(f"{rotulo}: deve começar com P (ex.: P01).")
    return codigo
```

⚠️ **Endurecer uma regra pode invalidar dados existentes.** Linhas antigas que violam a
regra nova serão **ignoradas** na carga e aparecerão como aviso. Antes de publicar,
rode o sistema com uma cópia dos dados reais e confira os avisos.

⚠️ O formato do código de curso é validado **pelas duas equipes** (ADR-004). Mude
`alfa/validacoes.py` e `beta/validacoes.py` juntos.

### Receita 4 — Adicionar um vínculo entre entidades

Exemplo: o Professor passa a ter um `codigo_curso` de coordenação.

1. Campo novo na entidade ([receita 1](#receita-1--adicionar-um-campo-a-uma-entidade)).
2. Validação de existência no gerenciador, em `GerenciadorProfessores.validar_vinculos`.
   Como a BETA não pode importar a ALFA, receba um validador injetado, como em
   `GerenciadorDisciplinas.__init__`.
3. Registrar o dependente em `sistema.py`, para bloquear a exclusão e cascatear a troca
   de código: `self.cursos.dependentes.append((self.professores, "codigo_curso", "professor(es)"))`.
4. Testes: vínculo inexistente recusado, exclusão bloqueada e cascata.

### Receita 5 — Adicionar uma opção ao menu ou um novo relatório

**Novo relatório** (ex.: carga horária total por curso): crie um método em
`GerenciadorRelatorios`, nunca na interface.

```python
def carga_por_curso(self):
    """Soma a carga horária das disciplinas de cada curso.

    Returns:
        dict[str, int]: nome do curso -> total de horas.
    """
    nomes = {c.codigo_curso: c.nome for c in self._cursos.listar()}
    totais = defaultdict(int)
    for d in self._disciplinas.listar():
        totais[nomes.get(d.codigo_curso, d.codigo_curso)] += d.carga_horaria
    return dict(totais)
```

**Nova opção no console:** acrescente uma entrada em `MenuConsole._opcoes_principais`. O
laço do menu não muda.

**Nova tela na GUI:** um método `mostrar_<algo>` que começa com `self._limpar(titulo)` e
um botão na lista de navegação de `_montar_estrutura`.

### Receita 6 — Migrar os arquivos .txt

Necessária ao **adicionar, remover ou reordenar** colunas. Faça backup de `dados/`
antes. Script de exemplo (acrescentar uma coluna `telefone` vazia não serve, porque
campo vazio é inválido; use um valor padrão válido):

```python
# migrar_alunos_telefone.py  (rodar UMA vez, na pasta gestao_academica)
from pathlib import Path

arquivo = Path("dados/alunos.txt")
linhas = arquivo.read_text(encoding="utf-8-sig").splitlines()
novas = [linha + ";1100000000" for linha in linhas if linha.strip()]
arquivo.with_suffix(".txt.antes-da-migracao").write_text("\n".join(linhas) + "\n", encoding="utf-8")
arquivo.write_text("\n".join(novas) + "\n", encoding="utf-8")
print(f"{len(novas)} linhas migradas")
```

Depois abra o sistema e confirme que **não há avisos de linhas ignoradas**.

---

## 4. Solução de problemas

| Sintoma | Causa provável | Solução |
|---------|----------------|---------|
| Aviso "linha ignorada" ao abrir | Linha com campos a menos ou a mais, valor inválido ou código repetido | Corrija a linha no `.txt` (ver [modelo de dados §3.1](../projeto/modelo-de-dados.md#31-linhas-inválidas)) |
| Todas as linhas de um arquivo ignoradas depois de uma mudança no código | `CAMPOS` mudou e o arquivo não foi migrado | [Receita 6](#receita-6--migrar-os-arquivos-txt) |
| Apareceu `alunos.txt.bak` | Houve linhas ignoradas e o arquivo foi regravado | Recupere as linhas do `.bak` se necessário e depois apague-o |
| Sobrou `*.txt.tmp` | Queda durante a gravação | Pode apagar; o `.txt` está íntegro |
| "[aviso] Tkinter indisponível" | Python sem Tk | `sudo apt install python3-tk`, ou use `--console` |
| A GUI não abre via SSH ou WSL | Sem servidor gráfico | Use `--console` |
| Relatório com "(curso X não encontrado)" | O `.txt` foi editado à mão com um vínculo quebrado | Cadastre o curso X ou corrija o `codigo_curso` do aluno |
| Acentos estranhos (ex.: `JoÃ£o`) | Arquivo salvo em ANSI/Latin-1 | Salve o `.txt` como UTF-8 |
| "Não é possível excluir: N aluno(s)..." | Integridade referencial (RN04) | Exclua ou mova os dependentes antes |
| Alterações "somem" | Duas instâncias abertas ao mesmo tempo (risco R1) | Use uma instância por vez |
| `test_camadas_respeitam_as_dependencias_permitidas` falhou | Uma importação nova viola a arquitetura | Veja a mensagem do teste; mova o código ou escreva um ADR |
| `test_cobertura_de_docstrings_e_total` falhou | Função ou classe nova sem docstring | Documente (ver [CONTRIBUTING](../../CONTRIBUTING.md)) |
| `test_referencia_da_api_esta_atualizada` falhou | Docstrings mudaram | `python ferramentas/gerar_referencia_api.py` |

---

## 5. Checklist antes de entregar uma mudança

- [ ] `python -m unittest discover -s testes -v` passa por completo.
- [ ] Testei manualmente a GUI, se mexi em `interface_grafica.py` (ela não tem testes automáticos).
- [ ] Novas funções e classes têm docstring (o teste cobra).
- [ ] Rodei `python ferramentas/gerar_referencia_api.py`, se mudei alguma docstring.
- [ ] Se mudei `CAMPOS`, migrei os `.txt` e atualizei `ENTIDADES`.
- [ ] Se mudei uma regra de arquitetura, escrevi um ADR e atualizei o arc42 §5.1.
- [ ] Atualizei o `CHANGELOG.md`, na seção `[Não lançado]`.
- [ ] Atualizei os documentos afetados: modelo de dados, especificação e matriz de rastreabilidade.
