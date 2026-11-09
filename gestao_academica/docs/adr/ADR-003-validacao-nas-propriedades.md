# ADR-003 — Validação nos setters via fábrica de propriedades

- **Status:** Aceita
- **Data:** 2026-10-19

## Contexto

O enunciado exige atributos protegidos e `@property` (4.A). Os dados entram por quatro
caminhos: GUI, console, demonstração e leitura do `.txt`. Escrever quatro `@property`
manuais por entidade (17 propriedades no total) repetiria a mesma validação básica.

## Decisão

A função `nucleo.entidade.propriedade(nome, rotulo, validar)` gera uma `property` que:

1. guarda o valor em `self._<nome>` (atributo protegido);
2. no setter, faz `strip()`, recusa vazio, caracteres de controle e `;`;
3. aplica a função `validar` específica, que pode **normalizar** o valor (CPF com
   máscara, modalidade canônica, carga horária como `int`).

```python
class Curso(Entidade):
    nome = propriedade("nome", "O nome do curso", validar_nome_curso)
```

Como o `__init__` atribui por meio dos setters, **nenhum objeto inválido chega a existir**.

## Consequências

- ✅ Todo caminho de entrada é validado, inclusive arquivos editados à mão.
- ✅ As regras por equipe ficam em `alfa/validacoes.py` e `beta/validacoes.py`, e cada
  equipe pode endurecer as suas.
- ⚠️ A validação de **contexto** (o curso existe? o CPF é único?) não cabe na entidade e
  fica no gerenciador (ver ADR-002).
- ⚠️ Quem não conhece *descriptors* pode estranhar o `propriedade()`. Esta ADR e a
  docstring explicam o mecanismo.
