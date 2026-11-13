"""RF16 - Ponto de entrada único do Sistema de Gestão Acadêmica (ALFA + BETA).

Uso:
    python main.py              -> abre a interface gráfica (cai no console se não houver tela)
    python main.py --console    -> força o menu de terminal
    python main.py --relatorio  -> imprime o relatório integrado (RF15) e sai
    python main.py --rendimento -> imprime o relatório de rendimento escolar (RF23) e sai
    python main.py --demo       -> roda a Integração Final da Seção 5 do enunciado e sai

O SistemaIntegrado é criado UMA vez aqui (RF11: carrega todos os .txt para a memória)
e entregue pronto para a interface escolhida. Isso é injeção de dependência: as
interfaces não sabem de onde vêm os dados, só recebem o objeto que os gerencia.
"""
import argparse
import sys

from demonstracao import executar_demonstracao
from menu_console import MenuConsole
from sistema import PASTA_DADOS, SistemaIntegrado


def criar_parser():
    """Monta o parser da linha de comando.

    Returns:
        argparse.ArgumentParser: com os modos --console, --relatorio, --rendimento, --demo e a opção --dados.
    """
    parser = argparse.ArgumentParser(description="Sistema de Gestão Acadêmica (ALFA + BETA)")
    modo = parser.add_mutually_exclusive_group()
    modo.add_argument("--console", action="store_true", help="usar o menu de terminal")
    modo.add_argument("--relatorio", action="store_true", help="imprimir o relatório integrado e sair")
    modo.add_argument("--rendimento", action="store_true",
                      help="imprimir o relatório de rendimento escolar (notas e médias) e sair")
    modo.add_argument("--demo", action="store_true",
                      help="cadastrar professor, curso, disciplina e aluno e mostrar o relatório")
    parser.add_argument("--dados", default=PASTA_DADOS, help="pasta dos arquivos .txt")
    return parser


def abrir_interface_grafica(sistema):
    """Tenta abrir a GUI. Devolve False se o ambiente não suportar Tkinter."""
    try:
        # Import "tardio": se o Tkinter não estiver instalado, o erro acontece aqui
        # e não derruba o programa inteiro logo na primeira linha.
        from interface_grafica import executar
    except ImportError as erro:
        print(f"[aviso] Tkinter indisponível ({erro}). Abrindo o menu de console.")
        return False
    try:
        executar(sistema)
    except RuntimeError as erro:
        print(f"[aviso] {erro} Abrindo o menu de console.")
        return False
    return True


def main(argv=None):
    """Executa o sistema no modo pedido.

    Args:
        argv (list[str] | None): argumentos (None = ``sys.argv``). Útil nos testes.

    Returns:
        int: código de saída do processo (0 = sucesso).
    """
    args = criar_parser().parse_args(argv)
    sistema = SistemaIntegrado(args.dados)   # RF11: carregamento inicial

    if args.demo:
        return 0 if executar_demonstracao(sistema) else 1
    if args.relatorio:
        for numero, frase in enumerate(sistema.relatorio(), start=1):
            print(f"{numero:>3}. {frase}")
        return 0
    if args.rendimento:
        linhas = sistema.relatorio_rendimento()
        if not linhas:
            print("Ainda não há notas lançadas.")
        for numero, linha in enumerate(linhas, start=1):
            print(f"{numero:>3}. {linha.frase}")
        return 0
    if args.console or not abrir_interface_grafica(sistema):
        return MenuConsole(sistema).executar()
    return 0


if __name__ == "__main__":
    sys.exit(main())
