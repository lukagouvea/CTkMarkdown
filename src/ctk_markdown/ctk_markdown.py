"""
Tkinter component for Markdown rendering.
Uses ctk.CTkTextbox with custom tags for better control and rendering.
"""

import tkinter as tk
import tkinter.font as tkfont
import customtkinter as ctk
import re
import webbrowser


class CTkMarkdown(ctk.CTkTextbox):
    """CTkTextbox widget with Markdown rendering."""

    PYTHON_KEYWORDS = {
        'False', 'None', 'True', 'and', 'as', 'assert', 'async', 'await',
        'break', 'class', 'continue', 'def', 'del', 'elif', 'else', 'except',
        'finally', 'for', 'from', 'global', 'if', 'import', 'in', 'is',
        'lambda', 'nonlocal', 'not', 'or', 'pass', 'raise', 'return', 'try',
        'while', 'with', 'yield', 'print', 'len', 'range', 'str', 'int',
        'float', 'list', 'dict', 'set', 'tuple', 'open', 'input', 'type'
    }

    JS_KEYWORDS = {
        'async', 'await', 'break', 'case', 'catch', 'class', 'const', 'continue',
        'debugger', 'default', 'delete', 'do', 'else', 'export', 'extends',
        'finally', 'for', 'function', 'if', 'import', 'in', 'instanceof',
        'let', 'new', 'return', 'static', 'super', 'switch', 'this', 'throw',
        'try', 'typeof', 'var', 'void', 'while', 'with', 'yield', 'console',
        'log', 'true', 'false', 'null', 'undefined'
    }

    def __init__(self, master, markdown_text="", **kwargs):
        defaults = {
            "cursor": "arrow",
            "wrap": "word"
        }
        if 'bg' in kwargs: kwargs['fg_color'] = kwargs.pop('bg')
        if 'fg' in kwargs: kwargs['text_color'] = kwargs.pop('fg')
        if 'borderwidth' in kwargs: kwargs['border_width'] = kwargs.pop('borderwidth')
        if 'relief' in kwargs: kwargs.pop('relief')
        if 'yscrollcommand' in kwargs: kwargs.pop('yscrollcommand')
        defaults.update(kwargs)
        super().__init__(master, **defaults)

        # --- Estado de links e âncoras (reiniciado a cada render) ---
        self._link_counter = 0      # contador para gerar tags únicas por link
        self._link_tags: list[str] = []  # nomes das tags de link criadas
        self._anchors: dict[str, str] = {}  # slug → nome do mark no textbox

        self._setup_tags()
        try:
            ctk.AppearanceModeTracker.add(self._apply_theme, self)
        except Exception:
            pass
        self._render_markdown(markdown_text)

    # ──────────────────────────────────────────────
    #  Configuração de tags
    # ──────────────────────────────────────────────

    def _setup_tags(self):
        """Configure formatting tags."""
        base_font = tkfont.Font(font=self._textbox.cget('font'))
        base_size = int(base_font.cget('size'))
        base_family = base_font.cget('family')

        self._theme_colors = {
            'light': {
                'heading_1': '#1a1a2e', 'heading_2': '#16213e', 'heading_3': '#1f4068',
                'heading_4': '#1b1b2f', 'heading_5': '#464866', 'heading_6': '#6b778d',
                'muted': '#6c757d', 'link': '#0d6efd',
                'code_inline_fg': '#d63384', 'code_inline_bg': '#f6f8fa',
                'code_block_fg': '#1f2328', 'code_block_bg': '#EEEEEE',
                'code_keyword': '#0550ae', 'code_string': '#0a3069',
                'code_comment': '#6e7781', 'code_number': '#953800',
                'code_function': '#8250df', 'code_class': '#1f6feb',
                'code_decorator': '#a371f7', 'code_operator': '#24292f',
                'blockquote_fg': '#6c757d', 'blockquote_bg': '#f8f9fa',
                'list_bullet': '#6c757d', 'list_number': '#0d6efd',
                'hr': '#dee2e6',
                'table_border': '#dee2e6',
                'table_header_bg': '#e9ecef', 'table_header_fg': '#212529',
                'table_cell_bg': '#ffffff', 'table_cell_fg': '#212529',
                'table_row_alt_bg': '#f8f9fa',
                'checkbox_done': '#198754', 'checkbox_pending': '#dc3545',
                'copy_btn_bg': '#e9ecef', 'copy_btn_fg': '#495057',
                'copy_btn_active_bg': '#198754', 'copy_btn_active_fg': '#ffffff',
            },
            'dark': {
                'heading_1': '#e6edf3', 'heading_2': '#d1d9e0', 'heading_3': '#b6c2cf',
                'heading_4': '#9fb0c2', 'heading_5': '#8b9bb0', 'heading_6': '#778899',
                'muted': '#9aa0a6', 'link': '#4da3ff',
                'code_inline_fg': '#ff7aa8', 'code_inline_bg': '#2b2b2b',
                'code_block_fg': '#f0f6fc', 'code_block_bg': '#212121',
                'code_keyword': '#569cd6', 'code_string': '#ce9178',
                'code_comment': '#6a9955', 'code_number': '#b5cea8',
                'code_function': '#dcdcaa', 'code_class': '#4ec9b0',
                'code_decorator': '#c586c0', 'code_operator': '#d4d4d4',
                'blockquote_fg': '#9aa0a6', 'blockquote_bg': '#20242a',
                'list_bullet': '#9aa0a6', 'list_number': '#4da3ff',
                'hr': '#30363d',
                'table_border': '#30363d',
                'table_header_bg': '#30363d', 'table_header_fg': '#e6edf3',
                'table_cell_bg': '#0d1117', 'table_cell_fg': '#c9d1d9',
                'table_row_alt_bg': '#161b22',
                'checkbox_done': '#3fb950', 'checkbox_pending': '#ff7b72',
                'copy_btn_bg': '#30363d', 'copy_btn_fg': '#8b949e',
                'copy_btn_active_bg': '#238636', 'copy_btn_active_fg': '#ffffff',
            }
        }

        self._textbox.tag_config('h1', font=('Segoe UI', base_size + 12, 'bold'), spacing1=20, spacing3=10)
        self._textbox.tag_config('h2', font=('Segoe UI', base_size + 8, 'bold'),  spacing1=18, spacing3=8)
        self._textbox.tag_config('h3', font=('Segoe UI', base_size + 5, 'bold'),  spacing1=15, spacing3=6)
        self._textbox.tag_config('h4', font=('Segoe UI', base_size + 3, 'bold'),  spacing1=12, spacing3=5)
        self._textbox.tag_config('h5', font=('Segoe UI', base_size + 2, 'bold'),  spacing1=10, spacing3=4)
        self._textbox.tag_config('h6', font=('Segoe UI', base_size + 1, 'bold'),  spacing1=8,  spacing3=3)

        self._textbox.tag_config('bold',        font=(base_family, base_size, 'bold'))
        self._textbox.tag_config('italic',      font=(base_family, base_size, 'italic'))
        self._textbox.tag_config('bold_italic', font=(base_family, base_size, 'bold italic'))
        self._textbox.tag_config('strikethrough', overstrike=True)
        self._textbox.tag_config('underline',   underline=True)

        self._textbox.tag_config('code_inline', font=('Consolas', base_size), spacing1=2)
        self._textbox.tag_config('code_block',  font=('Consolas', base_size),
                                 spacing1=10, spacing3=10, lmargin1=20, lmargin2=20, rmargin=20)

        for tag in ('code_keyword', 'code_string', 'code_comment', 'code_number',
                    'code_function', 'code_class', 'code_decorator', 'code_operator'):
            self._textbox.tag_config(tag, font=('Consolas', base_size - 1))

        self._textbox.tag_config('blockquote', font=('Segoe UI', base_size, 'italic'),
                                 lmargin1=30, lmargin2=30, spacing1=8, spacing3=8, borderwidth=3)

        # Tag genérica de link (visual); cada link terá também uma tag única para binding)
        self._textbox.tag_config('link', underline=True)
        # Cursor é gerenciado por tag, então não vinculamos aqui ao 'link' genérico

        self._textbox.tag_config('list_item',   lmargin1=25, lmargin2=40)
        self._textbox.tag_config('list_bullet')
        self._textbox.tag_config('list_number', font=('Segoe UI', base_size, 'bold'))

        self._textbox.tag_config('hr', font=('Segoe UI', 4), spacing1=15, spacing3=15, justify='center')

        self._textbox.tag_config('table_border', font=('Consolas', base_size))
        self._textbox.tag_config('table_header', font=('Consolas', base_size, 'bold'))
        self._textbox.tag_config('table_cell',   font=('Consolas', base_size))
        self._textbox.tag_config('table_row_alt', font=('Consolas', base_size))

        self._textbox.tag_config('checkbox_done')
        self._textbox.tag_config('checkbox_pending')

        self._apply_theme()

    def _get_mode(self, mode=None):
        if mode is None:
            mode = ctk.get_appearance_mode()
        return 'dark' if str(mode).lower().startswith('dark') else 'light'

    def _apply_theme(self, mode=None):
        mode = self._get_mode(mode)
        c = self._theme_colors[mode]
        tb = self._textbox

        for level in range(1, 7):
            tb.tag_config(f'h{level}', foreground=c[f'heading_{level}'])

        tb.tag_config('strikethrough', foreground=c['muted'])
        tb.tag_config('code_inline',   foreground=c['code_inline_fg'], background=c['code_inline_bg'])
        tb.tag_config('code_block',    foreground=c['code_block_fg'],  background=c['code_block_bg'])

        for attr in ('code_keyword', 'code_string', 'code_comment', 'code_number',
                     'code_function', 'code_class', 'code_decorator', 'code_operator'):
            tb.tag_config(attr, foreground=c[attr])

        tb.tag_config('blockquote', foreground=c['blockquote_fg'], background=c['blockquote_bg'])
        tb.tag_config('link',       foreground=c['link'])

        tb.tag_config('list_bullet', foreground=c['list_bullet'])
        tb.tag_config('list_number', foreground=c['list_number'])
        tb.tag_config('hr',          foreground=c['hr'])

        tb.tag_config('table_border',   foreground=c['table_border'])
        tb.tag_config('table_header',   background=c['table_header_bg'], foreground=c['table_header_fg'])
        tb.tag_config('table_cell',     background=c['table_cell_bg'],   foreground=c['table_cell_fg'])
        tb.tag_config('table_row_alt',  background=c['table_row_alt_bg'], foreground=c['table_cell_fg'])

        tb.tag_config('checkbox_done',    foreground=c['checkbox_done'])
        tb.tag_config('checkbox_pending', foreground=c['checkbox_pending'])

        # Atualiza todas as tags de link individuais criadas neste render
        for tag in self._link_tags:
            tb.tag_config(tag, foreground=c['link'], underline=True)

    # ──────────────────────────────────────────────
    #  API pública
    # ──────────────────────────────────────────────

    def set_markdown(self, markdown_text: str):
        """Re-renderiza o conteúdo Markdown."""
        self._render_markdown(markdown_text)

    # ──────────────────────────────────────────────
    #  Links e âncoras  ← NOVIDADE
    # ──────────────────────────────────────────────

    def _heading_slug(self, text: str) -> str:
        """
        Converte texto de um heading em um slug de âncora.
        Segue a mesma convenção do GitHub:
        - remove marcação inline
        - lowercase
        - remove caracteres especiais (não-word, não-espaço, não-hífen)
        - cada espaço → hífen individualmente (sem colapsar)

        Exemplo: "Seção A — Formatação"
          → remove '—'  → "seção a  formatação"  (dois espaços)
          → replace ' ' → "seção-a--formatação"   (dois hífens, correto)
        """
        text = re.sub(r'[*_`~#\[\]]', '', text)
        text = text.lower().strip()
        text = re.sub(r'[^\w\s-]', '', text)
        text = text.replace(' ', '-')   # substitui espaço a espaço, sem colapsar
        return text

    def _insert_link(self, text: str, url: str, base_tag: str = None):
        """
        Insere texto de link com uma tag única para binding de evento.
        - URLs externas (http/https): abre no navegador.
        - URLs internas (#ancora): faz scroll para o heading correspondente.
        """
        tag_name = f'_lnk_{self._link_counter}'
        self._link_counter += 1
        self._link_tags.append(tag_name)

        # Estilo visual herdado da tag genérica 'link'
        mode = self._get_mode()
        color = self._theme_colors[mode]['link']
        self._textbox.tag_config(tag_name, foreground=color, underline=True)

        # Bindings de evento
        self._textbox.tag_bind(
            tag_name, '<Button-1>',
            lambda e, u=url: self._handle_link_click(u)
        )
        self._textbox.tag_bind(
            tag_name, '<Enter>',
            lambda e: self.configure(cursor='hand2')
        )
        self._textbox.tag_bind(
            tag_name, '<Leave>',
            lambda e: self.configure(cursor='arrow')
        )

        tags = (tag_name, base_tag) if base_tag else (tag_name,)
        self.insert(tk.END, text, tags)

    def _handle_link_click(self, url: str):
        """Trata clique em link: externo abre navegador, interno faz scroll."""
        if url.startswith('#'):
            slug = url[1:]
            mark = self._anchors.get(slug)

            if not mark:
                # Fallback: tenta normalizar espaços e caixa
                slug_normalized = slug.replace(' ', '-').lower()
                mark = self._anchors.get(slug_normalized)

            if mark:
                try:
                    # Resolve o mark para um índice linha.coluna explícito
                    # antes de chamar see(), evitando ambiguidade no CTkTextbox
                    index = self._textbox.index(mark)
                    self._textbox.see(index)
                    # Força o CTkTextbox a propagar a nova posição de scroll
                    # para seu próprio frame e scrollbar
                    self._textbox.update_idletasks()
                except tk.TclError:
                    pass  # mark não existe mais (render foi resetado)
        else:
            webbrowser.open(url)

    def _register_heading_anchor(self, text: str):
        """
        Registra a posição atual como âncora nomeada para um heading.
        Deve ser chamado ANTES de inserir o texto do heading.

        Usa nomes de mark numéricos (_anc_0, _anc_1, …) para evitar
        problemas com caracteres Unicode em nomes de mark do Tkinter.
        """
        slug = self._heading_slug(text)

        # Garante slug único com sufixo numérico se necessário
        original_slug = slug
        suffix = 1
        while slug in self._anchors:
            slug = f'{original_slug}-{suffix}'
            suffix += 1

        # Nome do mark: índice numérico seguro para o Tkinter
        mark_name = f'_anc_{len(self._anchors)}'

        # Pega o índice exato atual antes da inserção
        current_index = self._textbox.index("end-1c")

        # gravity='left' → o mark não avança quando texto é inserido nessa posição,
        # ficando exatamente no início do heading
        self._textbox.mark_set(mark_name, current_index)
        self._textbox.mark_gravity(mark_name, 'left')

        self._anchors[slug] = mark_name

    # ──────────────────────────────────────────────
    #  Renderização principal
    # ──────────────────────────────────────────────

    def _render_markdown(self, text: str):
        """Processa e renderiza Markdown."""
        # Reinicia estado de links/âncoras a cada render
        self._link_counter = 0
        self._link_tags = []
        self._anchors = {}

        self.configure(state='normal')
        self.delete("0.0", "end")

        lines = text.split('\n')
        i = 0
        in_code_block = False
        code_block_content = []
        code_language = ""

        while i < len(lines):
            line = lines[i]

            # Bloco de código
            if line.strip().startswith('```'):
                if not in_code_block:
                    in_code_block = True
                    code_language = line.strip()[3:].strip().lower()
                    code_block_content = []
                else:
                    in_code_block = False
                    self._insert_code_block('\n'.join(code_block_content), code_language)
                    code_block_content = []
                    code_language = ""
                i += 1
                continue

            if in_code_block:
                code_block_content.append(line)
                i += 1
                continue

            # Linha horizontal
            if re.match(r'^(-{3,}|\*{3,}|_{3,})\s*$', line.strip()):
                self.insert(tk.END, '─' * 60 + '\n', 'hr')
                i += 1
                continue

            # Headings  ← registra âncora antes de inserir
            header_match = re.match(r'^\s*(#{1,6})\s+(.+)$', line)
            if header_match:
                level = len(header_match.group(1))
                content = header_match.group(2)
                self._register_heading_anchor(content)   # ← novo
                self._insert_formatted_text(content, f'h{level}')
                self.insert(tk.END, '\n')
                i += 1
                continue

            # Blockquote
            if line.strip().startswith('>'):
                quote_lines = []
                while i < len(lines) and lines[i].strip().startswith('>'):
                    quote_lines.append(lines[i].strip()[1:].strip())
                    i += 1
                quote_text = ' '.join(quote_lines)
                self.insert(tk.END, '┃ ', 'blockquote')
                self._insert_formatted_text(quote_text + '      ', 'blockquote')
                self.insert(tk.END, '\n\n')
                continue

            # Lista não-ordenada
            list_match = re.match(r'^(\s*)([-*+])\s+(.+)$', line)
            if list_match:
                indent = len(list_match.group(1)) // 2
                content = list_match.group(3)
                checkbox_match = re.match(r'\[([ xX])\]\s*(.+)', content)
                if checkbox_match:
                    checked = checkbox_match.group(1).lower() == 'x'
                    text_content = checkbox_match.group(2)
                    checkbox = '☑' if checked else '☐'
                    tag = 'checkbox_done' if checked else 'checkbox_pending'
                    self.insert(tk.END, '  ' * indent + checkbox + ' ', tag)
                    self._insert_formatted_text(text_content, 'list_item')
                else:
                    self.insert(tk.END, '  ' * indent + '• ', 'list_bullet')
                    self._insert_formatted_text(content, 'list_item')
                self.insert(tk.END, '\n')
                i += 1
                continue

            # Lista ordenada
            ordered_match = re.match(r'^(\s*)(\d+)\.\s+(.+)$', line)
            if ordered_match:
                indent = len(ordered_match.group(1)) // 2
                num = ordered_match.group(2)
                content = ordered_match.group(3)
                self.insert(tk.END, '  ' * indent + f'{num}. ', 'list_number')
                self._insert_formatted_text(content, 'list_item')
                self.insert(tk.END, '\n')
                i += 1
                continue

            # Tabela
            if '|' in line and i + 1 < len(lines) and re.match(r'^[\s|:-]+$', lines[i + 1]):
                table_lines = []
                while i < len(lines) and '|' in lines[i]:
                    table_lines.append(lines[i])
                    i += 1
                self._insert_table(table_lines)
                continue

            # Parágrafo normal
            if line.strip():
                self._insert_formatted_text(line)
                self.insert(tk.END, '\n')
            else:
                self.insert(tk.END, '\n')

            i += 1

        self.configure(state='disabled')

    # ──────────────────────────────────────────────
    #  Formatação inline
    # ──────────────────────────────────────────────

    def _insert_formatted_text(self, text: str, base_tag: str = None):
        """Insere texto com formatação inline (negrito, itálico, links, etc.)."""
        pattern = re.compile(
            r'(?P<bold_italic>\*\*\*(?P<bi_text>.+?)\*\*\*|___(?P<bi_text2>.+?)___)'
            r'|(?P<bold>\*\*(?P<b_text>.+?)\*\*|__(?P<b_text2>.+?)__)'
            r'|(?P<italic>\*(?P<i_text>.+?)\*|_(?P<i_text2>.+?)_)'
            r'|(?P<strike>~~(?P<s_text>.+?)~~)'
            r'|(?P<code>`(?P<c_text>[^`]+)`)'
            r'|(?P<link>\[(?P<l_text>[^\]]+)\]\((?P<l_url>[^)]+)\))'
        )

        last_end = 0
        for match in pattern.finditer(text):
            start, end = match.span()
            if start > last_end:
                plain = text[last_end:start]
                self.insert(tk.END, plain, base_tag) if base_tag else self.insert(tk.END, plain)

            if match.group('bold_italic'):
                content = match.group('bi_text') or match.group('bi_text2')
                tags = ('bold_italic', base_tag) if base_tag else ('bold_italic',)
                self.insert(tk.END, content, tags)
            elif match.group('bold'):
                content = match.group('b_text') or match.group('b_text2')
                tags = ('bold', base_tag) if base_tag else ('bold',)
                self.insert(tk.END, content, tags)
            elif match.group('italic'):
                content = match.group('i_text') or match.group('i_text2')
                tags = ('italic', base_tag) if base_tag else ('italic',)
                self.insert(tk.END, content, tags)
            elif match.group('strike'):
                content = match.group('s_text')
                tags = ('strikethrough', base_tag) if base_tag else ('strikethrough',)
                self.insert(tk.END, content, tags)
            elif match.group('code'):
                content = match.group('c_text')
                tags = ('code_inline', base_tag) if base_tag else ('code_inline',)
                self.insert(tk.END, content, tags)
            elif match.group('link'):
                # ← usa _insert_link em vez de tag genérica
                self._insert_link(
                    match.group('l_text'),
                    match.group('l_url'),
                    base_tag
                )

            last_end = end

        if last_end < len(text):
            remaining = text[last_end:]
            self.insert(tk.END, remaining, base_tag) if base_tag else self.insert(tk.END, remaining)

    # ──────────────────────────────────────────────
    #  Blocos de código com botão copiar  ← NOVIDADE
    # ──────────────────────────────────────────────

    def _insert_code_block(self, code: str, language: str):
        """Insere bloco de código com cabeçalho e botão Copiar."""
        self.insert(tk.END, '\n')

        mode = self._get_mode()
        c = self._theme_colors[mode]

        # Frame que contém label de linguagem + botão copiar
        header_frame = tk.Frame(self, bg=c['code_block_bg'])

        lang_label = tk.Label(
            header_frame,
            text=language.upper() if language else 'CODE',
            font=('Consolas', 9),
            bg=c['code_block_bg'],
            fg=c['code_comment'],
            padx=10, pady=3, anchor='w'
        )
        lang_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        def copy_to_clipboard(code_content=code):
            self.clipboard_clear()
            self.clipboard_append(code_content)
            copy_btn.configure(text='✓ Copiado!', bg=c['copy_btn_active_bg'], fg=c['copy_btn_active_fg'])
            self.after(1500, lambda: copy_btn.configure(
                text='⎘ Copiar', bg=c['copy_btn_bg'], fg=c['copy_btn_fg']
            ))

        copy_btn = tk.Button(
            header_frame,
            text='⎘ Copiar',
            font=('Segoe UI', 9),
            bg=c['copy_btn_bg'],
            fg=c['copy_btn_fg'],
            activebackground=c['copy_btn_active_bg'],
            activeforeground=c['copy_btn_active_fg'],
            relief='flat',
            padx=8, pady=3,
            cursor='hand2',
            command=copy_to_clipboard
        )
        copy_btn.pack(side=tk.RIGHT, padx=6, pady=3)

        self._textbox.window_create(tk.END, window=header_frame)
        self.insert(tk.END, '\n')

        # Destaque sintático
        if language in ('python', 'py'):
            self._highlight_python(code)
        elif language in ('javascript', 'js', 'typescript', 'ts'):
            self._highlight_javascript(code)
        else:
            self.insert(tk.END, code + '\n', 'code_block')

        self.insert(tk.END, '\n')

    # ──────────────────────────────────────────────
    #  Realce sintático
    # ──────────────────────────────────────────────

    def _highlight_python(self, code: str):
        patterns = [
            (r'#.*$', 'code_comment'),
            (r'("""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\')', 'code_string'),
            (r'(["\'])(?:(?!\1|\\).|\\.)*\1', 'code_string'),
            (r'\b(\d+\.?\d*)\b', 'code_number'),
            (r'@\w+', 'code_decorator'),
            (r'\bdef\s+(\w+)', 'code_function'),
            (r'\bclass\s+(\w+)', 'code_class'),
        ]
        for line in code.split('\n'):
            self._highlight_line(line, patterns, self.PYTHON_KEYWORDS)
            self.insert(tk.END, '\n', 'code_block')

    def _highlight_javascript(self, code: str):
        patterns = [
            (r'//.*$', 'code_comment'),
            (r'/\*[\s\S]*?\*/', 'code_comment'),
            (r'(["\'])(?:(?!\1|\\).|\\.)*\1', 'code_string'),
            (r'`[^`]*`', 'code_string'),
            (r'\b(\d+\.?\d*)\b', 'code_number'),
            (r'\bfunction\s+(\w+)', 'code_function'),
            (r'const\s+(\w+)\s*=\s*\([^)]*\)\s*=>', 'code_function'),
        ]
        for line in code.split('\n'):
            self._highlight_line(line, patterns, self.JS_KEYWORDS)
            self.insert(tk.END, '\n', 'code_block')

    def _highlight_line(self, line: str, patterns: list, keywords: set):
        if not line:
            return
        highlights = []
        for pattern, tag in patterns:
            for m in re.finditer(pattern, line, re.MULTILINE):
                highlights.append((m.start(), m.end(), tag))
        for keyword in keywords:
            for m in re.finditer(rf'\b{re.escape(keyword)}\b', line):
                highlights.append((m.start(), m.end(), 'code_keyword'))

        highlights.sort(key=lambda x: (x[0], -x[1]))
        filtered, last_end = [], 0
        for start, end, tag in highlights:
            if start >= last_end:
                filtered.append((start, end, tag))
                last_end = end

        last_pos = 0
        for start, end, tag in filtered:
            if start > last_pos:
                self.insert(tk.END, line[last_pos:start], 'code_block')
            self.insert(tk.END, line[start:end], ('code_block', tag))
            last_pos = end
        if last_pos < len(line):
            self.insert(tk.END, line[last_pos:], 'code_block')

    # ──────────────────────────────────────────────
    #  Tabelas com suporte a tema  ← NOVIDADE
    # ──────────────────────────────────────────────

    def _insert_table(self, table_lines: list):
        """Insere tabela responsiva ao tema claro/escuro."""
        if len(table_lines) < 2:
            return

        header_line = table_lines[0].strip().strip('|')
        headers = [c.strip() for c in header_line.split('|')]

        rows = []
        for line in table_lines[2:]:
            line = line.strip().strip('|')
            cells = [c.strip() for c in line.split('|')]
            if cells and any(c for c in cells):
                rows.append(cells)

        mode = self._get_mode()
        c = self._theme_colors[mode]

        # O bg do frame age como cor de borda entre células
        table_frame = tk.Frame(self, bg=c['table_border'], padx=0, pady=0)

        # Referência para atualização de tema posterior
        all_widgets: list[tuple[tk.Label, str]] = []  # (label, role)

        for col, header in enumerate(headers):
            lbl = tk.Label(
                table_frame, text=header,
                font=('Segoe UI', 10, 'bold'),
                bg=c['table_header_bg'], fg=c['table_header_fg'],
                padx=10, pady=5, relief='flat', anchor='w'
            )
            lbl.grid(row=0, column=col, sticky='nsew', padx=1, pady=1)
            all_widgets.append((lbl, 'header'))

        for row_idx, row in enumerate(rows):
            role = 'alt' if row_idx % 2 == 1 else 'cell'
            for col_idx in range(len(headers)):
                cell_text = row[col_idx] if col_idx < len(row) else ""
                bg = c['table_row_alt_bg'] if role == 'alt' else c['table_cell_bg']
                lbl = tk.Label(
                    table_frame, text=cell_text,
                    font=('Segoe UI', 10),
                    bg=bg, fg=c['table_cell_fg'],
                    padx=10, pady=5, relief='flat', anchor='w'
                )
                lbl.grid(row=row_idx + 1, column=col_idx, sticky='nsew', padx=1, pady=1)
                all_widgets.append((lbl, role))

        for col in range(len(headers)):
            table_frame.columnconfigure(col, weight=1)

        # Registra callback para atualização de tema ← novo
        def update_table_theme(new_mode=None, widgets=all_widgets, frame=table_frame):
            m = self._get_mode(new_mode)
            tc = self._theme_colors[m]
            frame.configure(bg=tc['table_border'])
            for lbl, role in widgets:
                if role == 'header':
                    lbl.configure(bg=tc['table_header_bg'], fg=tc['table_header_fg'])
                elif role == 'alt':
                    lbl.configure(bg=tc['table_row_alt_bg'], fg=tc['table_cell_fg'])
                else:
                    lbl.configure(bg=tc['table_cell_bg'], fg=tc['table_cell_fg'])

        try:
            ctk.AppearanceModeTracker.add(update_table_theme, self)
        except Exception:
            pass

        self.insert(tk.END, '\n')
        self._textbox.window_create(tk.END, window=table_frame)
        self.insert(tk.END, '\n')

    # ──────────────────────────────────────────────
    #  Exemplo de uso
    # ──────────────────────────────────────────────

    def _insert_sample(self):
        sample = '''# Renderizador Markdown para Tkinter

Este é um **componente nativo** para visualizar *Markdown* em tempo real!

---

## Seção A — Formatação

- **Negrito** com `**texto**`
- *Itálico* com `*texto*`
- ~~Riscado~~ com `~~texto~~`
- `Código inline` com crases

## Seção B — Links

### Links externos
Acesse a documentação em [Python.org](https://python.org) e [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter).

### Links internos (navegação)
- Ir para [Seção A](#seção-a--formatação)
- Ir para [Seção B](#seção-b--links)
- Ir para [Blocos de Código](#seção-c--blocos-de-código)
- Ir para [Tabela](#seção-d--tabela)

## Seção C — Blocos de Código

```python
def fibonacci(n):
    """Calcula o n-ésimo número de Fibonacci"""
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

for i in range(10):
    print(f"F({i}) = {fibonacci(i)}")
```

```javascript
const fetchData = async (url) => {
    const response = await fetch(url);
    const data = await response.json();
    console.log("Dados recebidos:", data);
    return data;
};
```

## Seção D — Tabela

| Linguagem  | Tipo     | Popularidade |
|------------|----------|--------------|
| Python     | Dinâmica | ⭐⭐⭐⭐⭐ |
| JavaScript | Dinâmica | ⭐⭐⭐⭐⭐ |
| Rust       | Estática | ⭐⭐⭐⭐   |

---

[Voltar ao início](#renderizador-markdown-para-tkinter)
'''
        self._render_markdown(sample)


# ──────────────────────────────────────────────────────────────
#  Demo standalone
# ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    root.title("CTkMarkdown Demo")
    root.geometry("800x700")

    def toggle_theme():
        mode = ctk.get_appearance_mode()
        ctk.set_appearance_mode("light" if mode == "Dark" else "dark")

    toolbar = ctk.CTkFrame(root, height=40)
    toolbar.pack(fill=tk.X, padx=10, pady=(10, 0))

    ctk.CTkButton(toolbar, text="Alternar Tema", command=toggle_theme, width=140).pack(
        side=tk.LEFT, padx=8, pady=6
    )

    md = CTkMarkdown(root, wrap='word', border_width=0)
    md.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    md._insert_sample()

    root.mainloop()
