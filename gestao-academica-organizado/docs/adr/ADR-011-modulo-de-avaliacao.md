# ADR-011 — Módulo de Avaliação em pacote próprio, com chave composta e média calculada

- **Status:** Aceita
- **Data:** 2026-11-09

## Contexto

Os requisitos RF19–RF24 acrescentam notas e pesos por aluno e disciplina, média ponderada
com teto de 10.0 e relatório de rendimento. Três pontos não cabiam no desenho anterior:

1. O registro é identificado por **dois** campos (matrícula + disciplina), mas o
   `Gerenciador` assumia que a chave era o primeiro campo.
2. A média depende de aritmética exata (um aluno não pode ser reprovado por erro de
   ponto flutuante) e deve refletir edições manuais do `notas.txt` (RF24).
3. A ALFA e a BETA são equipes independentes; as notas ligam entidades das duas.

## Decisão

- Novo pacote `avaliacao/` (entidade `Nota`, validações, cálculo, `GerenciadorNotas`,
  `GerenciadorRendimento`). Depende **só de** `nucleo`; recebe os gerenciadores de alunos e
  disciplinas por injeção, como a BETA recebe o validador de curso (ADR-004).
- O `Gerenciador` ganhou o gancho `identificador(obj)` (mais `_normalizar_id` e `_texto_id`).
  O padrão continua sendo o primeiro campo; `GerenciadorNotas` devolve a tupla
  `(matricula, codigo_disciplina)`. Nenhuma outra entidade foi afetada.
- Notas e pesos são `Decimal`. A média **não é gravada**: `media_ponderada()` calcula na hora
  e limita a 10.00; `GerenciadorNotas` relê o arquivo antes de listar e de cada gravação.
- `SistemaIntegrado` registra `Nota` como dependente de Aluno e Disciplina (ADR-006).

## Alternativas consideradas

| Alternativa | Por que não |
|-------------|-------------|
| Gravar a média no `.txt` | Descumpre o RF20 (formato fixo) e deixaria de refletir edições manuais (RF24) |
| `float` para notas | Médias como 6.999999… mudariam o status; `Decimal` é exato |
| Chave sintética (id da nota) | Mudaria o formato do arquivo exigido no RF20 |
| Colocar as notas em `alfa/` ou `beta/` | A nota liga as duas equipes; um pacote próprio mantém a independência (ADR-004) |

## Consequências

- ✅ O núcleo continua genérico; a chave composta é um ponto de extensão, não um caso especial.
- ✅ Edição manual do `notas.txt` vale na leitura seguinte sem reiniciar o sistema.
- ⚠️ Relê-se o `notas.txt` a cada listagem. Para centenas de linhas é imperceptível; para
  milhares, trocar por verificação de data de modificação.
- ⚠️ Quem edita o arquivo à mão com o sistema aberto pode ter a linha inválida ignorada (e
  avisada) na leitura seguinte, como nos demais arquivos (RNF04).
