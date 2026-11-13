"""RF17 - Painel acadêmico em Tkinter; reutiliza exclusivamente os gerenciadores do sistema.

Execução recomendada: python main.py (RF16). Necessita ambiente gráfico com Tkinter;
sem ele, o main.py abre automaticamente o menu de console.
"""
import tkinter as tk
from tkinter import ttk, messagebox

from avaliacao import Nota
from demonstracao import executar_demonstracao
from sistema import ENTIDADES, SistemaIntegrado

BG = '#f2f5fa'
NAV = '#14243d'
NAV2 = '#1e3554'
INK = '#17243a'
MUTED = '#62728a'
ACCENT = '#2863c5'
BORDER = '#dce3ed'
WHITE = '#ffffff'


class AplicacaoAcademica(tk.Tk):
    """Interface de CRUD generica, com menu lateral e relatorio integrado."""

    def __init__(self, sistema=None):
        """Monta a janela principal.

        Args:
            sistema (SistemaIntegrado | None): fachada com os dados; se None, cria uma
                com a pasta padrão.

        Raises:
            tkinter.TclError: se não houver ambiente gráfico.
        """
        super().__init__()
        self.sistema = sistema or SistemaIntegrado()
        self.title('Campus | Gestao Academica')
        self.geometry('1190x760')
        self.minsize(920, 610)
        self.configure(bg=BG)
        self.entidade_atual = None
        self.itens_visiveis = []
        self.busca_var = tk.StringVar()
        self._estilizar()
        self._montar_estrutura()
        self.mostrar_inicio()
        # RF18: o "X" da janela e o atalho Ctrl+Q passam pelo mesmo encerramento controlado
        self.protocol('WM_DELETE_WINDOW', self.encerrar)
        self.bind_all('<Control-q>', lambda _: self.encerrar())
        avisos = self.sistema.avisos_de_carga()
        if avisos:
            self.after(200, lambda: messagebox.showwarning(
                'Aviso de integridade', 'Algumas linhas dos arquivos TXT nao puderam ser carregadas:\n\n' + '\n'.join(avisos[:12])))

    def _estilizar(self):
        """Configura o tema ttk (tabela, cabeçalho, barra de rolagem e combobox)."""
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure('Acad.Treeview', background=WHITE, fieldbackground=WHITE,
                        foreground=INK, rowheight=38, borderwidth=0, font=('Segoe UI', 10))
        style.configure('Acad.Treeview.Heading', background='#edf2fa', foreground=INK,
                        font=('Segoe UI', 10, 'bold'), padding=(13, 11), borderwidth=0)
        style.map('Acad.Treeview', background=[('selected', '#dceafe')], foreground=[('selected', INK)])
        style.configure('Acad.Vertical.TScrollbar', background='#cbd5e1', troughcolor=WHITE)
        style.configure('Acad.TCombobox', padding=7)

    def _texto(self, parent, value, size=11, color=INK, bold=False, **kwargs):
        """Atalho para criar um Label com a tipografia do sistema."""
        return tk.Label(parent, text=value, bg=kwargs.pop('bg', WHITE), fg=color,
                        font=('Segoe UI', size, 'bold' if bold else 'normal'), **kwargs)

    def _botao(self, parent, rotulo, callback, cor=ACCENT, fg=WHITE, **kwargs):
        """Atalho para criar um botão plano com as cores do sistema."""
        return tk.Button(parent, text=rotulo, command=callback, bg=cor, fg=fg,
                         activebackground=cor, activeforeground=fg, relief='flat',
                         cursor='hand2', bd=0, padx=16, pady=11,
                         font=('Segoe UI', 10, 'bold'), **kwargs)

    def _montar_estrutura(self):
        """Cria o layout fixo: barra lateral de navegação, topo e área de conteúdo."""
        sidebar = tk.Frame(self, bg=NAV, width=236)
        sidebar.pack(side='left', fill='y')
        sidebar.pack_propagate(False)
        tk.Label(sidebar, text='▣  CAMPUS', bg=NAV, fg=WHITE,
                 font=('Segoe UI', 20, 'bold')).pack(anchor='w', padx=24, pady=(33, 6))
        tk.Label(sidebar, text='GESTÃO ACADÊMICA', bg=NAV, fg='#9aafcb',
                 font=('Segoe UI', 9, 'bold')).pack(anchor='w', padx=26, pady=(0, 39))
        tk.Label(sidebar, text='NAVEGAÇÃO', bg=NAV, fg='#8197b5',
                 font=('Segoe UI', 9, 'bold')).pack(anchor='w', padx=26, pady=(0, 12))
        for titulo, callback in [
            ('▦   Visão geral', self.mostrar_inicio),
            ('▤   Cursos', lambda: self.mostrar_entidade('curso')),
            ('♙   Alunos', lambda: self.mostrar_entidade('aluno')),
            ('♧   Professores', lambda: self.mostrar_entidade('professor')),
            ('▧   Disciplinas', lambda: self.mostrar_entidade('disciplina')),
            ('▣   Relatório integrado', self.mostrar_relatorio),
            ('✎   Notas', self.mostrar_notas),
            ('★   Rendimento escolar', self.mostrar_rendimento),
        ]:
            tk.Button(sidebar, text=titulo, command=callback, anchor='w', bg=NAV,
                      fg='#dfebfa', activebackground=NAV2, activeforeground=WHITE,
                      relief='flat', bd=0, highlightthickness=0, padx=25, pady=15, cursor='hand2',
                      font=('Segoe UI', 11)).pack(fill='x')
        tk.Label(sidebar, text='ALFA  +  BETA  •  TXT', bg=NAV, fg='#8197b5',
                 font=('Segoe UI', 9)).pack(side='bottom', anchor='w', padx=25, pady=(8, 25))
        # RF18: saída explícita, separada da navegação para não ser clicada por engano
        tk.Button(sidebar, text='⏻   Sair do sistema', command=self.encerrar, anchor='w',
                  bg=NAV, fg='#ffb4ab', activebackground='#3a2030', activeforeground=WHITE,
                  relief='flat', bd=0, highlightthickness=0, padx=25, pady=15, cursor='hand2',
                  font=('Segoe UI', 11)).pack(side='bottom', fill='x')
        self.principal = tk.Frame(self, bg=BG)
        self.principal.pack(side='left', fill='both', expand=True)
        self.topo = tk.Frame(self.principal, bg=WHITE, height=74, highlightbackground=BORDER,
                             highlightthickness=1)
        self.topo.pack(fill='x')
        self.topo.pack_propagate(False)
        self.titulo = self._texto(self.topo, 'Visão geral', 18, INK, True)
        self.titulo.pack(side='left', padx=31, pady=18)
        self._texto(self.topo, 'Sistema integrado  /  2026', 10, MUTED).pack(side='right', padx=30)
        self.corpo = tk.Frame(self.principal, bg=BG)
        self.corpo.pack(fill='both', expand=True, padx=30, pady=26)

    def _limpar(self, titulo):
        """Remove o conteúdo atual da área central e troca o título do topo."""
        for child in self.corpo.winfo_children():
            child.destroy()
        self.titulo.configure(text=titulo)

    def _cartao(self, parent, **kwargs):
        """Cria um painel branco com borda (componente visual base)."""
        return tk.Frame(parent, bg=WHITE, highlightbackground=BORDER,
                        highlightthickness=1, **kwargs)

    def mostrar_inicio(self):
        """Tela 'Visão geral': contadores por entidade e atalhos."""
        self.entidade_atual = None
        self._limpar('Visão geral')
        self._texto(self.corpo, 'Acompanhe os dados da instituição', 12, MUTED,
                    bg=BG).pack(anchor='w', pady=(0, 24))
        cards = tk.Frame(self.corpo, bg=BG)
        cards.pack(fill='x')
        for i, (chave, nome, descricao) in enumerate([
            ('curso', 'Cursos', 'Programas cadastrados'),
            ('aluno', 'Alunos', 'Matrículas ativas'),
            ('professor', 'Professores', 'Corpo docente'),
            ('disciplina', 'Disciplinas', 'Componentes curriculares'),
            ('nota', 'Notas', 'Avaliações lançadas'),
        ]):
            card = self._cartao(cards)
            card.grid(row=0, column=i, sticky='nsew', padx=(0, 13 if i < 4 else 0))
            cards.grid_columnconfigure(i, weight=1)
            self._texto(card, nome, 11, MUTED).pack(anchor='w', padx=20, pady=(20, 9))
            gerente = (self.sistema.notas if chave == 'nota'
                       else getattr(self.sistema, ENTIDADES[chave]['gerente']))
            self._texto(card, str(len(gerente.listar())), 29, INK, True).pack(anchor='w', padx=20)
            self._texto(card, descricao, 9, MUTED).pack(anchor='w', padx=20, pady=(4, 20))
        detalhe = self._cartao(self.corpo)
        detalhe.pack(fill='x', pady=(26, 0))
        self._texto(detalhe, 'Bem-vindo ao Campus', 17, INK, True).pack(anchor='w', padx=24, pady=(25, 9))
        self._texto(detalhe, 'Organize cursos, matrículas, professores e disciplinas em um só lugar.\n'
                    'Todas as alterações são salvas nos arquivos TXT do projeto.', 11, MUTED,
                    justify='left').pack(anchor='w', padx=24, pady=(0, 20))
        acoes = tk.Frame(detalhe, bg=WHITE)
        acoes.pack(anchor='w', padx=24, pady=(0, 25))
        self._botao(acoes, 'Ver relatório integrado  →', self.mostrar_relatorio).pack(side='left')
        self._botao(acoes, '▶  Executar demonstração', self.rodar_demonstracao,
                    cor='#e7efff', fg=ACCENT).pack(side='left', padx=12)

    def rodar_demonstracao(self):
        """Seção 5 do enunciado: roda o fluxo completo e abre o relatório com o resultado."""
        mensagens = []
        ok = executar_demonstracao(self.sistema, saida=mensagens.append, mostrar_arquivos=False)
        # Só as linhas das etapas (sem o relatório, que será aberto na tela própria)
        resumo = [m.strip() for m in mensagens if m.strip().startswith(('[', '+', '= ', 'x'))
                  and 'Relatório' not in m]
        if not ok:
            messagebox.showerror('Demonstração interrompida', '\n'.join(resumo), parent=self)
            return
        self.mostrar_relatorio()
        messagebox.showinfo('Demonstração concluída', '\n'.join(resumo) +
                            '\n\nOs registros DEMO foram gravados nos arquivos .txt.', parent=self)

    def mostrar_entidade(self, chave):
        """Tela de CRUD de uma entidade (RF01-RF05): busca, tabela e ações.

        Args:
            chave (str): chave em ENTIDADES ("curso", "aluno", "professor", "disciplina").
        """
        self.entidade_atual = chave
        meta = ENTIDADES[chave]
        gerente = getattr(self.sistema, meta['gerente'])
        self._limpar(meta['titulo'])
        cab = tk.Frame(self.corpo, bg=BG)
        cab.pack(fill='x', pady=(0, 20))
        self._texto(cab, f'Gerencie {meta["titulo"].lower()} e seus registros',
                    11, MUTED, bg=BG).pack(side='left')
        self._botao(cab, '+  Novo cadastro', lambda: self._formulario(chave)).pack(side='right')
        painel = self._cartao(self.corpo)
        painel.pack(fill='both', expand=True)
        busca = tk.Frame(painel, bg=WHITE)
        busca.pack(fill='x', padx=20, pady=(19, 15))
        self._texto(busca, 'Buscar:', 10, MUTED).pack(side='left', padx=(0, 9))
        self.busca_var.set('')
        entrada = ttk.Entry(busca, textvariable=self.busca_var, width=40, font=('Segoe UI', 10))
        entrada.pack(side='left', ipady=6)
        entrada.bind('<KeyRelease>', lambda _: self._atualizar_tabela())
        self._botao(busca, 'Limpar', lambda: self.busca_var.set('') or self._atualizar_tabela(),
                    cor='#e9eef6', fg=INK).pack(side='left', padx=12)
        self.contador = self._texto(busca, '', 10, MUTED)
        self.contador.pack(side='right')
        tabela_frame = tk.Frame(painel, bg=WHITE)
        tabela_frame.pack(fill='both', expand=True, padx=19, pady=(0, 12))
        campos = [c for c, _ in meta['campos']]
        self.tabela = ttk.Treeview(tabela_frame, columns=campos, show='headings',
                                    style='Acad.Treeview', selectmode='browse')
        for campo, rotulo in meta['campos']:
            self.tabela.heading(campo, text=rotulo)
            self.tabela.column(campo, minwidth=110, width=150 if campo == 'nome' else 125,
                               stretch=True, anchor='w')
        rolagem = ttk.Scrollbar(tabela_frame, orient='vertical', command=self.tabela.yview)
        self.tabela.configure(yscrollcommand=rolagem.set)
        rolagem.pack(side='right', fill='y')
        self.tabela.pack(fill='both', expand=True)
        self.tabela.bind('<Double-1>', lambda _: self._selecionar_acao('alterar'))
        acoes = tk.Frame(painel, bg=WHITE)
        acoes.pack(fill='x', padx=20, pady=(0, 19))
        self._botao(acoes, 'Editar selecionado', lambda: self._selecionar_acao('alterar'),
                    cor='#e7efff', fg=ACCENT).pack(side='left')
        self._botao(acoes, 'Excluir selecionado', lambda: self._selecionar_acao('excluir'),
                    cor='#fff0ee', fg='#b42318').pack(side='left', padx=10)
        self._botao(acoes, 'Atualizar lista', self._atualizar_tabela,
                    cor='#eef1f6', fg=INK).pack(side='right')
        self._atualizar_tabela()

    def _atualizar_tabela(self):
        """Recarrega a tabela a partir da memória, aplicando o filtro de busca (RF02/RF03)."""
        if self.entidade_atual is None or not hasattr(self, 'tabela'):
            return
        meta = ENTIDADES[self.entidade_atual]
        gerente = getattr(self.sistema, meta['gerente'])
        termo = self.busca_var.get().strip()
        itens = gerente.pesquisar(termo) if termo else gerente.listar()
        self.tabela.delete(*self.tabela.get_children())
        for item in itens:
            valores = [getattr(item, campo) for campo, _ in meta['campos']]
            self.tabela.insert('', 'end', iid=str(valores[0]), values=valores)
        self.contador.configure(text=f'{len(itens)} registro(s)')

    def _selecionar_acao(self, acao):
        """Executa 'alterar' ou 'excluir' sobre a linha selecionada.

        Args:
            acao (str): ``"alterar"`` ou ``"excluir"``.
        """
        selecionado = self.tabela.selection()
        if not selecionado:
            messagebox.showinfo('Seleção necessária', 'Selecione um registro na tabela primeiro.', parent=self)
            return
        chave = self.entidade_atual
        gerente = getattr(self.sistema, ENTIDADES[chave]['gerente'])
        codigo = selecionado[0]
        if acao == 'alterar':
            self._formulario(chave, gerente.obter(codigo))
            return
        if not messagebox.askyesno('Confirmar exclusão',
                                   f'Deseja realmente excluir o registro {codigo}?', parent=self):
            return
        try:
            gerente.excluir(codigo)
        except (ValueError, LookupError, OSError) as e:
            messagebox.showerror('Não foi possível excluir', str(e), parent=self)
        else:
            self._atualizar_tabela()
            messagebox.showinfo('Excluído', 'Registro excluído e arquivo TXT atualizado.', parent=self)

    # Mensagens orientativas; as regras efetivas são aplicadas pelas entidades.
    DICAS = {
        'matricula': '1 a 24 caracteres: letras, números, _ ou -.',
        'codigo_curso': '1 a 24 caracteres: letras, números, _ ou -.',
        'codigo_professor': '1 a 24 caracteres: letras, números, _ ou -.',
        'codigo_disciplina': '1 a 24 caracteres: letras, números, _ ou -.',
        'nome': 'De 1 a 120 caracteres, contendo letras.',
        'especialidade': 'De 1 a 120 caracteres, contendo letras.',
        'cpf': '11 dígitos (com ou sem a máscara 000.000.000-00).',
        'email': 'Ex.: nome@instituicao.edu.br (até 254 caracteres).',
        'modalidade': 'Selecione Presencial ou EAD.',
        'carga_horaria': 'Número inteiro de horas, maior que zero.',
    }

    def _formulario(self, chave, registro=None):
        """Abre o formulário modal de cadastro (RF01) ou edição (RF04).

        Campos de vínculo viram combobox com os códigos existentes, o que evita digitar
        um código inválido. A validação definitiva continua nas entidades/gerenciadores.

        Args:
            chave (str): chave em ENTIDADES.
            registro: registro a editar; None para um novo cadastro.
        """
        meta = ENTIDADES[chave]
        gerente = getattr(self.sistema, meta['gerente'])
        modal = tk.Toplevel(self)
        modal.title(('Editar' if registro else 'Cadastrar') + ' • ' + meta['titulo'])
        modal.configure(bg=WHITE)
        modal.transient(self)
        modal.grab_set()
        modal.resizable(True, True)

        largura = 560
        altura_desejada = 250 + len(meta['campos']) * 90
        limite_tela = max(520, modal.winfo_screenheight() - 120)
        altura = min(altura_desejada, limite_tela)
        modal.geometry(f'{largura}x{altura}')
        modal.minsize(520, min(altura, 520))

        cabecalho = tk.Frame(modal, bg=WHITE)
        cabecalho.pack(fill='x', padx=28, pady=(25, 0))
        self._texto(cabecalho, 'Editar registro' if registro else 'Novo cadastro',
                    19, INK, True).pack(anchor='w', pady=(0, 5))
        self._texto(cabecalho, meta['titulo'] + ' • Campos obrigatórios', 10, MUTED).pack(
            anchor='w', pady=(0, 16))

        conteudo = tk.Frame(modal, bg=WHITE)
        conteudo.pack(fill='both', expand=True, padx=(28, 16), pady=(0, 10))

        canvas = tk.Canvas(conteudo, bg=WHITE, highlightthickness=0, bd=0)
        rolagem = ttk.Scrollbar(conteudo, orient='vertical', command=canvas.yview,
                                style='Acad.Vertical.TScrollbar')
        canvas.configure(yscrollcommand=rolagem.set)
        rolagem.pack(side='right', fill='y')
        canvas.pack(side='left', fill='both', expand=True)

        campos_frame = tk.Frame(canvas, bg=WHITE)
        janela_campos = canvas.create_window((0, 0), window=campos_frame, anchor='nw')

        def atualizar_area(_=None):
            """Ajusta a área rolável ao tamanho do conteúdo."""
            canvas.configure(scrollregion=canvas.bbox('all'))

        def ajustar_largura(event):
            """Faz os campos acompanharem a largura da janela."""
            canvas.itemconfigure(janela_campos, width=event.width)

        campos_frame.bind('<Configure>', atualizar_area)
        canvas.bind('<Configure>', ajustar_largura)

        def ao_rolar_mouse(event):
            """Rola o formulário com a roda do mouse."""
            if event.delta:
                canvas.yview_scroll(int(-1 * (event.delta / 120)), 'units')

        def ativar_rolagem(_event):
            """Liga a roda do mouse enquanto o cursor está sobre o formulário."""
            canvas.bind_all('<MouseWheel>', ao_rolar_mouse)

        def desativar_rolagem(_event):
            """Desliga a roda do mouse ao sair do formulário."""
            canvas.unbind_all('<MouseWheel>')

        canvas.bind('<Enter>', ativar_rolagem)
        canvas.bind('<Leave>', desativar_rolagem)

        variaveis = {}
        primeiro_widget = None
        for indice, (campo, rotulo) in enumerate(meta['campos']):
            self._texto(campos_frame, rotulo.replace(' (horas)', ''), 10, INK, True).grid(
                row=indice * 3, column=0, sticky='w', pady=(7, 3))
            variavel = tk.StringVar(value=str(getattr(registro, campo)) if registro else '')
            variaveis[campo] = variavel
            if campo == 'modalidade':
                widget = ttk.Combobox(campos_frame, textvariable=variavel,
                                      values=('Presencial', 'EAD'), state='readonly', width=48,
                                      style='Acad.TCombobox')
            elif campo in ('codigo_curso', 'codigo_professor') and indice != 0:
                fonte = self.sistema.cursos if campo == 'codigo_curso' else self.sistema.professores
                valores = [getattr(e, fonte.chave) for e in fonte.listar()]
                widget = ttk.Combobox(campos_frame, textvariable=variavel, values=valores,
                                      width=48, state='readonly', style='Acad.TCombobox')
            else:
                widget = ttk.Entry(campos_frame, textvariable=variavel, font=('Segoe UI', 10))
            widget.grid(row=indice * 3 + 1, column=0, sticky='ew', ipady=6)
            dica = self.DICAS.get(campo, 'Campo obrigatório.')
            if registro and indice == 0:
                # RF04: o código também pode mudar; o gerenciador atualiza os vínculos
                dica += ' Ao alterar, os registros vinculados são atualizados juntos.'
            self._texto(campos_frame, dica, 9, MUTED, wraplength=470, justify='left').grid(
                row=indice * 3 + 2, column=0, sticky='w', pady=(2, 4))
            if primeiro_widget is None:
                primeiro_widget = widget
        campos_frame.grid_columnconfigure(0, weight=1)

        rodape = tk.Frame(modal, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
        rodape.pack(fill='x', side='bottom')
        botoes = tk.Frame(rodape, bg=WHITE)
        botoes.pack(fill='x', padx=28, pady=16)
        self._botao(botoes, 'Cancelar', modal.destroy, cor='#eef1f6', fg=INK).pack(side='right')

        def salvar():
            """Envia os dados ao gerenciador; em caso de erro mantém o modal aberto com a mensagem."""
            dados = {campo: var.get().strip() for campo, var in variaveis.items()}
            try:
                if registro is None:
                    gerente.cadastrar(meta['classe'](**dados))
                else:
                    gerente.alterar(getattr(registro, gerente.chave), **dados)
            except (ValueError, LookupError, TypeError, OSError) as e:
                messagebox.showerror('Confira os dados', str(e), parent=modal)
                return
            modal.destroy()
            self.mostrar_entidade(chave)
            messagebox.showinfo('Salvo com sucesso', 'Os dados foram gravados no arquivo TXT.', parent=self)

        self._botao(botoes, 'Salvar alterações' if registro else 'Cadastrar', salvar).pack(
            side='right', padx=(0, 12))
        modal.bind('<Return>', lambda _: salvar())
        modal.bind('<Escape>', lambda _: modal.destroy())
        modal.after(100, lambda: primeiro_widget.focus_set() if primeiro_widget else None)

    def mostrar_relatorio(self):
        """Tela do relatório integrado (RF15), somente leitura."""
        self.entidade_atual = None
        self._limpar('Relatório integrado')
        self._texto(self.corpo, 'Vínculos entre alunos, cursos, disciplinas e professores',
                    11, MUTED, bg=BG).pack(anchor='w', pady=(0, 20))
        painel = self._cartao(self.corpo)
        painel.pack(fill='both', expand=True)
        topo = tk.Frame(painel, bg=WHITE)
        topo.pack(fill='x', padx=22, pady=20)
        self._texto(topo, 'Relações acadêmicas', 15, INK, True).pack(side='left')
        self._botao(topo, 'Atualizar relatório', self.mostrar_relatorio,
                    cor='#e7efff', fg=ACCENT).pack(side='right')
        area = tk.Text(painel, wrap='word', font=('Segoe UI', 11), bg=WHITE,
                       fg=INK, relief='flat', padx=24, pady=18, spacing3=18)
        area.pack(fill='both', expand=True, padx=15, pady=(0, 15))
        linhas = self.sistema.relatorio()
        area.insert('1.0', '\n'.join(f'{i}.  {linha}' for i, linha in enumerate(linhas, 1))
                    if linhas else 'Ainda não há vínculos cadastrados para apresentar.')
        area.configure(state='disabled')

    # ---------- Módulo de Avaliação (RF19-RF24) ----------
    COLUNAS_NOTAS = (('matricula', 'Matrícula', 90), ('codigo_disciplina', 'Disciplina', 90),
                     ('nota1', 'Nota 1', 62), ('peso1', 'Peso 1', 62), ('nota2', 'Nota 2', 62),
                     ('peso2', 'Peso 2', 62), ('nota3', 'Nota 3', 62), ('peso3', 'Peso 3', 62),
                     ('media', 'Média', 78))

    def mostrar_notas(self):
        """Tela de notas: tabela com a média recalculada a cada exibição (RF21/RF24)."""
        self.entidade_atual = None
        self._limpar('Notas')
        cab = tk.Frame(self.corpo, bg=BG)
        cab.pack(fill='x', pady=(0, 20))
        self._texto(cab, 'Lance notas e pesos; a média ponderada é calculada automaticamente',
                    11, MUTED, bg=BG).pack(side='left')
        self._botao(cab, '+  Lançar notas', lambda: self._formulario_nota()).pack(side='right')
        painel = self._cartao(self.corpo)
        painel.pack(fill='both', expand=True)
        quadro = tk.Frame(painel, bg=WHITE)
        quadro.pack(fill='both', expand=True, padx=19, pady=(19, 12))
        colunas = [c for c, _, _ in self.COLUNAS_NOTAS]
        self.tabela = ttk.Treeview(quadro, columns=colunas, show='headings',
                                   style='Acad.Treeview', selectmode='browse')
        for campo, rotulo, largura in self.COLUNAS_NOTAS:
            self.tabela.heading(campo, text=rotulo)
            self.tabela.column(campo, minwidth=largura, width=largura, stretch=True, anchor='w')
        rolagem = ttk.Scrollbar(quadro, orient='vertical', command=self.tabela.yview)
        self.tabela.configure(yscrollcommand=rolagem.set)
        rolagem.pack(side='right', fill='y')
        self.tabela.pack(fill='both', expand=True)
        self.tabela.bind('<Double-1>', lambda _: self._acao_nota('alterar'))
        acoes = tk.Frame(painel, bg=WHITE)
        acoes.pack(fill='x', padx=20, pady=(0, 19))
        self._botao(acoes, 'Editar selecionado', lambda: self._acao_nota('alterar'),
                    cor='#e7efff', fg=ACCENT).pack(side='left')
        self._botao(acoes, 'Excluir selecionado', lambda: self._acao_nota('excluir'),
                    cor='#fff0ee', fg='#b42318').pack(side='left', padx=10)
        self.contador = self._texto(acoes, '', 10, MUTED)
        self.contador.pack(side='right', padx=(12, 0))
        self._botao(acoes, 'Atualizar lista', self._atualizar_notas,
                    cor='#eef1f6', fg=INK).pack(side='right')
        self._atualizar_notas()

    def _atualizar_notas(self):
        """Relê o notas.txt (RF24) e recarrega a tabela com a média recalculada."""
        self.tabela.delete(*self.tabela.get_children())
        notas = self.sistema.notas.listar()
        for nota in notas:
            valores = [str(getattr(nota, c)) for c, _, _ in self.COLUNAS_NOTAS if c != 'media']
            valores.append(str(self.sistema.notas.media(nota)))
            self.tabela.insert('', 'end', iid=f'{nota.matricula}/{nota.codigo_disciplina}',
                               values=valores)
        self.contador.configure(text=f'{len(notas)} registro(s)')

    def _acao_nota(self, acao):
        """Edita ou exclui a nota selecionada na tabela.

        Args:
            acao (str): ``"alterar"`` ou ``"excluir"``.
        """
        selecionado = self.tabela.selection()
        if not selecionado:
            messagebox.showinfo('Seleção necessária', 'Selecione um registro na tabela primeiro.',
                                parent=self)
            return
        identificacao = selecionado[0]
        if acao == 'alterar':
            try:
                self._formulario_nota(self.sistema.notas.obter(identificacao))
            except (LookupError, ValueError) as e:
                messagebox.showerror('Registro não encontrado', str(e), parent=self)
                self._atualizar_notas()
            return
        if not messagebox.askyesno('Confirmar exclusão',
                                   f'Deseja realmente excluir as notas {identificacao}?', parent=self):
            return
        try:
            self.sistema.notas.excluir(identificacao)
        except (ValueError, LookupError, OSError) as e:
            messagebox.showerror('Não foi possível excluir', str(e), parent=self)
        else:
            self._atualizar_notas()
            messagebox.showinfo('Excluído', 'Notas excluídas e arquivo TXT atualizado.', parent=self)

    def _formulario_nota(self, registro=None):
        """Formulário modal para lançar (RF19) ou alterar (RF24) notas e pesos.

        A matrícula e a disciplina viram combobox com os códigos existentes. A validação
        definitiva (0.0 a 10.0, pesos, vínculos) continua na entidade e no gerenciador.

        Args:
            registro (Nota | None): registro a editar; None para um novo lançamento.
        """
        modal = tk.Toplevel(self)
        modal.title(('Editar' if registro else 'Lançar') + ' • Notas')
        modal.configure(bg=WHITE)
        modal.transient(self)
        modal.grab_set()
        modal.geometry('560x720')
        modal.minsize(520, 600)
        self._texto(modal, 'Editar notas' if registro else 'Lançar notas', 19, INK, True).pack(
            anchor='w', padx=28, pady=(25, 4))
        self._texto(modal, 'Notas de 0.0 a 10.0 • Use ponto ou vírgula (ex.: 8.5)', 10, MUTED).pack(
            anchor='w', padx=28, pady=(0, 12))
        corpo = tk.Frame(modal, bg=WHITE)
        corpo.pack(fill='both', expand=True, padx=28)
        corpo.grid_columnconfigure(0, weight=1)
        campos = [('matricula', 'Matrícula do aluno'), ('codigo_disciplina', 'Código da disciplina'),
                  ('nota1', 'Nota 1'), ('peso1', 'Peso 1'), ('nota2', 'Nota 2'),
                  ('peso2', 'Peso 2'), ('nota3', 'Nota 3'), ('peso3', 'Peso 3')]
        fontes = {'matricula': [a.matricula for a in self.sistema.alunos.listar()],
                  'codigo_disciplina': [d.codigo_disciplina for d in self.sistema.disciplinas.listar()]}
        variaveis = {}
        primeiro = None
        for linha, (campo, rotulo) in enumerate(campos):
            self._texto(corpo, rotulo, 10, INK, True).grid(row=linha * 2, column=0, sticky='w',
                                                          pady=(7, 3))
            variavel = tk.StringVar(value=str(getattr(registro, campo)) if registro else '')
            variaveis[campo] = variavel
            if campo in fontes:
                widget = ttk.Combobox(corpo, textvariable=variavel, values=fontes[campo],
                                      state='readonly', style='Acad.TCombobox')
            else:
                widget = ttk.Entry(corpo, textvariable=variavel, font=('Segoe UI', 10))
            widget.grid(row=linha * 2 + 1, column=0, sticky='ew', ipady=6)
            primeiro = primeiro or widget
        rodape = tk.Frame(modal, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
        rodape.pack(fill='x', side='bottom')
        botoes = tk.Frame(rodape, bg=WHITE)
        botoes.pack(fill='x', padx=28, pady=16)
        self._botao(botoes, 'Cancelar', modal.destroy, cor='#eef1f6', fg=INK).pack(side='right')

        def salvar():
            """Envia ao gerenciador; em caso de erro mantém o modal aberto com a mensagem."""
            dados = {campo: var.get().strip() for campo, var in variaveis.items()}
            try:
                if registro is None:
                    self.sistema.notas.cadastrar(Nota(**dados))
                else:
                    identificacao = (registro.matricula, registro.codigo_disciplina)
                    self.sistema.notas.alterar(identificacao, **dados)
            except (ValueError, LookupError, TypeError, OSError) as e:
                messagebox.showerror('Confira os dados', str(e), parent=modal)
                return
            modal.destroy()
            self.mostrar_notas()
            messagebox.showinfo('Salvo com sucesso', 'Os dados foram gravados no arquivo TXT.',
                                parent=self)

        self._botao(botoes, 'Salvar alterações' if registro else 'Lançar', salvar).pack(
            side='right', padx=(0, 12))
        modal.bind('<Return>', lambda _: salvar())
        modal.bind('<Escape>', lambda _: modal.destroy())
        modal.after(100, lambda: primeiro.focus_set())

    def mostrar_rendimento(self):
        """Tela do relatório de rendimento escolar (RF23), somente leitura."""
        self.entidade_atual = None
        self._limpar('Rendimento escolar')
        cab = tk.Frame(self.corpo, bg=BG)
        cab.pack(fill='x', pady=(0, 20))
        self._texto(cab, 'Notas, pesos, média final e situação de cada aluno por disciplina',
                    11, MUTED, bg=BG).pack(side='left')
        self._botao(cab, 'Atualizar relatório', self.mostrar_rendimento,
                    cor='#e7efff', fg=ACCENT).pack(side='right')
        painel = self._cartao(self.corpo)
        painel.pack(fill='both', expand=True)
        quadro = tk.Frame(painel, bg=WHITE)
        quadro.pack(fill='both', expand=True, padx=19, pady=19)
        colunas = (('aluno', 'Aluno', 150), ('disciplina', 'Disciplina', 170),
                   ('notas', 'Notas e pesos', 300), ('media', 'Média final', 90),
                   ('status', 'Status', 90))
        tabela = ttk.Treeview(quadro, columns=[c for c, _, _ in colunas], show='headings',
                              style='Acad.Treeview', selectmode='browse')
        for campo, rotulo, largura in colunas:
            tabela.heading(campo, text=rotulo)
            tabela.column(campo, minwidth=largura, width=largura, stretch=True, anchor='w')
        tabela.tag_configure('Aprovado', foreground='#15803d')
        tabela.tag_configure('Reprovado', foreground='#b42318')
        rolagem = ttk.Scrollbar(quadro, orient='vertical', command=tabela.yview)
        tabela.configure(yscrollcommand=rolagem.set)
        rolagem.pack(side='right', fill='y')
        tabela.pack(fill='both', expand=True)
        for linha in self.sistema.relatorio_rendimento():
            tabela.insert('', 'end', tags=(linha.situacao,), values=(
                linha.aluno, linha.disciplina, linha.texto_notas, linha.media, linha.situacao))

    def encerrar(self):
        """RF18: confirma, informa que os dados já estão gravados e fecha a janela."""
        if not messagebox.askyesno('Sair do sistema', 'Deseja realmente encerrar o sistema?\n\n'
                                   + self.sistema.resumo_encerramento(), parent=self):
            return
        self.unbind_all('<MouseWheel>')
        self.destroy()   # encerra o mainloop de forma limpa, sem matar o processo


def executar(sistema=None):
    """Abre a janela. Levanta RuntimeError se não houver ambiente gráfico (main.py trata)."""
    try:
        app = AplicacaoAcademica(sistema)
    except tk.TclError as erro:
        raise RuntimeError('Não foi possível abrir a interface gráfica (sem ambiente de '
                           'área de trabalho).') from erro
    app.mainloop()


if __name__ == '__main__':
    executar()
