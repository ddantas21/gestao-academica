# ADR-010 — Regras de arquitetura verificadas por testes (fitness functions)

- **Status:** Aceita
- **Data:** 2026-10-26

## Contexto

Documentação de arquitetura envelhece. Ao revisar o código para escrever esta
documentação, encontramos uma violação (BETA importando ALFA, ver ADR-004) que nenhum
teste tinha pegado. Sem verificação automática, outras violações voltariam a aparecer.

## Decisão

`testes/test_arquitetura.py` verifica, a cada execução da suíte:

| Regra | Teste |
|-------|-------|
| Cada camada só importa o permitido (arc42 §5.1) | `test_camadas_respeitam_as_dependencias_permitidas` |
| BETA não importa ALFA | `test_beta_e_independente_da_alfa` |
| Entidades têm só `__init__` e `__str__` | `test_entidades_so_definem_init_e_str` |
| Entidades não acessam arquivos | `test_entidades_nao_acessam_arquivos` |
| Todo módulo, classe e função tem docstring | `test_cobertura_de_docstrings_e_total` |
| Os documentos principais existem | `test_documentos_de_arquitetura_existem` |

As importações são analisadas com o módulo `ast` (sem executar o código).

## Consequências

- ✅ A arquitetura documentada e a real não divergem em silêncio.
- ✅ Um novo colaborador descobre a regra no momento em que a quebra.
- ⚠️ Para mudar uma regra de propósito: escreva um novo ADR, atualize
  `REGRAS_DE_DEPENDENCIA` no teste e o diagrama da seção 5.1 do arc42.
