# ADR-006 — Integridade referencial: bloquear exclusão e cascatear a troca de código

- **Status:** Aceita
- **Data:** 2026-10-26

## Contexto

Os vínculos (RF13, RF14) são códigos gravados em outros arquivos, e não há banco de dados
para garantir chaves estrangeiras. O RF04 pede que **qualquer** atributo possa ser
alterado, incluindo o código. Sem controle, apareceriam alunos apontando para cursos
inexistentes, e o relatório (RF15) mostraria "(curso não encontrado)".

## Decisão

Cada gerenciador mantém `dependentes: list[(gerenciador, campo, rótulo)]`, preenchida na
montagem:

| Entidade referenciada | Dependentes | Onde é registrado |
|-----------------------|-------------|-------------------|
| Curso | Aluno.codigo_curso, Disciplina.codigo_curso | `SistemaIntegrado.__init__` |
| Professor | Disciplina.codigo_professor | `SistemaBeta.__init__` |
| Aluno | Nota.matricula | `SistemaIntegrado.__init__` |
| Disciplina | Nota.codigo_disciplina | `SistemaIntegrado.__init__` |

- **Cadastro e alteração:** `validar_vinculos` exige que o registro referenciado exista
  (equivale a `FOREIGN KEY`).
- **Exclusão:** bloqueada se houver dependentes (equivale a `ON DELETE RESTRICT`).
- **Troca de código:** propagada aos dependentes (equivale a `ON UPDATE CASCADE`).
  Todas as trocas são **planejadas antes de aplicar**; se a gravação falhar, as listas
  copiadas são restauradas e regravadas (`_desfazer`).

## Alternativas consideradas

| Alternativa | Por que não |
|-------------|-------------|
| Proibir a troca de código | Descumpre a leitura literal do RF04 ("qualquer um de seus atributos") |
| Exclusão em cascata | Apagar alunos ao excluir um curso é destrutivo demais |

## Consequências

- ✅ O relatório nunca mostra vínculos quebrados criados pelo sistema.
- ⚠️ A cascata percorre um nível de dependência. Hoje Aluno e Disciplina não têm
  dependentes; se uma nova entidade passar a referenciar a Disciplina, a cascata
  continua funcionando, porque cada gerenciador verifica os seus próprios `dependentes`
  na alteração do seu código.
- ⚠️ Gerenciadores acessam `_registros` de outros gerenciadores na cascata. Isso é
  aceitável porque todos são da mesma família de classes, mas não replique esse padrão
  fora do `Gerenciador`.
