# ADR-007 — Fachada única, duas interfaces e fallback para o console

- **Status:** Aceita
- **Data:** 2026-10-26

## Contexto

O RF17 aceita menu "via console ou interface gráfica", e o desafio pede GUI. O RF16
exige um `main.py` único. Em ambientes sem Tkinter ou sem tela (laboratório Linux, SSH),
a versão 1.0.0 quebrava na primeira linha com `ModuleNotFoundError`.

## Decisão

- `SistemaIntegrado` é a **fachada**: monta tudo e é o único objeto que as interfaces
  conhecem.
- `menu_console.MenuConsole` e `interface_grafica.AplicacaoAcademica` são **finas**:
  coletam a entrada, chamam o gerenciador e mostram o resultado ou o erro.
- Ambas são **genéricas** sobre `sistema.ENTIDADES`. Não há código por entidade.
- O `main.py` cria o sistema **uma vez** e injeta na interface. Ele importa
  `interface_grafica` tardiamente e cai para o console em `ImportError` ou quando não há
  tela (`RuntimeError`).
- O `MenuConsole` recebe `entrada` e `saida` injetáveis, o que permite testá-lo sem
  teclado.

## Consequências

- ✅ Console e GUI se comportam igual, porque as regras estão nos gerenciadores.
- ✅ O sistema roda em qualquer máquina com Python.
- ✅ O console é 100% testável automaticamente.
- ⚠️ A GUI não tem testes automatizados (exigiria um display). Teste manualmente após mudanças.
- ⚠️ `ENTIDADES` precisa acompanhar `CAMPOS` (débito D3).
