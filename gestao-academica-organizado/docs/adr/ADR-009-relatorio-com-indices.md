# ADR-009 — Relatório em gerenciador próprio com índices em dicionário

- **Status:** Aceita
- **Data:** 2026-10-26

## Contexto

O RF15 pede a frase "O Aluno [Nome] está matriculado no curso [Nome do Curso], assistindo
a disciplina [Nome da Disciplina] com o professor [Nome do Professor]". A versão 1.0.0
gerava o relatório dentro do `SistemaIntegrado`, contrariando a dica de colocar os RFs nas
gerenciadoras, e chamava `buscar()` (O(n)) dentro dos laços.

## Decisão

- Criar `relatorios.GerenciadorRelatorios`, que recebe os quatro gerenciadores por injeção.
- `gerar()` monta índices `{codigo: objeto}` e agrupa as disciplinas por curso
  (`defaultdict`) **uma vez**, o equivalente a um *hash join*.
- Cada linha é um `LinhaRelatorio` (dataclass imutável) e a propriedade `frase` produz
  o texto exato do RF15.
- Um aluno de curso sem disciplinas gera uma linha "sem disciplinas cadastradas", em vez
  de desaparecer do relatório.

## Consequências

- ✅ Custo O(A + D + C + P) em vez de O(A × D).
- ✅ Os dados estruturados (`gerar()`) ficam separados da apresentação (`frases()`),
  então é fácil exportar para outro formato no futuro.
- ✅ A classe pode ser testada com qualquer conjunto de gerenciadores.
