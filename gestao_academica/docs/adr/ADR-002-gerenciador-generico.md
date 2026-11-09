# ADR-002 — Gerenciador genérico com Template Method

- **Status:** Aceita
- **Data:** 2026-10-19

## Contexto

As quatro entidades precisam das mesmas operações: cadastrar, listar, pesquisar, alterar,
excluir, carregar e salvar (RF01–RF05, RF10–RF12). A dica do enunciado pede que essa
lógica fique em "classes gerenciadoras (ex.: GerenciadorAlunos)". Implementar o CRUD
quatro vezes multiplicaria os bugs e as diferenças de comportamento.

## Decisão

Criar `nucleo.gerenciador.Gerenciador` com todo o fluxo de CRUD e persistência. Cada
gerenciador concreto só **configura** atributos de classe e, quando necessário,
sobrescreve **um gancho**:

```python
class GerenciadorAlunos(Gerenciador):
    ROTULO = "aluno"          # nome nas mensagens
    CLASSE = Aluno            # entidade gerenciada
    CAMPOS_UNICOS = ("cpf",)  # além da chave

    def validar_vinculos(self, aluno):   # gancho do Template Method
        ...
```

A chave de cada entidade é sempre `CLASSE.CAMPOS[0]`.

## Alternativas consideradas

| Alternativa | Por que não |
|-------------|-------------|
| Um CRUD escrito à mão por entidade | Quatro vezes mais código e comportamento divergente |
| Composição (um `Repositorio` injetado) | Mais flexível, mas mais complexo do que o necessário para o escopo |

## Consequências

- ✅ Um bug corrigido no `Gerenciador` fica corrigido para as quatro entidades.
- ✅ A classe `GerenciadorAlunos` exigida pelo enunciado existe e é explícita.
- ✅ Adicionar uma nova entidade custa cerca de 15 linhas de gerenciador.
- ⚠️ Uma mudança no `Gerenciador` afeta todas as entidades. Rode a suíte inteira de testes.
