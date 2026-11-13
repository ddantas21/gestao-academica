"""Gera docs/api/referencia.md a partir das docstrings do código (fonte única da verdade).

Uso, na pasta do projeto:
    python ferramentas/gerar_referencia_api.py           # regrava o arquivo
    python ferramentas/gerar_referencia_api.py --check   # só verifica (código 1 se desatualizado)

O código é lido com o módulo ``ast``: nada é importado nem executado, então funciona
até sem Tkinter instalado. O teste ``test_referencia_da_api_esta_atualizada`` usa a
mesma função para garantir que a referência acompanha o código.
"""
import ast
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DESTINO = RAIZ / "docs" / "api" / "referencia.md"

# Ordem de leitura sugerida: da base para a apresentação (igual ao arc42, seção 5)
MODULOS = [
    "nucleo/entidade.py", "nucleo/gerenciador.py",
    "alfa/validacoes.py", "alfa/curso.py", "alfa/aluno.py", "alfa/gerenciadores.py",
    "beta/validacoes.py", "beta/professor.py", "beta/disciplina.py", "beta/integracao.py",
    "relatorios.py", "sistema.py", "demonstracao.py",
    "menu_console.py", "interface_grafica.py", "main.py",
]


def assinatura(funcao):
    """Reconstrói a assinatura de uma função a partir da AST (ex.: ``(self, codigo)``)."""
    return f"({ast.unparse(funcao.args)})"


def documentar_funcao(funcao, nivel):
    """Bloco Markdown de uma função ou método."""
    prefixo = "@staticmethod " if any(
        isinstance(d, ast.Name) and d.id == "staticmethod" for d in funcao.decorator_list) else ""
    if any(isinstance(d, ast.Name) and d.id == "property" for d in funcao.decorator_list):
        prefixo = "@property "
    doc = ast.get_docstring(funcao) or "_Sem docstring._"
    return f"{'#' * nivel} `{prefixo}{funcao.name}{assinatura(funcao)}`\n\n```text\n{doc}\n```\n"


def documentar_modulo(relativo):
    """Bloco Markdown de um módulo: docstring, classes (com métodos) e funções."""
    arvore = ast.parse((RAIZ / relativo).read_text(encoding="utf-8"))
    partes = [f"## `{relativo}`\n", f"{ast.get_docstring(arvore) or '_Sem docstring._'}\n"]
    for no in arvore.body:
        if isinstance(no, ast.ClassDef):
            bases = ", ".join(ast.unparse(b) for b in no.bases)
            partes.append(f"### class `{no.name}`" + (f"({bases})" if bases else "") + "\n")
            partes.append(f"```text\n{ast.get_docstring(no) or '_Sem docstring._'}\n```\n")
            for metodo in (n for n in no.body if isinstance(n, ast.FunctionDef)):
                partes.append(documentar_funcao(metodo, 4))
        elif isinstance(no, ast.FunctionDef):
            partes.append(documentar_funcao(no, 3))
    return "\n".join(partes)


def gerar():
    """Monta o conteúdo completo de docs/api/referencia.md.

    Returns:
        str: Markdown da referência.
    """
    cabecalho = (
        "# Referência da API\n\n"
        "> ⚙️ **Arquivo gerado automaticamente** por `ferramentas/gerar_referencia_api.py` "
        "a partir das docstrings.\n> Não edite à mão: altere a docstring no código e "
        "rode o script novamente.\n\n## Módulos\n\n"
        + "\n".join(f"- [`{m}`](#{m.replace('/', '').replace('.', '')})"
                    for m in MODULOS)
        + "\n\n---\n\n"
    )
    return cabecalho + "\n---\n\n".join(documentar_modulo(m) for m in MODULOS)


def main(argv=None):
    """Grava a referência ou, com ``--check``, apenas verifica se está atualizada.

    Returns:
        int: 0 se ok/gravado; 1 se ``--check`` encontrou diferença.
    """
    argv = sys.argv[1:] if argv is None else argv
    conteudo = gerar()
    if "--check" in argv:
        atual = DESTINO.read_text(encoding="utf-8") if DESTINO.exists() else ""
        if atual != conteudo:
            print("docs/api/referencia.md está desatualizado. Rode: python ferramentas/gerar_referencia_api.py")
            return 1
        print("Referência da API atualizada.")
        return 0
    DESTINO.parent.mkdir(parents=True, exist_ok=True)
    DESTINO.write_text(conteudo, encoding="utf-8", newline="\n")
    print(f"Gerado: {DESTINO.relative_to(RAIZ)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
