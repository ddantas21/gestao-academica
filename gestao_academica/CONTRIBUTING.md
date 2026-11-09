# Como contribuir

Padrões que mantêm o código consistente. Os itens marcados com 🤖 são verificados
automaticamente pela suíte de testes.

## 1. Fluxo de trabalho

1. Leia a [documentação técnica](docs/README.md) da área que vai alterar.
2. Rode `python -m unittest discover -s testes -v`: tudo deve passar **antes** de começar.
3. Faça a mudança seguindo as [receitas do guia de manutenção](docs/manutencao/guia-de-manutencao.md#3-receitas).
4. Escreva ou ajuste os testes, e atualize a documentação afetada.
5. Rode `python ferramentas/gerar_referencia_api.py` se mudou docstrings.
6. Rode a suíte de novo e registre a mudança no `CHANGELOG.md`.

Use o [checklist do guia](docs/manutencao/guia-de-manutencao.md#5-checklist-antes-de-entregar-uma-mudança)
antes de entregar.

## 2. Arquitetura

- 🤖 Respeite as **regras de dependência** (arc42 §5.1): `nucleo` não importa ninguém;
  `alfa` e `beta` só importam `nucleo`; as interfaces só importam `sistema` e `demonstracao`.
- 🤖 **Entidades** têm apenas `CAMPOS`, as `propriedade(...)`, `__init__` e `__str__`.
- **Regras de negócio** ficam nos gerenciadores ou nas funções `validar_*`, nunca nas
  interfaces.
- **Interfaces** tratam apenas `ValueError`, `LookupError`, `TypeError` e `OSError`
  (arc42 §8.2). Nunca use `except Exception` para esconder erros.
- Mudou uma regra de arquitetura? **Escreva um ADR** (`docs/adr/README.md` tem o modelo).

## 3. Código

| Item | Padrão | Exemplo |
|------|--------|---------|
| Idioma | Português, sem acentos nos identificadores | `validar_carga_horaria` |
| Módulos e funções | `snake_case` | `gerar_referencia_api.py`, `executar_demonstracao()` |
| Classes | `PascalCase` | `GerenciadorDisciplinas` |
| Constantes | `MAIUSCULAS` | `SEPARADOR`, `LIMITE_NOME` |
| Membros internos | prefixo `_` | `_registros`, `_para_linha()` |
| Gerenciadores | `Gerenciador` + plural | `GerenciadorAlunos` |
| Validações | `validar_<campo>_<entidade>` por equipe | `validar_cpf_professor` |
| Mensagens de erro | Para o usuário final, em português, dizendo como corrigir | `"O curso '99' não existe. Cadastre o curso primeiro."` |
| Linha | Até cerca de 110 caracteres | — |
| Dependências | Somente a biblioteca padrão | Bibliotecas externas exigem um ADR |
| Arquivos | Abrir sempre com `encoding="utf-8"` (gravação) | — |

## 4. Docstrings (Google Style)

🤖 **Todo módulo, classe e função** de produção tem docstring.

```python
def obter(self, codigo):
    """Devolve o registro com o código informado.

    Args:
        codigo (str): identificador; espaços nas pontas são ignorados.

    Returns:
        Entidade: o registro encontrado.

    Raises:
        LookupError: se não existir registro com esse código.
    """
```

- **Primeira linha:** o que a função faz, no presente, terminando com ponto.
- `Args`, `Returns`, `Raises`: quando não forem óbvios pelo nome.
- **Referencie o requisito** atendido (`RF04: ...`) quando houver um.
- **Comentários `#`** explicam o **porquê**, e não o quê: `# utf-8-sig aceita BOM do Bloco de Notas`.
- 🤖 Exemplos `>>>` em `nucleo/entidade.py` são executados como doctest.

## 5. Testes

- **Nome:** `test_rf<NN>_<comportamento_esperado>` ou `test_<regra>_<comportamento>`.
- **Sempre** sobre a pasta temporária do `BaseTeste`; nunca sobre `dados/`.
- Verifique o **arquivo** (`self.ler(...)`), e não só a memória.
- Atualize a [matriz de rastreabilidade](docs/requisitos/especificacao.md#8-matriz-de-rastreabilidade).

## 6. Versionamento

- [SemVer](https://semver.org/lang/pt-BR/): `MAIOR.MENOR.CORREÇÃO`.
  - **MAIOR:** muda o formato dos `.txt` sem compatibilidade ou quebra o contrato do `Gerenciador`.
  - **MENOR:** nova funcionalidade compatível.
  - **CORREÇÃO:** correção de bug.
- Registre no `CHANGELOG.md`, seção `[Não lançado]`, nas categorias Adicionado,
  Alterado, Corrigido, Removido e Segurança.
- **Nunca** versione dados pessoais reais em `dados/` (risco R4).
