from MardownRenderer import MarkdownRenderer
import tkinter as tk
import tkinter.ttk as ttk


# ============================================================
# Aplicação de Demonstração
# ============================================================

def main():
    """Função principal"""
    root = tk.Tk()
    root.title("📝 Markdown Editor & Viewer")
    root.geometry("1300x800")
    root.configure(bg='#2c3e50')
    
    # Estilo
    style = ttk.Style()
    style.theme_use('clam')
    style.configure('TFrame', background='#f5f5f5')
    style.configure('TPanedwindow', background='#2c3e50')
    
    # Toolbar
    toolbar = tk.Frame(root, bg='#34495e', pady=10)
    toolbar.pack(fill=tk.X)
    
    title = tk.Label(toolbar, text="🔮 Markdown Renderer", 
                    font=('Segoe UI', 16, 'bold'),
                    fg='white', bg='#34495e')
    title.pack(side=tk.LEFT, padx=20)
    
    # Botões
    btn_frame = tk.Frame(toolbar, bg='#34495e')
    btn_frame.pack(side=tk.RIGHT, padx=20)
    
    def clear():
        renderer.editor.delete("1.0", tk.END)
        renderer.render()
    
    def export_md():
        content = renderer.editor.get("1.0", tk.END)
        root.clipboard_clear()
        root.clipboard_append(content)
    
    tk.Button(btn_frame, text="🗑️ Limpar", command=clear,
             font=('Segoe UI', 10), bg='#e74c3c', fg='white',
             relief='flat', padx=15, pady=5).pack(side=tk.LEFT, padx=5)
    
    tk.Button(btn_frame, text="📋 Copiar MD", command=export_md,
             font=('Segoe UI', 10), bg='#27ae60', fg='white',
             relief='flat', padx=15, pady=5).pack(side=tk.LEFT, padx=5)
    
    # Componente principal
    renderer = MarkdownRenderer(root, show_editor=False)
    renderer.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    root.mainloop()


if __name__ == "__main__":
    main()
