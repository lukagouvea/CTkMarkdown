# ctk-markdown

![python](https://img.shields.io/badge/python-3.9%2B-blue)
![customtkinter](https://img.shields.io/badge/customtkinter-required-1f6feb)
![status](https://img.shields.io/badge/status-alpha-orange)
![PyPI - License](https://img.shields.io/badge/license-MIT-blue)

`ctk-markdown` is a **CustomTkinter** Markdown renderer based on `CTkTextbox`. It applies rich tags for headings, lists, tables, code blocks, and inline formatting.

## ✨ Features

- Single widget (`CTkMarkdown`) with Markdown rendering
- Headings, lists, blockquotes, tables, and code blocks
- Basic syntax highlighting for Python and JavaScript
- Clickable external links (opens in default browser)
- Internal anchor navigation (click a link to scroll to a specific section heading)
- Copy button for code blocks
- Theme-aware colors and responsive tables for light and dark appearance modes

## 📦 Installation

```bash
pip install ctk-markdown
```

## 🚀 Usage

```python
from ctk_markdown import CTkMarkdown
import customtkinter as ctk

app = ctk.CTk()
frame = ctk.CTkFrame(app)
frame.pack(fill="both", expand=True, padx=16, pady=16)

renderer = CTkMarkdown(frame)
renderer.pack(fill="both", expand=True)
renderer.set_markdown("""# Title\nText with *italic* and **bold**.""")

app.mainloop()
```

## 🧠 How it works

The widget inherits from `CTkTextbox`. Markdown parsing is done line by line and uses Tkinter text tags for styling. Theme colors are applied based on the current CustomTkinter appearance mode.

## 🧪 Run the demo

```bash
python example.py
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
