"""Testes automatizados dos requisitos funcionais RF01 a RF18.

Executar a partir da pasta do projeto:
    python -m unittest discover -s testes -v

Cada teste roda numa pasta temporária, então os .txt reais em dados/ nunca são alterados.
"""
import io
import shutil
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from alfa import Aluno, Curso
from beta import Disciplina, Professor
from avaliacao import Nota
from avaliacao.calculo import media_ponderada, status
from decimal import Decimal
from demonstracao import executar_demonstracao
from main import main
from menu_console import MenuConsole
from sistema import PASTA_DADOS, SistemaIntegrado


class BaseTeste(unittest.TestCase):
    """Cria uma cópia isolada de dados/ para cada teste e a apaga no final."""

    def setUp(self):
        self.pasta = Path(tempfile.mkdtemp())
        for arquivo in PASTA_DADOS.glob("*.txt"):
            shutil.copy(arquivo, self.pasta)
        self.sistema = SistemaIntegrado(self.pasta)

    def tearDown(self):
        shutil.rmtree(self.pasta, ignore_errors=True)

    def ler(self, nome):
        return (self.pasta / nome).read_text(encoding="utf-8").splitlines()


class TestCrud(BaseTeste):
    """RF01-RF05: operações de cadastro, listagem, pesquisa, alteração e exclusão."""

    def test_rf01_cadastrar_grava_no_txt(self):
        self.sistema.cursos.cadastrar(Curso("30", "Medicina", "presencial"))
        self.assertIn("30;Medicina;Presencial", self.ler("cursos.txt"))

    def test_rf02_listar_converte_em_objetos(self):
        alunos = self.sistema.alunos.listar()
        self.assertEqual(2, len(alunos))
        self.assertIsInstance(alunos[0], Aluno)

    def test_rf03_pesquisar_por_codigo_e_por_nome(self):
        self.assertEqual("João Silva", self.sistema.alunos.pesquisar("202301")[0].nome)
        self.assertEqual("202301", self.sistema.alunos.pesquisar("joao")[0].matricula)

    def test_rf04_alterar_reflete_no_arquivo(self):
        self.sistema.professores.alterar("P01", especialidade="Banco de Dados")
        self.assertIn("P01;Carlos Souza;111.222.333-44;Banco de Dados", self.ler("professores.txt"))

    def test_rf04_alterar_o_codigo_atualiza_vinculos_em_cascata(self):
        self.sistema.cursos.alterar("10", codigo_curso="15")
        self.assertIn("15;Análise e Desenvolvimento de Sistemas;Presencial", self.ler("cursos.txt"))
        self.assertIn("202301;João Silva;123.456.789-00;joao.silva@email.com;15", self.ler("alunos.txt"))
        self.assertIn("D01;Programação Orientada a Objetos;80;P01;15", self.ler("disciplinas.txt"))
        # o relatório continua ligando tudo depois da troca
        self.assertTrue(any("João Silva" in f and "Carlos Souza" in f for f in self.sistema.relatorio()))

    def test_rf04_alterar_codigo_do_professor_atualiza_disciplinas(self):
        self.sistema.professores.alterar("P02", codigo_professor="P20")
        self.assertIn("D02;Engenharia de Requisitos;60;P20;20", self.ler("disciplinas.txt"))

    def test_rf04_codigo_novo_ja_existente_e_rejeitado_sem_alterar_nada(self):
        antes = self.ler("alunos.txt")
        with self.assertRaises(ValueError):
            self.sistema.cursos.alterar("10", codigo_curso="20")
        self.assertEqual(antes, self.ler("alunos.txt"))
        self.assertIsNotNone(self.sistema.cursos.buscar("10"))

    def test_rf04_falha_de_disco_na_cascata_desfaz_tudo(self):
        alunos = self.sistema.alunos
        salvar_original = alunos.salvar
        tentativas = []

        def falhar_uma_vez():
            tentativas.append(1)
            if len(tentativas) == 1:
                raise OSError("disco cheio (simulado)")
            salvar_original()          # o rollback consegue regravar

        alunos.salvar = falhar_uma_vez
        with self.assertRaises(OSError):
            self.sistema.cursos.alterar("10", codigo_curso="15")
        self.assertIsNotNone(self.sistema.cursos.buscar("10"))
        self.assertIsNone(self.sistema.cursos.buscar("15"))
        self.assertEqual("10", alunos.buscar("202301").codigo_curso)
        self.assertIn("10;Análise e Desenvolvimento de Sistemas;Presencial", self.ler("cursos.txt"))

    def test_rf04_alterar_codigo_pelo_menu_console(self):
        fila = iter(["1", "4", "20", "21", "", "", "0", "0", "s"])
        MenuConsole(self.sistema, entrada=lambda _: next(fila), saida=lambda _: None).executar()
        self.assertEqual("21", self.sistema.alunos.buscar("202302").codigo_curso)

    def test_rf05_excluir_remove_do_arquivo(self):
        self.sistema.notas.excluir(("202302", "D02"))     # aluno com notas só sai depois delas
        self.sistema.alunos.excluir("202302")
        self.assertFalse(any(l.startswith("202302;") for l in self.ler("alunos.txt")))

    def test_codigo_duplicado_e_rejeitado(self):
        with self.assertRaises(ValueError):
            self.sistema.cursos.cadastrar(Curso("10", "Outro", "EAD"))


class TestAtributos(BaseTeste):
    """RF06-RF09: atributos obrigatórios e regras de validação dos campos."""

    def test_rf06_a_rf09_campos_obrigatorios(self):
        self.assertEqual(Aluno.CAMPOS, ("matricula", "nome", "cpf", "email", "codigo_curso"))
        self.assertEqual(Curso.CAMPOS, ("codigo_curso", "nome", "modalidade"))
        self.assertEqual(Professor.CAMPOS, ("codigo_professor", "nome", "cpf", "especialidade"))
        self.assertEqual(Disciplina.CAMPOS, ("codigo_disciplina", "nome", "carga_horaria",
                                             "codigo_professor", "codigo_curso"))

    def test_rf07_modalidade_apenas_presencial_ou_ead(self):
        with self.assertRaises(ValueError):
            Curso("40", "Direito", "Híbrido")

    def test_campo_vazio_ou_com_separador_e_rejeitado(self):
        with self.assertRaises(ValueError):
            Professor("P9", "", "11122233344", "Física")
        with self.assertRaises(ValueError):
            Professor("P9", "Ana;Hack", "11122233344", "Física")

    def test_caracteres_de_controle_sao_bloqueados(self):
        with self.assertRaises(ValueError):
            Professor("P9", "Ana", "11122233344", "Física\x1b[31m")


class TestPersistencia(BaseTeste):
    """RF10-RF12: formato do .txt, carregamento inicial e sincronização de escrita."""

    def test_rf10_separador_ponto_e_virgula(self):
        for nome in ("alunos.txt", "cursos.txt", "professores.txt", "disciplinas.txt"):
            self.assertTrue(all(";" in linha for linha in self.ler(nome)))

    def test_rf11_carregamento_inicial(self):
        novo = SistemaIntegrado(self.pasta)
        self.assertEqual(2, len(novo.disciplinas.listar()))

    def test_rf11_arquivo_salvo_com_bom_e_lido_normalmente(self):
        arquivo = self.pasta / "cursos.txt"
        arquivo.write_bytes(b"\xef\xbb\xbf" + arquivo.read_bytes())   # BOM do Bloco de Notas
        novo = SistemaIntegrado(self.pasta)
        self.assertIsNotNone(novo.cursos.buscar("10"))
        self.assertEqual([], novo.cursos.linhas_ignoradas)

    def test_rf12_escrita_persiste_entre_execucoes(self):
        self.sistema.professores.cadastrar(Professor("P03", "Rita Costa", "22233344455", "Redes"))
        self.assertIsNotNone(SistemaIntegrado(self.pasta).professores.buscar("P03"))


class TestIntegracao(BaseTeste):
    """RF13-RF15: vínculos entre entidades, integridade referencial e relatório."""

    def test_rf13_aluno_exige_curso_existente(self):
        with self.assertRaises(ValueError):
            self.sistema.alunos.cadastrar(Aluno("9", "Ana", "99988877766", "a@b.com", "999"))

    def test_rf14_disciplina_exige_professor_e_curso(self):
        with self.assertRaises(ValueError):
            self.sistema.disciplinas.cadastrar(Disciplina("D9", "Física", 40, "PX", "10"))
        with self.assertRaises(ValueError):
            self.sistema.disciplinas.cadastrar(Disciplina("D9", "Física", 40, "P01", "999"))

    def test_exclusao_bloqueada_quando_ha_dependentes(self):
        with self.assertRaises(ValueError):
            self.sistema.cursos.excluir("10")

    def test_rf15_frase_do_relatorio(self):
        self.assertIn("O Aluno João Silva está matriculado no curso Análise e Desenvolvimento "
                      "de Sistemas, assistindo a disciplina Programação Orientada a Objetos "
                      "com o professor Carlos Souza", self.sistema.relatorio())

    def test_rf15_uma_linha_por_disciplina_do_curso(self):
        self.sistema.disciplinas.cadastrar(Disciplina("D03", "Estrutura de Dados", 60, "P02", "10"))
        frases_joao = [f for f in self.sistema.relatorio() if "João Silva" in f]
        self.assertEqual(2, len(frases_joao))


class TestInterfaceConsole(BaseTeste):
    """RF17-RF18: menu de console simulado com respostas pré-definidas."""

    def executar_menu(self, respostas):
        """Simula o usuário digitando as respostas, em ordem."""
        fila = iter(respostas)
        saida = []
        codigo = MenuConsole(self.sistema, entrada=lambda _: next(fila),
                             saida=saida.append).executar()
        return codigo, "\n".join(map(str, saida))

    def test_rf17_cadastro_completo_pelo_menu(self):
        codigo, texto = self.executar_menu(
            ["1", "1", "50", "Nutrição", "EAD", "0", "0", "s"])
        self.assertEqual(0, codigo)
        self.assertIn("Cadastrado com sucesso", texto)
        self.assertIsNotNone(self.sistema.cursos.buscar("50"))

    def test_rf17_alterar_mantendo_campos_com_enter(self):
        self.executar_menu(["2", "4", "202301", "", "", "", "novo@email.com", "", "0", "0", "s"])
        aluno = self.sistema.alunos.buscar("202301")
        self.assertEqual(("João Silva", "novo@email.com"), (aluno.nome, aluno.email))

    def test_rf17_relatorio_pelo_menu(self):
        _, texto = self.executar_menu(["5", "0", "s"])
        self.assertIn("assistindo a disciplina Engenharia de Requisitos", texto)

    def test_rf18_sair_com_confirmacao(self):
        codigo, texto = self.executar_menu(["0", "n", "0", "s"])
        self.assertEqual(0, codigo)
        self.assertIn("Sistema encerrado", texto)

    def test_rf18_ctrl_d_encerra_sem_erro(self):
        def fim_de_entrada(_):
            raise EOFError
        saida = []
        codigo = MenuConsole(self.sistema, entrada=fim_de_entrada, saida=saida.append).executar()
        self.assertEqual(0, codigo)
        self.assertIn("Sistema encerrado. Até logo!", saida)

    def test_opcao_invalida_nao_quebra_o_menu(self):
        _, texto = self.executar_menu(["abc", "0", "s"])
        self.assertIn("Opção inválida", texto)


class TestAvaliacao(BaseTeste):
    """RF19-RF24: notas, pesos, média ponderada, teto de 10.0 e relatório de rendimento."""

    def nota(self, matricula="202301", disciplina="D02", n1="8.5", p1="2", n2="7.0", p2="3",
             n3="9.0", p3="5"):
        return Nota(matricula, disciplina, n1, p1, n2, p2, n3, p3)

    # --- RF19: estrutura ---
    def test_rf19_registro_tem_matricula_disciplina_tres_notas_e_tres_pesos(self):
        self.assertEqual(("matricula", "codigo_disciplina", "nota1", "peso1", "nota2", "peso2",
                          "nota3", "peso3"), Nota.CAMPOS)
        nota = self.nota()
        self.assertEqual((Decimal("8.5"), Decimal("2")), (nota.nota1, nota.peso1))

    def test_rf19_aluno_e_disciplina_precisam_existir(self):
        with self.assertRaises(ValueError):
            self.sistema.notas.cadastrar(self.nota(matricula="999999"))
        with self.assertRaises(ValueError):
            self.sistema.notas.cadastrar(self.nota(disciplina="XXX"))

    def test_rf19_um_registro_por_aluno_e_disciplina(self):
        with self.assertRaises(ValueError):
            self.sistema.notas.cadastrar(self.nota(matricula="202301", disciplina="D01"))

    def test_rf19_mesmo_aluno_pode_ter_varias_disciplinas(self):
        self.sistema.notas.cadastrar(self.nota())      # 202301 em D02
        self.assertEqual(2, len(self.sistema.notas.pesquisar("202301")))

    def test_rf19_exclusao_de_aluno_ou_disciplina_com_notas_e_bloqueada(self):
        with self.assertRaises(ValueError):
            self.sistema.alunos.excluir("202301")
        with self.assertRaises(ValueError):
            self.sistema.disciplinas.excluir("D01")

    def test_rf19_trocar_matricula_atualiza_o_notas_txt(self):
        self.sistema.alunos.alterar("202301", matricula="202399")
        self.assertIn("202399;D01;8.5;2;7.0;3;9.0;5", self.ler("notas.txt"))

    # --- RF20: persistência ---
    def test_rf20_formato_do_arquivo_notas_txt(self):
        self.sistema.notas.cadastrar(self.nota())
        self.assertIn("202301;D02;8.5;2;7.0;3;9.0;5", self.ler("notas.txt"))

    def test_rf20_nova_execucao_enxerga_as_notas(self):
        self.sistema.notas.cadastrar(self.nota())
        outro = SistemaIntegrado(self.pasta)
        self.assertEqual(3, len(outro.notas.listar()))

    def test_rf20_virgula_decimal_e_aceita_e_gravada_com_ponto(self):
        self.sistema.notas.cadastrar(self.nota(n1="8,5"))
        self.assertIn("202301;D02;8.5;2;7.0;3;9.0;5", self.ler("notas.txt"))

    def test_rf20_linha_malformada_e_ignorada_sem_derrubar_o_sistema(self):
        with open(self.pasta / "notas.txt", "a", encoding="utf-8") as arq:
            arq.write("202301;D02;abc;2;7.0;3;9.0;5\n")
        sistema = SistemaIntegrado(self.pasta)
        self.assertEqual(2, len(sistema.notas.listar()))
        self.assertTrue(any("notas.txt" in aviso for aviso in sistema.avisos_de_carga()))

    # --- RF21: média ponderada ---
    def test_rf21_media_ponderada_do_exemplo_do_enunciado(self):
        self.assertEqual(Decimal("8.30"), media_ponderada(self.nota()))

    def test_rf21_media_com_pesos_diferentes(self):
        nota = self.nota(n1="10", p1="1", n2="0", p2="1", n3="5", p3="2")   # (10+0+10)/4
        self.assertEqual(Decimal("5.00"), media_ponderada(nota))

    def test_rf21_media_e_calculada_na_hora_e_nao_gravada(self):
        self.assertNotIn("8.3", "\n".join(self.ler("notas.txt")))     # só notas e pesos no arquivo
        self.assertEqual(Decimal("8.30"), self.sistema.notas.media(self.sistema.notas.obter(("202301", "D01"))))

    def test_rf21_arredondamento_meio_para_cima(self):
        nota = self.nota(n1="7.0", p1="1", n2="7.0", p2="1", n3="7.01", p3="1")   # 7.00333...
        self.assertEqual(Decimal("7.00"), media_ponderada(nota))
        nota = self.nota(n1="6.99", p1="1", n2="6.99", p2="1", n3="7.0", p3="1")  # 6.99333...
        self.assertEqual(Decimal("6.99"), media_ponderada(nota))

    # --- RF22: validação e teto ---
    def test_rf22_nota_fora_do_intervalo_e_rejeitada(self):
        for invalida in ("10.1", "-1", "11", "abc", "", "1e1", "nan"):
            with self.assertRaises(ValueError, msg=invalida):
                self.nota(n1=invalida)

    def test_rf22_limites_zero_e_dez_sao_aceitos(self):
        self.assertEqual(Decimal("0.00"), media_ponderada(self.nota(n1="0", n2="0", n3="0")))
        self.assertEqual(Decimal("10.00"), media_ponderada(self.nota(n1="10", n2="10", n3="10")))

    def test_rf22_peso_negativo_ou_soma_zero_e_rejeitada(self):
        with self.assertRaises(ValueError):
            self.nota(p1="-1")
        with self.assertRaises(ValueError):
            self.nota(p1="0", p2="0", p3="0")

    def test_rf22_media_nunca_passa_de_dez_mesmo_com_dados_adulterados(self):
        nota = self.nota(n1="10", n2="10", n3="10")
        nota._nota1 = Decimal("30")          # contorna o setter de propósito
        self.assertEqual(Decimal("10.00"), media_ponderada(nota))

    def test_rf22_pesos_grandes_nao_estouram_o_teto(self):
        self.assertLessEqual(media_ponderada(self.nota(p1="500", p2="900", p3="1000")), Decimal("10.00"))

    def test_rf22_arquivo_com_nota_acima_de_dez_e_ignorado(self):
        with open(self.pasta / "notas.txt", "a", encoding="utf-8") as arq:
            arq.write("202301;D02;11;2;7.0;3;9.0;5\n")
        self.assertEqual(2, len(SistemaIntegrado(self.pasta).notas.listar()))

    # --- RF23: relatório ---
    def test_rf23_relatorio_com_nomes_notas_media_e_status(self):
        linhas = {l.matricula: l for l in self.sistema.relatorio_rendimento()}
        joao = linhas["202301"]
        self.assertEqual(("João Silva", "Programação Orientada a Objetos"), (joao.aluno, joao.disciplina))
        self.assertEqual(((Decimal("8.5"), Decimal("2")), (Decimal("7.0"), Decimal("3")),
                          (Decimal("9.0"), Decimal("5"))), joao.notas)
        self.assertEqual((Decimal("8.30"), "Aprovado"), (joao.media, joao.situacao))
        self.assertEqual((Decimal("6.05"), "Reprovado"), (linhas["202302"].media, linhas["202302"].situacao))

    def test_rf23_status_limite_de_aprovacao(self):
        self.assertEqual("Aprovado", status(Decimal("7.00")))
        self.assertEqual("Reprovado", status(Decimal("6.99")))

    def test_rf23_main_imprime_o_relatorio_de_rendimento(self):
        saida = io.StringIO()
        with redirect_stdout(saida):
            codigo = main(["--rendimento", "--dados", str(self.pasta)])
        self.assertEqual(0, codigo)
        self.assertIn("Maria Oliveira", saida.getvalue())
        self.assertIn("Reprovado", saida.getvalue())

    def test_rf23_relatorio_pelo_menu_console(self):
        saida = []
        fila = iter(["8", "0", "s"])
        MenuConsole(self.sistema, entrada=lambda _: next(fila), saida=saida.append).executar()
        texto = "\n".join(saida)
        self.assertIn("Média final: 8.30 | Status: Aprovado", texto)

    # --- RF24: alteração e recálculo ---
    def test_rf24_alterar_nota_recalcula_a_media(self):
        self.sistema.notas.alterar(("202302", "D02"), nota1="10", nota2="10", nota3="10")
        linha = [l for l in self.sistema.relatorio_rendimento() if l.matricula == "202302"][0]
        self.assertEqual((Decimal("10.00"), "Aprovado"), (linha.media, linha.situacao))

    def test_rf24_edicao_manual_do_arquivo_vale_na_proxima_leitura(self):
        arquivo = self.pasta / "notas.txt"
        texto = arquivo.read_text(encoding="utf-8").replace("5.0;2;6.0;3;6.5;5", "9.0;2;9.0;3;9.0;5")
        arquivo.write_text(texto, encoding="utf-8")
        linha = [l for l in self.sistema.relatorio_rendimento() if l.matricula == "202302"][0]
        self.assertEqual((Decimal("9.00"), "Aprovado"), (linha.media, linha.situacao))

    def test_rf24_alteracao_invalida_nao_muda_nada(self):
        antes = self.ler("notas.txt")
        with self.assertRaises(ValueError):
            self.sistema.notas.alterar(("202301", "D01"), nota1="12")
        self.assertEqual(antes, self.ler("notas.txt"))

    def test_rf24_alterar_peso_pelo_menu_console(self):
        fila = iter(["7", "4", "202302", "D02", "", "5", "", "", "", "", "0", "0", "s"])
        saida = []
        MenuConsole(self.sistema, entrada=lambda _: next(fila), saida=saida.append).executar()
        self.assertIn("202302;D02;5.0;5;6.0;3;6.5;5", self.ler("notas.txt"))
        self.assertTrue(any("Nova média" in linha for linha in saida))

    def test_lancar_notas_pelo_menu_console(self):
        self.sistema.notas.excluir(("202302", "D02"))
        fila = iter(["7", "1", "202302", "D02", "8", "1", "8", "1", "8", "1", "0", "0", "s"])
        MenuConsole(self.sistema, entrada=lambda _: next(fila), saida=lambda _: None).executar()
        self.assertIn("202302;D02;8;1;8;1;8;1", self.ler("notas.txt"))


class TestRequisitosTecnicos(BaseTeste):
    """Seção 4.A do PDF e dica do enunciado novo."""
    ENTIDADES = (Aluno, Curso, Professor, Disciplina)

    def test_entidades_tem_init_e_str_proprios(self):
        for classe in self.ENTIDADES:
            self.assertIn("__init__", vars(classe), classe.__name__)
            self.assertIn("__str__", vars(classe), classe.__name__)

    def test_encapsulamento_com_property_e_atributo_protegido(self):
        curso = Curso("77", "Física", "EAD")
        self.assertIsInstance(vars(Curso)["nome"], property)
        self.assertEqual("Física", curso._nome)
        with self.assertRaises(ValueError):
            curso.nome = ""          # o setter valida

    def test_entidades_nao_conhecem_o_arquivo(self):
        # Dica: entidades apenas como modelos de dados; o .txt é do gerenciador
        for classe in self.ENTIDADES:
            self.assertFalse(hasattr(classe, "para_linha"), classe.__name__)

    def test_gerenciador_converte_objeto_e_linha_nos_dois_sentidos(self):
        ger = self.sistema.disciplinas
        original = ger.buscar("D01")
        linha = ger._para_linha(original)
        self.assertEqual("D01;Programação Orientada a Objetos;80;P01;10\n", linha)
        self.assertEqual(str(original), str(ger._de_linha(linha)))


class TestIntegracaoFinal(BaseTeste):
    """Seção 5 do PDF: o main.py deve cadastrar tudo em ordem e gerar o relatório."""

    def test_demonstracao_cadastra_na_ordem_e_persiste(self):
        saida = []
        self.assertTrue(executar_demonstracao(self.sistema, saida.append))
        self.assertTrue(any(l.startswith("DEMO-P;") for l in self.ler("professores.txt")))
        self.assertTrue(any(l.startswith("DEMO-C;") for l in self.ler("cursos.txt")))
        self.assertIn("DEMO-D;Algoritmos e Estruturas de Dados;80;DEMO-P;DEMO-C",
                      self.ler("disciplinas.txt"))
        self.assertTrue(any(l.startswith("DEMO-A;") for l in self.ler("alunos.txt")))
        self.assertIn("O Aluno Lucas Ferreira está matriculado no curso Ciência da Computação, "
                      "assistindo a disciplina Algoritmos e Estruturas de Dados com o "
                      "professor Beatriz Ramos", self.sistema.relatorio())

    def test_demonstracao_pode_rodar_duas_vezes_sem_duplicar(self):
        executar_demonstracao(self.sistema, lambda _: None)
        self.assertTrue(executar_demonstracao(self.sistema, lambda _: None))
        self.assertEqual(1, sum(l.startswith("DEMO-A;") for l in self.ler("alunos.txt")))

    def test_demonstracao_pelo_menu_console(self):
        fila = iter(["6", "0", "s"])
        saida = []
        MenuConsole(self.sistema, entrada=lambda _: next(fila), saida=saida.append).executar()
        self.assertIn("Demonstração concluída.", [str(m).strip() for m in saida])


class TestPontoDeEntrada(BaseTeste):
    """RF16: execução pelo main.py com argumentos de linha de comando."""

    def rodar_main(self, *args):
        """Executa o main.py capturando o que ele imprime."""
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            codigo = main([*args, "--dados", str(self.pasta)])
        return codigo, buffer.getvalue()

    def test_rf16_main_gera_relatorio(self):
        codigo, texto = self.rodar_main("--relatorio")
        self.assertEqual(0, codigo)
        self.assertIn("O Aluno Maria Oliveira", texto)

    def test_rf16_main_roda_demonstracao(self):
        codigo, texto = self.rodar_main("--demo")
        self.assertEqual(0, codigo)
        self.assertIn("--- disciplinas.txt ---", texto)


if __name__ == "__main__":
    unittest.main()
