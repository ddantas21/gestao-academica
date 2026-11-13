# ADR-004 — BETA independente da ALFA via injeção de validador

- **Status:** Aceita (corrige uma violação encontrada na versão 1.1.0)
- **Data:** 2026-10-26

## Contexto

A Disciplina (BETA) referencia um Curso (ALFA). A BETA precisa: (a) validar o
**formato** do `codigo_curso` e (b) saber se o curso **existe** (RF14). Na versão 1.1.0,
`beta/disciplina.py` fazia `from alfa.validacoes import validar_codigo_curso`. Com isso,
a BETA não podia ser executada nem testada sem o pacote da ALFA, o que contradizia a
própria docstring de `beta/integracao.py`.

## Decisão

1. **Formato:** a BETA tem o seu próprio `validar_codigo_curso` em `beta/validacoes.py`,
   apoiado em `nucleo.validar_codigo`.
2. **Existência:** `SistemaBeta` e `GerenciadorDisciplinas` recebem um
   `validador_curso: Callable[[str], bool]`, que é injeção de dependência por função. A
   ligação com a ALFA acontece **somente** no `SistemaIntegrado`:

```python
self.beta = SistemaBeta(pasta, validador_curso=lambda codigo: self.cursos.buscar(codigo) is not None)
```

3. Sem validador (BETA isolada), o código do curso é apenas armazenado.
4. A regra "BETA não importa ALFA" é verificada por `test_beta_e_independente_da_alfa`.

## Consequências

- ✅ As equipes desenvolvem e testam em paralelo.
- ✅ É possível trocar a fonte de cursos, por exemplo um *mock* nos testes.
- ⚠️ As duas equipes precisam manter a **mesma regra de formato** do código de curso.
  Hoje ambas usam `nucleo.validar_codigo`. Se uma delas mudar, combine com a outra.
