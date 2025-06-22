# 🔐 AKV-TUI — Azure Key Vault Explorer
[![CI](https://github.com/jkoessle/akv-tui/actions/workflows/release.yml/badge.svg?event=push)](https://github.com/jkoessle/akv-tui/actions/workflows/release.yml?query=branch%3Amain)
[![PyPI - Version](https://img.shields.io/pypi/v/akv-tui)](https://pypi.org/project/akv-tui/)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/akv-tui)
[![License](https://img.shields.io/badge/license-MIT-green)](./LICENSE)

**AKV-TUI** is a fast and intuitive terminal-based UI (TUI) for browsing secrets, keys, and certificates in your Azure Key Vaults. Built with [Textual](https://github.com/Textualize/textual), it lets you quickly search, preview, and copy values from your vaults — all from your terminal.

## ✨ Features

- 🔍 Browse secrets, keys, and certificates from any Azure subscription
- 📋 Copy values to clipboard with one click
- 🔐 Authenticate with `az login` or interactive browser login
- ⌨️ Keyboard navigation with intuitive shortcuts

## 🚀 Installation

We recommend using [uv](https://github.com/astral-sh/uv) or [pipx](https://pipx.pypa.io/stable/installation/) for isolated CLI apps.

### Using `pipx`
```bash
pipx install akv-tui
```

### With `uv`:
```bash
uv venv
source .venv/bin/activate
uv pip install .
```

## 🧪 Requirements

- Python 3.10+
- [Azure CLI](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli?view=azure-cli-latest) if you want to use `az login` for authentication
- Clipboard tool:
  - macOS: pbcopy & pbpaste (built-in)
  - Linux: xclip (recommended) or xsel

## 🛠️ Usage

Simply start the app in the terminal of your choice:

```bash
akv-tui
```

Or if you cloned the repository locally:

```bash
python -m akv_tui
```

### Keyboard Shortcuts

| Key             | Action                          |
| --------------- | ------------------------------- |
| `q`             | Quit the application            |
| `d`             | Toggle dark/light theme         |
| `↑`/`↓`         | Navigate list items             |
| `←`/`→`         | Switch between input/list       |
| `Enter`         | Copy selected value             |
| `Tab`           | Navigate widgets clockwise      |
| `Shift` + `Tab` | Navigate widgets anti-clockwise |

## 🧩 How It Works

- Tries to authenticate using DefaultAzureCredential
- Falls back to InteractiveBrowserCredential if needed
- Fetches Key Vaults from all accessible subscriptions
- Loads and filters secrets, keys, or certificates based on selection
- Copies values to clipboard on selection

## 🛡️ Security

This tool does not store credentials or secrets locally. It uses Azure's official authentication flow and only accesses values that your identity has permission to read.

To use this app effectively, make sure your Azure account has at least:
- Reader or Key Vault Reader role on your subscriptions
- Secret Reader, Key Reader, or Certificate Reader permissions on the vault
