# ADR-001 — Persistência em arquivos .txt separados por `;`

- **Status:** Aceita
- **Data:** 2026-10-19
- **Decisores:** Equipes ALFA e BETA

## Contexto

O enunciado exige que os dados fiquem em `alunos.txt`, `cursos.txt`, `professores.txt` e
`disciplinas.txt`, com os campos separados por ponto e vírgula (RF10). O sistema precisa
carregar tudo ao iniciar (RF11) e atualizar o arquivo a cada escrita (RF12).

## Decisão

- Cada entidade tem **um arquivo**, com **um registro por linha** e os campos na ordem
  de `Classe.CAMPOS`.
- O separador é a constante `SEPARADOR = ";"` em `nucleo/entidade.py`, a única fonte da
  verdade.
- Codificação UTF-8 e quebra de linha `\n` em qualquer sistema operacional
  (`newline="\n"`).
- O `;` e os caracteres de controle são **proibidos nos dados**, em vez de usar aspas e
  *escape* como no CSV.
- A primeira coluna é sempre o identificador único.

## Alternativas consideradas

| Alternativa | Por que não |
|-------------|-------------|
| Módulo `csv` com aspas | Permitiria `;` nos dados, mas o arquivo fica menos legível e o formato pedido é simples |
| JSON | Descumpre o enunciado |
| SQLite | Descumpre o enunciado; seria a evolução natural (ver o débito D1) |

## Consequências

- ✅ O arquivo é legível e editável à mão, o que facilita a demonstração.
- ✅ A leitura se resume a um `split`.
- ⚠️ Nenhum campo pode conter `;`. A regra é aplicada na validação e documentada para o usuário.
- ⚠️ Mudar a ordem de `CAMPOS` quebra os arquivos existentes. É preciso migrar (ver o
  guia de manutenção, receita 6).
