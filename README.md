# KiCad Library Manager

A command-line tool for managing EasyEDA components in KiCad projects. This tool simplifies the process of downloading, organizing, and maintaining a shared component library that works across multiple KiCad projects.

## Features

- **Global Component Library**: Create a shared library that can be used across all your KiCad projects
- **Easy Component Management**: Download components from EasyEDA with a single command
- **Git-Friendly**: Library structure designed for easy version control
- **Team Collaboration**: Perfect for projects using hierarchical sheets and multiple contributors
- **Diagnostic Tools**: Built-in health checks to ensure your environment is configured correctly
- **Debug Mode**: Toggle verbose logging for troubleshooting

## Requirements

- Python 3.7 or higher
- pip (Python package manager)
- Internet connection (for downloading components)

## Installation

### Step 1: Clone or Download

Download or clone this repository to your local machine:

```bash
git clone <repository-url>
cd rapid-board
```

### Step 2: Run Setup

Run the setup script to automatically configure your environment:

**On Linux/macOS:**
```bash
python3 setup.py
```

**On Windows:**
```bash
python setup.py
```

The setup script will:
1. Check your Python version
2. Create a virtual environment
3. Install all dependencies (including easyeda2kicad)
4. Create a configuration file
5. Set up the component library directory
6. Create CLI wrapper scripts for easy access

### Step 3: Follow the Prompts

During setup, you'll be asked:
- **Library path**: Where to store components (default: `library/`)
- **Debug mode**: Whether to enable verbose logging (default: No)

## Configuration

After setup, a `config.json` file will be created in the project root with your settings:

```json
{
  "library_path": "library",
  "debug_mode": false,
  "easyeda2kicad_path": null
}
```

You can manually edit this file to change settings:
- `library_path`: Relative path from project root where components are stored
- `debug_mode`: Enable (`true`) or disable (`false`) verbose logging
- `easyeda2kicad_path`: Path to easyeda2kicad (usually auto-detected)

## Usage

After setup, you can use the tool with the `kicad-lib` command wrapper.

### Running Commands

**On Linux/macOS:**
```bash
./kicad-lib <command> [options]
```

**On Windows:**
```bash
.\kicad-lib.bat <command> [options]
```

For brevity, the examples below use `kicad-lib`. Adjust for your platform as needed.

### Available Commands

#### Get a Component

Download a component from EasyEDA and add it to your library:

```bash
rb get C12345
```

- `C12345` is an example LCSC part number
- Use `--type` to specify what to download: `symbol`, `footprint`, or `both` (default)

**Examples:**
```bash
rb get C12345                    # Download both symbol and footprint
rb get C12345 --type symbol      # Download only the symbol
rb get C12345 --type footprint   # Download only the footprint
```

#### List Components

Display all components in your library:

```bash
rb list
```

Add `-v` or `--verbose` for detailed information:

```bash
rb list --verbose
```

#### Get Component Info

Show detailed information about a specific component:

```bash
rb info C12345
```

#### Delete a Component

Remove a component from the library:

```bash
rb delete C12345
```

Add `--force` to skip the confirmation prompt:

```bash
rb delete C12345 --force
```

#### Run Diagnostics

Check your system configuration and environment:

```bash
rb diagnostics
```

This will verify:
- Python version
- Virtual environment status
- Configuration file validity
- Library directory accessibility
- easyeda2kicad installation
- Available disk space

Add `-v` for more detailed diagnostic information:

```bash
rb diagnostics --verbose
```

#### Show Help

Display help information:

```bash
rb --help                  # General help
rb get --help              # Help for the 'get' command
rb delete --help           # Help for the 'delete' command
```

#### Enable Debug Mode

Run any command with debug logging:

```bash
rb --debug get C12345
```

Or enable it permanently in `config.json`:

```json
{
  "debug_mode": true
}
```

## Project Structure

```
rapid-board/
├── config.json              # Configuration file (created by setup)
├── setup.py                 # Setup script
├── requirements.txt         # Python dependencies
├── README.md               # This file
├── rb               # CLI wrapper (Unix)
├── rb.bat           # CLI wrapper (Windows)
├── venv/                   # Virtual environment (created by setup)
├── library/                # Component library (created by setup)
│   ├── C12345/            # Example component directory
│   │   ├── symbol.kicad_sym
│   │   ├── footprint.kicad_mod
│   │   └── metadata.json
│   └── C67890/            # Another component
└── src/                    # Source code
    ├── __init__.py
    ├── cli.py              # Command-line interface
    ├── component_manager.py # Component operations
    ├── diagnostics.py      # Health checks
    ├── easyeda_interface.py # EasyEDA2KiCad wrapper
    └── utils.py            # Shared utilities
```

## Using with KiCad Projects

### Setting Up a New Project

1. Create your KiCad project in a separate directory
2. Use the component library manager to download components you need
3. In KiCad, add the library path to your project:
   - Open KiCad
   - Go to Preferences → Manage Symbol Libraries (for symbols)
   - Go to Preferences → Manage Footprint Libraries (for footprints)
   - Add the library directory as a new library path

### Team Collaboration

For team projects:

1. **Store the library in version control**:
   ```bash
   git add library/
   git commit -m "Add component library"
   git push
   ```

2. **Team members can sync**:
   ```bash
   git pull
   ```

3. **Everyone uses the same components**: Since the library path is relative, it works consistently across different systems

### Hierarchical Sheets

The tool supports KiCad's hierarchical sheets naturally:
- All team members have access to the same component library
- Sheets can reference components from the shared library
- Changes to the library are tracked in version control

## Troubleshooting

### "easyeda2kicad not found"

Run diagnostics to check the installation:

```bash
rb diagnostics
```

If easyeda2kicad is missing, try reinstalling:

```bash
./venv/bin/pip install --upgrade easyeda2kicad
```

### Permission Errors

On Unix systems, ensure the CLI wrapper is executable:

```bash
chmod +x rb
```

### Import Errors

Make sure you're running commands from the project root directory and the virtual environment is properly set up. Try running setup again:

```bash
python3 setup.py
```

### Debug Mode

For detailed debugging information, enable debug mode:

```bash
rb --debug <command>
```

Or edit `config.json`:

```json
{
  "debug_mode": true
}
```

## Advanced Usage

### Custom Library Location

Edit `config.json` to change where components are stored:

```json
{
  "library_path": "my_components"
}
```

### Programmatic Access

You can import and use the modules directly in Python:

```python
from src import component_manager, utils

# Setup logging
utils.setup_logging(debug_mode=True)

# Get a component
success, message = component_manager.get_component("C12345")
print(message)

# List components
components = component_manager.list_components()
for comp in components:
    print(comp['id'])
```

## Development

### Running Tests

Currently, tests are not included but can be added in a `tests/` directory.

### Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add appropriate documentation
5. Submit a pull request

### Code Style

The project follows these conventions:
- Descriptive variable and function names
- Docstrings for all functions
- One functionality per file
- Shared utilities in `utils.py`

## Known Limitations

- **Component fetching from projects**: Automatically fetching missing components from KiCad project files is not yet implemented
- **BOM generation**: Bill of Materials export is not yet implemented
- **Search functionality**: Searching EasyEDA's library directly is limited by easyeda2kicad's capabilities

## Future Enhancements

Potential features for future versions:
- Parse KiCad project files to identify and fetch missing components
- Generate and export Bill of Materials (BOM)
- Interactive component search
- Component update checking
- Batch operations
- Web interface

## License

[Add your license here]

## Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check the diagnostics: `rb diagnostics`
- Enable debug mode for more information

## Acknowledgments

This tool wraps and depends on:
- [easyeda2kicad](https://github.com/uPesy/easyeda2kicad) - For converting EasyEDA components to KiCad format
- [KiCad](https://www.kicad.org/) - The amazing open-source PCB design software
- [EasyEDA](https://easyeda.com/) - For providing the component library