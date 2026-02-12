# Quick Start Guide

Get up and running with KiCad Library Manager in 3 easy steps:

## 1. Run Setup

```bash
python3 setup.py
```

Follow the prompts to configure your library location and preferences.

## 2. Download a Component

```bash
./kicad-lib get C12345
```

Replace `C12345` with any LCSC part number from EasyEDA.

## 3. List Your Components

```bash
./kicad-lib list
```

## Common Commands

| Command | Description |
|---------|-------------|
| `./kicad-lib get <id>` | Download a component |
| `./kicad-lib list` | Show all components |
| `./kicad-lib info <id>` | Component details |
| `./kicad-lib delete <id>` | Remove a component |
| `./kicad-lib diagnostics` | System health check |
| `./kicad-lib --help` | Show all commands |

## Need Help?

- Run `./kicad-lib diagnostics` to check your setup
- See [README.md](README.md) for detailed documentation
- Enable debug mode: `./kicad-lib --debug <command>`

## Windows Users

Use `.\kicad-lib.bat` instead of `./kicad-lib`:

```bash
python setup.py
.\kicad-lib.bat get C12345
```