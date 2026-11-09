"""Fitness functions: testes que protegem as regras de arquitetura documentadas.

Se um destes testes falhar, o código passou a contradizer docs/arquitetura/arc42.md.
Corrija o código ou, se a mudança for intencional, registre um novo ADR em docs/adr/
e atualize a regra aqui.

    python -m unittest discover -s testes -v
"""
import ast
import importlib.util
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent

# Camada/pacote -> prefixos internos que ela PODE importar (ver arc42, seção 5.1)
REGRAS_DE_DEPENDENCIA = {
    "nucleo": {"nucleo"},
    "alfa": {"nucleo", "alfa"},
    "beta": {"nucleo", "beta"},
    "avaliacao": {"nucleo", "avaliacao"},
    "relatorios": set(),
    "sistema": {"alfa", "beta", "avaliacao", "relatorios"},
    "demonstracao": {"alfa", "beta"},
    "menu_console": {"sistema", "demonstracao", "avaliacao"},
    "interface_grafica": {"sistema", "demonstracao", "avaliacao"},
    "main": {"sistema", "menu_console", "interface_grafica", "demonstracao"},
    "ferramentas": set(),   # só lê o código-fonte com ast
}
MODULOS_INTERNOS = set(REGRAS_DE_DEPENDENCIA)
ARQUIVOS_DE_ENTIDADE = ("alfa/aluno.py", "alfa/curso.py", "beta/professor.py", "beta/disciplina.py",
                        "avaliacao/nota.py")


def arquivos_de_producao():
    """Todos os .py do sistema, exceto os testes."""
    return [p for p in RAIZ.rglob("*.py") if "testes" not in p.relative_to(RAIZ).parts]


def camada_de(caminho):
    """'alfa/aluno.py' -> 'alfa'; 'main.py' -> 'main'."""
    partes = caminho.relative_to(RAIZ).with_suffix("").parts
    return partes[0]


def importacoes_internas(caminho):
    """Conjunto de módulos internos importados (absolutos ou relativos) por um arquivo."""
    arvore = ast.parse(caminho.read_text(encoding="utf-8"))
    encontrados = set()
    for no in ast.walk(arvore):
        if isinstance(no, ast.Import):
            nomes = [alias.name for alias in no.names]
        elif isinstance(no, ast.ImportFrom):
            # import relativo (from .x import y) fica dentro do próprio pacote
            nomes = [camada_de(caminho)] if no.level else [no.module or ""]
        else:
            continue
        encontrados |= {n.split(".")[0] for n in nomes if n.split(".")[0] in MODULOS_INTERNOS}
    return encontrados


class TestRegrasDeDependencia(unittest.TestCase):
    """Cada camada só importa o que o diagrama de componentes permite."""

    def test_camadas_respeitam_as_dependencias_permitidas(self):
        violacoes = []
        for caminho in arquivos_de_producao():
            camada = camada_de(caminho)
            proibidas = importacoes_internas(caminho) - REGRAS_DE_DEPENDENCIA[camada] - {camada}
            if proibidas:
                violacoes.append(f"{caminho.relative_to(RAIZ)} importa {sorted(proibidas)}")
        self.assertEqual([], violacoes)

    def test_beta_e_independente_da_alfa(self):
        # ADR-004: a BETA deve funcionar e ser testada sem a ALFA
        for caminho in (RAIZ / "beta").glob("*.py"):
            self.assertNotIn("alfa", importacoes_internas(caminho), caminho.name)


class TestEntidadesSaoModelosDeDados(unittest.TestCase):
    """Dica do enunciado: entidades apenas como modelos de dados (ADR-003 e ADR-008)."""

    def test_entidades_so_definem_init_e_str(self):
        for relativo in ARQUIVOS_DE_ENTIDADE:
            arvore = ast.parse((RAIZ / relativo).read_text(encoding="utf-8"))
            for classe in (n for n in arvore.body if isinstance(n, ast.ClassDef)):
                metodos = {n.name for n in classe.body if isinstance(n, ast.FunctionDef)}
                self.assertEqual({"__init__", "__str__"}, metodos, relativo)

    def test_entidades_nao_acessam_arquivos(self):
        for relativo in ARQUIVOS_DE_ENTIDADE:
            codigo = (RAIZ / relativo).read_text(encoding="utf-8")
            for proibido in ("open(", "gerenciador", "pathlib"):
                self.assertNotIn(proibido, codigo, f"{relativo} usa {proibido}")


class TestDocumentacaoDoCodigo(unittest.TestCase):
    """Todo módulo, classe e função de produção precisa de docstring."""

    def test_cobertura_de_docstrings_e_total(self):
        sem_doc = []
        for caminho in arquivos_de_producao():
            arvore = ast.parse(caminho.read_text(encoding="utf-8"))
            nome = caminho.relative_to(RAIZ)
            if ast.get_docstring(arvore) is None:
                sem_doc.append(f"{nome} (módulo)")
            for no in ast.walk(arvore):
                if isinstance(no, (ast.FunctionDef, ast.ClassDef)) and ast.get_docstring(no) is None:
                    sem_doc.append(f"{nome}:{no.lineno} {no.name}")
        self.assertEqual([], sem_doc)

    def test_documentos_de_arquitetura_existem(self):
        for relativo in ("README.md", "CHANGELOG.md", "CONTRIBUTING.md", "docs/README.md",
                         "docs/arquitetura/arc42.md", "docs/requisitos/especificacao.md",
                         "docs/projeto/modelo-de-dados.md", "docs/projeto/modelo-de-classes.md",
                         "docs/manutencao/guia-de-manutencao.md"):
            self.assertTrue((RAIZ / relativo).is_file(), relativo)

    def test_referencia_da_api_esta_atualizada(self):
        # A referência é gerada das docstrings; se divergir, alguém esqueceu de regenerar
        spec = importlib.util.spec_from_file_location(
            "gerar_referencia_api", RAIZ / "ferramentas" / "gerar_referencia_api.py")
        gerador = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(gerador)
        atual = gerador.DESTINO.read_text(encoding="utf-8") if gerador.DESTINO.exists() else ""
        self.assertEqual(gerador.gerar(), atual,
                         "Rode: python ferramentas/gerar_referencia_api.py")


def load_tests(loader, testes, padrao):
    """Inclui na suíte os exemplos executáveis (doctests) escritos nas docstrings."""
    import doctest
    import nucleo.entidade
    testes.addTests(doctest.DocTestSuite(nucleo.entidade))
    return testes


if __name__ == "__main__":
    unittest.main()
