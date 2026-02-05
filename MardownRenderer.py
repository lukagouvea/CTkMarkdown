"""
Componente Tkinter para Renderização de Markdown
Usa tk.Text com tags customizadas para melhor controle e renderização
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import re


class MarkdownText(tk.Text):
    """Widget Text com suporte nativo a Markdown"""
    
    def __init__(self, master, **kwargs):
        # Configurações padrão
        defaults = {
            'wrap': tk.WORD,
            'padx': 15,
            'pady': 15,
            'bg': '#ffffff',
            'fg': '#333333',
            'font': ('Segoe UI', 11),
            'spacing1': 2,
            'spacing2': 2,
            'spacing3': 5,
            'state': 'disabled',
            'cursor': 'arrow',
            'relief': 'flat',
            'borderwidth': 0,
        }
        defaults.update(kwargs)
        super().__init__(master, **defaults)
        
        self._setup_tags()
    
    def _setup_tags(self):
        """Configura as tags de formatação"""
        # Fontes
        base_size = 11
        
        # Cabeçalhos
        self.tag_configure('h1', font=('Segoe UI', base_size + 12, 'bold'), 
                          foreground='#1a1a2e', spacing1=20, spacing3=10)
        self.tag_configure('h2', font=('Segoe UI', base_size + 8, 'bold'), 
                          foreground='#16213e', spacing1=18, spacing3=8)
        self.tag_configure('h3', font=('Segoe UI', base_size + 5, 'bold'), 
                          foreground='#1f4068', spacing1=15, spacing3=6)
        self.tag_configure('h4', font=('Segoe UI', base_size + 3, 'bold'), 
                          foreground='#1b1b2f', spacing1=12, spacing3=5)
        self.tag_configure('h5', font=('Segoe UI', base_size + 2, 'bold'), 
                          foreground='#464866', spacing1=10, spacing3=4)
        self.tag_configure('h6', font=('Segoe UI', base_size + 1, 'bold'), 
                          foreground='#6b778d', spacing1=8, spacing3=3)
        
        # Formatação de texto
        self.tag_configure('bold', font=('Segoe UI', base_size, 'bold'))
        self.tag_configure('italic', font=('Segoe UI', base_size, 'italic'))
        self.tag_configure('bold_italic', font=('Segoe UI', base_size, 'bold italic'))
        self.tag_configure('strikethrough', overstrike=True, foreground='#888888')
        self.tag_configure('underline', underline=True)
        
        # Código inline
        self.tag_configure('code_inline', 
                          font=('Consolas', base_size), 
                          background='#f0f0f0',
                          foreground='#d63384',
                          spacing1=2)
        
        # Bloco de código
        self.tag_configure('code_block', 
                          font=('Consolas', base_size - 1),
                          background='#1e1e1e',
                          foreground='#d4d4d4',
                          spacing1=10,
                          spacing3=10,
                          lmargin1=20,
                          lmargin2=20,
                          rmargin=20)
        
        # Syntax highlighting para código
        self.tag_configure('code_keyword', foreground='#569cd6', font=('Consolas', base_size - 1))
        self.tag_configure('code_string', foreground='#ce9178', font=('Consolas', base_size - 1))
        self.tag_configure('code_comment', foreground='#6a9955', font=('Consolas', base_size - 1))
        self.tag_configure('code_number', foreground='#b5cea8', font=('Consolas', base_size - 1))
        self.tag_configure('code_function', foreground='#dcdcaa', font=('Consolas', base_size - 1))
        self.tag_configure('code_class', foreground='#4ec9b0', font=('Consolas', base_size - 1))
        self.tag_configure('code_decorator', foreground='#c586c0', font=('Consolas', base_size - 1))
        self.tag_configure('code_operator', foreground='#d4d4d4', font=('Consolas', base_size - 1))
        
        # Citação
        self.tag_configure('blockquote', 
                          font=('Segoe UI', base_size, 'italic'),
                          foreground='#6c757d',
                          background='#f8f9fa',
                          lmargin1=30,
                          lmargin2=30,
                          spacing1=8,
                          spacing3=8,
                          borderwidth=3)
        
        # Links
        self.tag_configure('link', foreground='#0d6efd', underline=True)
        self.tag_bind('link', '<Enter>', lambda e: self.config(cursor='hand2'))
        self.tag_bind('link', '<Leave>', lambda e: self.config(cursor='arrow'))
        
        # Listas
        self.tag_configure('list_item', lmargin1=25, lmargin2=40)
        self.tag_configure('list_bullet', foreground='#6c757d')
        self.tag_configure('list_number', foreground='#0d6efd', font=('Segoe UI', base_size, 'bold'))
        
        # Linha horizontal
        self.tag_configure('hr', font=('Segoe UI', 4), foreground='#dee2e6', 
                          spacing1=15, spacing3=15, justify='center')
        
        # Tabela
        self.tag_configure('table_border', font=('Consolas', base_size),
                          foreground='#6c757d')
        self.tag_configure('table_header', font=('Consolas', base_size, 'bold'),
                          background='#e9ecef', foreground='#212529')
        self.tag_configure('table_cell', font=('Consolas', base_size),
                          background='#ffffff')
        self.tag_configure('table_row_alt', font=('Consolas', base_size),
                          background='#f8f9fa')
        
        # Checkbox
        self.tag_configure('checkbox_done', foreground='#198754')
        self.tag_configure('checkbox_pending', foreground='#dc3545')


class MarkdownRenderer(tk.Frame):
    """Componente completo para edição e visualização de Markdown"""
    
    # Palavras-chave para syntax highlighting
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
    
    def __init__(self, master, show_editor=True, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(bg='#f5f5f5')
        self.show_editor = show_editor
        self._setup_ui()
    
    def _setup_ui(self):
        """Configura a interface"""
        if self.show_editor:
            # PanedWindow para divisão editor/preview
            self.paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
            self.paned.pack(fill=tk.BOTH, expand=True)
            
            # Frame do Editor
            editor_frame = ttk.Frame(self.paned)
            self.paned.add(editor_frame, weight=1)
            
            # Label do editor
            editor_label = tk.Label(editor_frame, text="📝 Editor Markdown", 
                                   font=('Segoe UI', 10, 'bold'),
                                   bg='#2d2d2d', fg='white', pady=8)
            editor_label.pack(fill=tk.X)
            
            # Editor de texto
            self.editor = scrolledtext.ScrolledText(
                editor_frame,
                wrap=tk.WORD,
                font=('Consolas', 11),
                bg='#1e1e1e',
                fg='#d4d4d4',
                insertbackground='#ffffff',
                selectbackground='#264f78',
                padx=15,
                pady=15,
                undo=True,
                relief='flat'
            )
            self.editor.pack(fill=tk.BOTH, expand=True)
            
            # Frame do Preview
            preview_frame = ttk.Frame(self.paned)
            self.paned.add(preview_frame, weight=1)
            
            # Label do preview
            preview_label = tk.Label(preview_frame, text="👁️ Preview", 
                                    font=('Segoe UI', 10, 'bold'),
                                    bg='#0d6efd', fg='white', pady=8)
            preview_label.pack(fill=tk.X)
            
            # Preview com scroll
            preview_container = tk.Frame(preview_frame)
            preview_container.pack(fill=tk.BOTH, expand=True)
            
            scrollbar = ttk.Scrollbar(preview_container)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            self.preview = MarkdownText(preview_container, yscrollcommand=scrollbar.set)
            self.preview.pack(fill=tk.BOTH, expand=True)
            scrollbar.config(command=self.preview.yview)
            
            # Bindings
            self.editor.bind('<KeyRelease>', lambda e: self.after(100, self.render))
            
            # Inserir exemplo
            self._insert_sample()
        else:
            # Somente preview
            scrollbar = ttk.Scrollbar(self)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            self.preview = MarkdownText(self, yscrollcommand=scrollbar.set)
            self.preview.pack(fill=tk.BOTH, expand=True)
            scrollbar.config(command=self.preview.yview)
            self._insert_sample()
    
    def render(self):
        """Renderiza o Markdown"""
        if self.show_editor:
            text = self.editor.get("1.0", tk.END)
        else:
            return
        
        self._render_markdown(text)
    
    def set_markdown(self, text: str):
        """Define o texto Markdown"""
        if self.show_editor:
            self.editor.delete("1.0", tk.END)
            self.editor.insert("1.0", text)
        self._render_markdown(text)
    
    def _render_markdown(self, text: str):
        """Processa e renderiza o Markdown"""
        self.preview.config(state='normal')
        self.preview.delete("1.0", tk.END)
        
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
                self.preview.insert(tk.END, '─' * 60 + '\n', 'hr')
                i += 1
                continue
            
            # Cabeçalhos
            header_match = re.match(r'^(#{1,6})\s+(.+)$', line)
            if header_match:
                level = len(header_match.group(1))
                content = header_match.group(2)
                self._insert_formatted_text(content, f'h{level}')
                self.preview.insert(tk.END, '\n')
                i += 1
                continue
            
            # Citação
            if line.strip().startswith('>'):
                quote_lines = []
                while i < len(lines) and lines[i].strip().startswith('>'):
                    quote_lines.append(lines[i].strip()[1:].strip())
                    i += 1
                quote_text = ' '.join(quote_lines)
                self.preview.insert(tk.END, '┃ ', 'blockquote')
                self._insert_formatted_text(quote_text, 'blockquote')
                self.preview.insert(tk.END, '\n\n')
                continue
            
            # Lista não ordenada
            list_match = re.match(r'^(\s*)([-*+])\s+(.+)$', line)
            if list_match:
                indent = len(list_match.group(1)) // 2
                content = list_match.group(3)
                
                # Checkbox
                checkbox_match = re.match(r'\[([ xX])\]\s*(.+)', content)
                if checkbox_match:
                    checked = checkbox_match.group(1).lower() == 'x'
                    text_content = checkbox_match.group(2)
                    checkbox = '☑' if checked else '☐'
                    tag = 'checkbox_done' if checked else 'checkbox_pending'
                    self.preview.insert(tk.END, '  ' * indent + checkbox + ' ', tag)
                    self._insert_formatted_text(text_content, 'list_item')
                else:
                    self.preview.insert(tk.END, '  ' * indent + '• ', 'list_bullet')
                    self._insert_formatted_text(content, 'list_item')
                
                self.preview.insert(tk.END, '\n')
                i += 1
                continue
            
            # Lista ordenada
            ordered_match = re.match(r'^(\s*)(\d+)\.\s+(.+)$', line)
            if ordered_match:
                indent = len(ordered_match.group(1)) // 2
                num = ordered_match.group(2)
                content = ordered_match.group(3)
                self.preview.insert(tk.END, '  ' * indent + f'{num}. ', 'list_number')
                self._insert_formatted_text(content, 'list_item')
                self.preview.insert(tk.END, '\n')
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
                self.preview.insert(tk.END, '\n')
            else:
                self.preview.insert(tk.END, '\n')
            
            i += 1
        
        self.preview.config(state='disabled')
    
    def _insert_formatted_text(self, text: str, base_tag: str = None):
        """Insere texto com formatação inline"""
        # Padrões de formatação
        patterns = [
            (r'\*\*\*(.+?)\*\*\*', 'bold_italic'),      # ***texto***
            (r'___(.+?)___', 'bold_italic'),            # ___texto___
            (r'\*\*(.+?)\*\*', 'bold'),                 # **texto**
            (r'__(.+?)__', 'bold'),                     # __texto__
            (r'\*(.+?)\*', 'italic'),                   # *texto*
            (r'_(.+?)_', 'italic'),                     # _texto_
            (r'~~(.+?)~~', 'strikethrough'),            # ~~texto~~
            (r'`([^`]+)`', 'code_inline'),              # `código`
            (r'\[([^\]]+)\]\(([^)]+)\)', 'link'),       # [texto](url)
        ]
        
        # Encontrar todas as formatações
        segments = []
        last_end = 0
        
        # Combinar todos os padrões e ordenar por posição
        all_matches = []
        for pattern, tag in patterns:
            for match in re.finditer(pattern, text):
                all_matches.append((match.start(), match.end(), match, tag))
        
        all_matches.sort(key=lambda x: x[0])
        
        # Remover sobreposições
        filtered_matches = []
        last_match_end = 0
        for start, end, match, tag in all_matches:
            if start >= last_match_end:
                filtered_matches.append((start, end, match, tag))
                last_match_end = end
        
        # Processar segmentos
        last_end = 0
        for start, end, match, tag in filtered_matches:
            # Texto antes da formatação
            if start > last_end:
                plain_text = text[last_end:start]
                if base_tag:
                    self.preview.insert(tk.END, plain_text, base_tag)
                else:
                    self.preview.insert(tk.END, plain_text)
            
            # Texto formatado
            if tag == 'link':
                link_text = match.group(1)
                # link_url = match.group(2)  # Pode ser usado para abrir links
                tags = ('link', base_tag) if base_tag else ('link',)
                self.preview.insert(tk.END, link_text, tags)
            else:
                content = match.group(1)
                tags = (tag, base_tag) if base_tag else (tag,)
                self.preview.insert(tk.END, content, tags)
            
            last_end = end
        
        # Texto restante
        if last_end < len(text):
            remaining = text[last_end:]
            if base_tag:
                self.preview.insert(tk.END, remaining, base_tag)
            else:
                self.preview.insert(tk.END, remaining)
    
    def _insert_code_block(self, code: str, language: str):
        """Insere bloco de código com syntax highlighting"""
        self.preview.insert(tk.END, '\n')
        
        # Cabeçalho do bloco de código
        if language:
            lang_display = language.upper()
            self.preview.insert(tk.END, f' {lang_display} \n', 'code_block')
        
        # Aplicar syntax highlighting
        if language in ('python', 'py'):
            self._highlight_python(code)
        elif language in ('javascript', 'js', 'typescript', 'ts'):
            self._highlight_javascript(code)
        else:
            self.preview.insert(tk.END, code + '\n', 'code_block')
        
        self.preview.insert(tk.END, '\n')
    
    def _highlight_python(self, code: str):
        """Syntax highlighting para Python"""
        # Padrões para Python
        patterns = [
            (r'#.*$', 'code_comment'),                           # Comentários
            (r'("""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\')', 'code_string'),  # Docstrings
            (r'(["\'])(?:(?!\1|\\).|\\.)*\1', 'code_string'),    # Strings
            (r'\b(\d+\.?\d*)\b', 'code_number'),                 # Números
            (r'@\w+', 'code_decorator'),                          # Decoradores
            (r'\bdef\s+(\w+)', 'code_function'),                 # Funções
            (r'\bclass\s+(\w+)', 'code_class'),                  # Classes
        ]
        
        lines = code.split('\n')
        for line in lines:
            self._highlight_line(line, patterns, self.PYTHON_KEYWORDS)
            self.preview.insert(tk.END, '\n', 'code_block')
    
    def _highlight_javascript(self, code: str):
        """Syntax highlighting para JavaScript"""
        patterns = [
            (r'//.*$', 'code_comment'),                          # Comentários linha
            (r'/\*[\s\S]*?\*/', 'code_comment'),                 # Comentários bloco
            (r'(["\'])(?:(?!\1|\\).|\\.)*\1', 'code_string'),   # Strings
            (r'`[^`]*`', 'code_string'),                         # Template literals
            (r'\b(\d+\.?\d*)\b', 'code_number'),                 # Números
            (r'\bfunction\s+(\w+)', 'code_function'),            # Funções
            (r'const\s+(\w+)\s*=\s*\([^)]*\)\s*=>', 'code_function'),  # Arrow functions
        ]
        
        lines = code.split('\n')
        for line in lines:
            self._highlight_line(line, patterns, self.JS_KEYWORDS)
            self.preview.insert(tk.END, '\n', 'code_block')
    
    def _highlight_line(self, line: str, patterns: list, keywords: set):
        """Aplica highlighting a uma linha"""
        if not line:
            return
        
        # Encontrar todas as correspondências
        highlights = []  # (start, end, tag)
        
        for pattern, tag in patterns:
            for match in re.finditer(pattern, line, re.MULTILINE):
                highlights.append((match.start(), match.end(), tag))
        
        # Adicionar palavras-chave
        for keyword in keywords:
            pattern = rf'\b{re.escape(keyword)}\b'
            for match in re.finditer(pattern, line):
                highlights.append((match.start(), match.end(), 'code_keyword'))
        
        # Ordenar e remover sobreposições
        highlights.sort(key=lambda x: (x[0], -x[1]))
        filtered = []
        last_end = 0
        for start, end, tag in highlights:
            if start >= last_end:
                filtered.append((start, end, tag))
                last_end = end
        
        # Inserir texto com highlighting
        last_pos = 0
        for start, end, tag in filtered:
            if start > last_pos:
                self.preview.insert(tk.END, line[last_pos:start], 'code_block')
            self.preview.insert(tk.END, line[start:end], ('code_block', tag))
            last_pos = end
        
        if last_pos < len(line):
            self.preview.insert(tk.END, line[last_pos:], 'code_block')
    
    def _insert_table(self, table_lines: list):
        """Insere uma tabela usando um widget real (Frame + Grid) para alinhamento perfeito"""
        if len(table_lines) < 2:
            return
        
        # Parse headers
        header_line = table_lines[0].strip()
        if header_line.startswith('|'): header_line = header_line[1:]
        if header_line.endswith('|'): header_line = header_line[:-1]
        headers = [cell.strip() for cell in header_line.split('|')]
        
        # Parse rows
        rows = []
        for line in table_lines[2:]:
            line = line.strip()
            if line.startswith('|'): line = line[1:]
            if line.endswith('|'): line = line[:-1]
            cells = [cell.strip() for cell in line.split('|')]
            if cells and any(c for c in cells):
                rows.append(cells)

        # Criar um container para a tabela
        # O bg aqui define a cor da "borda" entre as células
        table_frame = tk.Frame(self.preview, bg='#bdc3c7', padx=0, pady=0)
        
        # Adicionar cabeçalhos
        for col, header in enumerate(headers):
            lbl = tk.Label(table_frame, text=header, font=('Segoe UI', 10, 'bold'),
                          bg='#e9ecef', fg='#212529', padx=10, pady=5, 
                          relief='flat', anchor='w')
            lbl.grid(row=0, column=col, sticky='nsew', padx=1, pady=1)
            
        # Adicionar linhas de dados
        for row_idx, row in enumerate(rows):
            for col_idx in range(len(headers)):
                cell_text = row[col_idx] if col_idx < len(row) else ""
                bg_color = '#f8f9fa' if row_idx % 2 == 1 else '#ffffff'
                lbl = tk.Label(table_frame, text=cell_text, font=('Segoe UI', 10),
                              bg=bg_color, fg='#333333', padx=10, pady=5,
                              relief='flat', anchor='w')
                lbl.grid(row=row_idx + 1, column=col_idx, sticky='nsew', padx=1, pady=1)

        # Forçar colunas a terem peso para distribuir espaço se necessário
        for col in range(len(headers)):
            table_frame.columnconfigure(col, weight=1)

        # Inserir o widget da tabela dentro do Text
        self.preview.insert(tk.END, '\n')
        self.preview.window_create(tk.END, window=table_frame)
        self.preview.insert(tk.END, '\n')
    
    def _insert_sample(self):
        """Insere texto de exemplo"""
        sample = '''# 🎉 Renderizador Markdown para Tkinter

Este é um **componente nativo** para visualizar *Markdown* em tempo real!

## ✨ Formatação de Texto

- **Texto em negrito** usando `**texto**`
- *Texto em itálico* usando `*texto*`
- ***Negrito e itálico*** usando `***texto***`
- ~~Texto riscado~~ usando `~~texto~~`
- `Código inline` usando crases

## 📝 Listas

### Lista não ordenada:
- Item principal
  - Sub-item
  - Outro sub-item
- Segundo item
- Terceiro item

### Lista ordenada:
1. Primeiro passo
2. Segundo passo
3. Terceiro passo

### Checkboxes:
- [x] Tarefa concluída
- [ ] Tarefa pendente
- [x] Outra tarefa feita

## 💬 Citações

> "A simplicidade é a sofisticação máxima."
> — Leonardo da Vinci

## 💻 Blocos de Código

### Python:
```python
def fibonacci(n):
    """Calcula o n-ésimo número de Fibonacci"""
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# Exemplo de uso
for i in range(10):
    print(f"F({i}) = {fibonacci(i)}")
```

### JavaScript:
```javascript
// Função assíncrona moderna
const fetchData = async (url) => {
    const response = await fetch(url);
    const data = await response.json();
    console.log("Dados recebidos:", data);
    return data;
};

fetchData("https://api.exemplo.com/dados");
```

## 📊 Tabelas

| Linguagem | Tipo | Popularidade |
|-----------|------|--------------|
| Python | Dinâmica | ⭐⭐⭐⭐⭐ |
| JavaScript | Dinâmica | ⭐⭐⭐⭐⭐ |
| Rust | Estática | ⭐⭐⭐⭐ |
| Go | Estática | ⭐⭐⭐⭐ |

---

## 🔗 Links

Visite o [Python.org](https://python.org) para mais informações!

---

**Divirta-se escrevendo em Markdown!** 🚀
'''
        self.set_markdown(sample)
        self.render()