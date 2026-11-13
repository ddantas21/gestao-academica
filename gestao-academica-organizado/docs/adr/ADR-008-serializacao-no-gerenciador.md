# ADR-008 — Conversão objeto ↔ linha do .txt no gerenciador

- **Status:** Aceita (substitui `Entidade.para_linha`, removido na versão 1.2.0)
- **Data:** 2026-10-26

## Contexto

A dica do enunciado pede que as entidades fiquem "apenas como modelos de dados". Na
versão 1.1.0, a `Entidade` tinha `para_linha()`, que sabia o formato do arquivo, enquanto
a leitura (`split(";")`) estava no `Gerenciador`. O conhecimento do formato estava
dividido em duas classes.

## Decisão

- `Gerenciador._para_linha(obj)` e `Gerenciador._de_linha(linha)` concentram o formato.
- A `Entidade` só declara `CAMPOS` (ordem das colunas) e não tem nenhum método de E/S.
- O teste `test_entidades_so_definem_init_e_str` garante que as entidades tenham apenas
  `__init__` e `__str__`.

## Consequências

- ✅ Trocar o formato (por exemplo, para CSV com aspas) exige mexer em um único arquivo.
- ✅ As entidades podem ser reaproveitadas com outra persistência.
- ⚠️ `CAMPOS` continua na entidade, porque é o contrato de dados que o gerenciador usa.
