"""Integração Final (Seção 5 do enunciado) - demonstração guiada.

Executa, na ordem exigida, o fluxo completo de cadastro e depois mostra o relatório e o
conteúdo dos .txt (entregável "Demonstração": dados persistidos no arquivo de texto).

    python main.py --demo

Os registros usam códigos com prefixo DEMO para ficarem fáceis de identificar e excluir.
Rodar de novo não duplica nada: o que já existe é reaproveitado.
Toda gravação passa pelos gerenciadores, exatamente como no menu (nenhum atalho).
"""
from alfa import Aluno, Curso
from beta import Disciplina, Professor

ERROS_ESPERADOS = (ValueError, LookupError, TypeError, OSError)

# (chave da entidade, função que cria o objeto). Funções em vez de objetos prontos:
# assim nada é instanciado ao importar o módulo, só quando a demonstração roda.
ETAPAS = [
    ("1/4  Cadastrar um Professor e um Curso", [
        ("professor", lambda: Professor("DEMO-P", "Beatriz Ramos", "321.654.987-01",
                                        "Estruturas de Dados")),
        ("curso", lambda: Curso("DEMO-C", "Ciência da Computação", "Presencial")),
    ]),
    ("2/4  Cadastrar uma Disciplina vinculada ao Professor e ao Curso", [
        ("disciplina", lambda: Disciplina("DEMO-D", "Algoritmos e Estruturas de Dados", 80,
                                          "DEMO-P", "DEMO-C")),
    ]),
    ("3/4  Cadastrar um Aluno vinculado ao Curso", [
        ("aluno", lambda: Aluno("DEMO-A", "Lucas Ferreira", "741.852.963-00",
                                "lucas.ferreira@email.com", "DEMO-C")),
    ]),
]


def executar_demonstracao(sistema, saida=print, mostrar_arquivos=True):
    """Roda as quatro etapas. Devolve True se tudo deu certo, False se alguma falhou."""
    saida("\n=== DEMONSTRAÇÃO DA INTEGRAÇÃO FINAL ===")
    for titulo, cadastros in ETAPAS:
        saida(f"\n[{titulo}]")
        for chave, criar in cadastros:
            gerente = sistema.gerenciador(chave)
            try:
                registro = criar()
                existente = gerente.buscar(getattr(registro, gerente.chave))
                if existente is not None:
                    saida(f"  = já existia, reaproveitado: {existente}")
                    continue
                gerente.cadastrar(registro)
            except ERROS_ESPERADOS as erro:
                saida(f"  x falhou: {erro}")
                saida("Demonstração interrompida. Corrija o problema e rode novamente.")
                return False
            saida(f"  + cadastrado em {gerente.arquivo.name}: {registro}")

    saida("\n[4/4  Relatório Completo]")
    for numero, frase in enumerate(sistema.relatorio(), start=1):
        saida(f"  {numero:>2}. {frase}")

    if mostrar_arquivos:
        saida("\n[Dados persistidos nos arquivos .txt]")
        for gerente in sistema.gerenciadores():
            saida(f"\n  --- {gerente.arquivo.name} ---")
            for linha in gerente.arquivo.read_text(encoding="utf-8").splitlines():
                saida(f"  {linha}")
    saida("\nDemonstração concluída.")
    return True
