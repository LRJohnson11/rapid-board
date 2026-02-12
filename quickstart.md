# Quick Start Guide

Get up and running with KiCad Library Manager in 3 easy steps:

## 1. Run Setup

```bash
python3 setup.py
```

Follow the prompts to configure your library location and preferences.

## 2. Download a Component

```bash
./rb get C12345
```

Replace `C12345` with any LCSC part number from EasyEDA.

## 3. List Your Components

```bash
./rb list
```

## Common Commands

| Command | Description |
|---------|-------------|
| `./rb get <id>` | Download a component |
| `./rb list` | Show all components |
| `./rb info <id>` | Component details |
| `./rb delete <id>` | Remove a component |
| `./rb diagnostics` | System health check |
| `./rb --help` | Show all commands |

## Need Help?

- Run `./rb diagnostics` to check your setup
- See [README.md](README.md) for detailed documentation
- Enable debug mode: `./rb --debug <command>`

## Windows Users

Use `.\rb.bat` instead of `./rb`:

```bash
python setup.py
.\rb.bat get C12345
```