from markdownrenderer import MarkdownRenderer
import customtkinter as ctk
import tkinter as tk


# ============================================================
# Demo Application
# ============================================================

def main():
    """Main function"""
    root = ctk.CTk()
    root.title("📝 Markdown Editor & Viewer")
    root.geometry("1300x800")
    root.configure(fg_color='#2c3e50')
    
    # Toolbar
    toolbar = ctk.CTkFrame(root, fg_color='#34495e', corner_radius=0)
    toolbar.pack(fill=tk.X)
    
    title = ctk.CTkLabel(toolbar, text="🔮 Markdown Renderer",
                         font=('Segoe UI', 16, 'bold'),
                         text_color='white')
    title.pack(side=tk.LEFT, padx=20, pady=10)
    
    # Buttons
    btn_frame = ctk.CTkFrame(toolbar, fg_color='transparent')
    btn_frame.pack(side=tk.RIGHT, padx=20)
    
    def clear():
        renderer.set_markdown("")
    
    def export_md():
        content = renderer.get("0.0", tk.END)
        root.clipboard_clear()
        root.clipboard_append(content)
    
    ctk.CTkButton(btn_frame, text="🗑️ Limpar", command=clear,
                  font=('Segoe UI', 10), fg_color='#e74c3c',
                  text_color='white', corner_radius=6).pack(side=tk.LEFT, padx=5)
    
    ctk.CTkButton(btn_frame, text="📋 Copiar MD", command=export_md,
                  font=('Segoe UI', 10), fg_color='#27ae60',
                  text_color='white', corner_radius=6).pack(side=tk.LEFT, padx=5)
    
    # Main component
    content_frame = ctk.CTkFrame(root, fg_color='#f5f5f5', corner_radius=8)
    content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    renderer = MarkdownRenderer(content_frame)
    renderer._insert_sample()
    renderer.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    root.mainloop()


if __name__ == "__main__":
    main()
