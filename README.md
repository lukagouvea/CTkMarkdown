# markdownrenderer

![python](https://img.shields.io/badge/python-3.9%2B-blue)
![customtkinter](https://img.shields.io/badge/customtkinter-required-1f6feb)
![status](https://img.shields.io/badge/status-alpha-orange)

`markdownrenderer` is a **CustomTkinter** Markdown renderer based on `CTkTextbox`. It applies rich tags for headings, lists, tables, code blocks, and inline formatting.

## ✨ Features

- Single widget (`MarkdownRenderer`) with Markdown rendering
- Headings, lists, blockquotes, tables, and code blocks
- Basic syntax highlighting for Python and JavaScript
- Theme-aware colors for light and dark appearance modes

## 📦 Installation

```bash
pip install customtkinter
```

## 🚀 Usage

```python
from markdownrenderer import MarkdownRenderer
import customtkinter as ctk

app = ctk.CTk()
frame = ctk.CTkFrame(app)
frame.pack(fill="both", expand=True, padx=16, pady=16)

renderer = MarkdownRenderer(frame)
renderer.pack(fill="both", expand=True)
renderer.set_markdown("""# Title\nText with *italic* and **bold**.""")

app.mainloop()
```

## 🧠 How it works

The widget inherits from `CTkTextbox`. Markdown parsing is done line by line and uses Tkinter text tags for styling. Theme colors are applied based on the current CustomTkinter appearance mode.

## 🧪 Run the demo

```bash
python test.py
```

## 🤝 Contributing

Contributions are welcome!

1. Fork the repo
2. Create a feature branch (`feature/my-change`)
3. Commit your changes
4. Open a Pull Request with a clear description

Ideas:
- More language grammars for code highlighting
- Image support
- Clickable links

## 📄 License

Choose a license (e.g., MIT) before publishing to GitHub.
