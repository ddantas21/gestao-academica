# ADR-005 — Gravação atômica com arquivo temporário

- **Status:** Aceita
- **Data:** 2026-10-19

## Contexto

O RF12 exige regravar o arquivo a cada escrita. Abrir `alunos.txt` com `"w"` apaga o
conteúdo imediatamente. Se o programa cair no meio da escrita, o arquivo fica vazio ou
pela metade.

## Decisão

`Gerenciador.salvar()`:

1. escreve tudo em `arquivo.txt.tmp`;
2. troca com `os.replace(tmp, arquivo)`. A troca é atômica em POSIX e, no Windows,
   substitui o arquivo numa única operação, desde que os dois estejam no mesmo disco;
3. se houver `linhas_ignoradas` na carga, copia o original para `arquivo.txt.bak` antes
   da primeira regravação (uma vez só);
4. cada operação de escrita (`cadastrar`, `alterar`, `excluir`) desfaz a mudança em
   memória se `salvar()` levantar `OSError`.

## Consequências

- ✅ Um arquivo nunca fica pela metade: ou tem o conteúdo antigo, ou o novo.
- ✅ Linhas que o programa não entendeu não se perdem.
- ⚠️ A atomicidade vale **por arquivo**. Na cascata entre vários arquivos (ADR-006),
  uma queda entre duas trocas pode deixar os arquivos inconsistentes (risco R2).
- ⚠️ O `.bak` não é sobrescrito. Se houver um antigo, apague-o depois de conferir.
