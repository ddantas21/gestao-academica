# Registros de Decisão de Arquitetura (ADR)

Cada ADR documenta **uma** decisão significativa: o contexto, o que foi decidido, as
alternativas descartadas e as consequências. O formato segue a proposta de Michael
Nygard (*Documenting Architecture Decisions*, 2011).

## Índice

| ADR | Título | Status |
|-----|--------|--------|
| [001](ADR-001-persistencia-txt.md) | Persistência em arquivos .txt separados por `;` | Aceita |
| [002](ADR-002-gerenciador-generico.md) | Gerenciador genérico com Template Method | Aceita |
| [003](ADR-003-validacao-nas-propriedades.md) | Validação nos setters via fábrica de propriedades | Aceita |
| [004](ADR-004-independencia-da-beta.md) | BETA independente da ALFA via injeção de validador | Aceita |
| [005](ADR-005-gravacao-atomica.md) | Gravação atômica com arquivo temporário | Aceita |
| [006](ADR-006-integridade-referencial.md) | Integridade referencial: bloquear exclusão e cascatear troca de código | Aceita |
| [007](ADR-007-fachada-e-interfaces.md) | Fachada única, duas interfaces e fallback para o console | Aceita |
| [008](ADR-008-serializacao-no-gerenciador.md) | Conversão objeto ↔ linha do .txt no gerenciador | Aceita |
| [009](ADR-009-relatorio-com-indices.md) | Relatório em gerenciador próprio com índices em dicionário | Aceita |
| [010](ADR-010-fitness-functions.md) | Regras de arquitetura verificadas por testes | Aceita |
| [011](ADR-011-modulo-de-avaliacao.md) | Módulo de Avaliação em pacote próprio, chave composta e média calculada | Aceita |

## Quando escrever um ADR

Escreva um quando a decisão:

- mudar uma regra de dependência entre pacotes;
- mudar o formato dos arquivos `.txt`;
- introduzir uma biblioteca externa;
- mudar o contrato público do `Gerenciador` ou do `SistemaIntegrado`;
- desfizer ou substituir um ADR anterior.

ADRs **não são editados** depois de aceitos. Para mudar uma decisão, crie um ADR novo com
status "Aceita" e marque o antigo como "Substituída por ADR-0XX".

## Modelo

```markdown
# ADR-0XX — Título curto no imperativo

- **Status:** Proposta | Aceita | Substituída por ADR-0YY | Descartada
- **Data:** AAAA-MM-DD

## Contexto
Qual problema ou força motivou a decisão? Quais restrições existiam?

## Decisão
O que foi decidido, de forma concreta (com trecho de código, se ajudar).

## Alternativas consideradas
| Alternativa | Por que não |

## Consequências
- ✅ ganhos
- ⚠️ custos, riscos e o que passa a ser obrigatório
```
