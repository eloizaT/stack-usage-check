# Stack usage check

stack-usage-check is a Python package that analyzes stack usage in AUTOSAR software builds by correlating GCC stack-usage files, linker map data, and RTE ARXML mappings, then reports usage against configured memory thresholds.


```sh
stack-usage-check generate --obj-dir build/objects --map-file build/application.map --rte-arxml config/Rte.arxml --output stack_report.json --memory-threshold-limit 0.85
```

Runnable selection and mapping still depend on the existing _Step, Run_, and stack-symbol naming conventions.

## Build the package

### 1. Prepare Python

Use Python 3.9 or newer and a Git checkout of this repository. Python 3.12 was used for build validation:

Create and activate an isolated build environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install build
```

### 2. Build the source archive and wheel

```bash
python -m build
```

The build command installs the backend declared in `pyproject.toml` into an isolated environment, creates a source archive, and builds a wheel from that archive. Outputs are placed in `dist/`:

- `stack_usage_check-<version>.tar.gz`
- `stack_usage_check-<version>-py3-none-any.whl`

### 3. Install and check the wheel

List the outputs, then install the exact wheel you just built, replacing `<version>` with its filename's version:

```bash
ls -lh dist/
python -m pip install --force-reinstall "dist/stack_usage_check-<version>-py3-none-any.whl"
python -m pip check
stack-usage-check --version
stack-usage-check generate --help
python -m stack_usage_check --version
```

Use the exact filename if `dist/` contains multiple builds. Installation also installs the runtime dependencies declared in `pyproject.toml`.

See [the testing guide](TESTING_GUIDE.md) for functional checks using synthetic inputs; those checks run from source and do not replace the wheel installation checks above.


## ToDo

Here is a non-exhaustive list of potential improvements:

- Document input formats and make project naming conventions configurable

## See also

See [the testing guide](TESTING_GUIDE.md) for reproducible CLI checks and known limitations.
