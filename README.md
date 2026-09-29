# Stack usage check

stack-usage-check is a Python package that gathers stack usage data and then generates it into a json report .
The current workflow reads GCC .su files, a map file containing _STACK_Array symbols in the supported column layout, and RTE ARXML timing-event mappings.

The generate command runs this workflow directly; the former -b/--branch option has been removed.

```sh
stack-usage-check generate --obj-dir build/objects --map-file build/application.map --rte-arxml config/Rte.arxml --output stack_report.json --memory-threshold-limit 0.85
```

Runnable selection and mapping still depend on the existing _Step, Run_, and stack-symbol naming conventions. This cleanup does not add support for other input formats.

## Build the package

Run these commands in Bash from the repository root. On Windows, open an Ubuntu WSL terminal first (for example, run `wsl -d Ubuntu-24.04` from PowerShell).

### 1. Prepare Python

Use Python 3.9 or newer and a Git checkout of this repository. Python 3.12 was used for build validation. On Ubuntu 24.04, install Python's virtual-environment support if it is missing:

```bash
sudo apt update
sudo apt install python3-venv
```

Create and activate an isolated build environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install build
```

An internet connection is needed to download build tools and dependencies. Installing the Poetry CLI is not required.

### 2. Build the source archive and wheel

```bash
python -m build
```

The build command installs the backend declared in `pyproject.toml` into an isolated environment, creates a source archive, and builds a wheel from that archive. Outputs are placed in `dist/`:

- `stack_usage_check-<version>.tar.gz`
- `stack_usage_check-<version>-py3-none-any.whl`

The version is derived from Git by `poetry-dynamic-versioning`. Development builds can include a commit identifier and a `.dirty` suffix when the checkout contains changes.

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

After changing source files, rerun `python -m build` and reinstall the resulting wheel to test the updated installed package. See [the testing guide](TESTING_GUIDE.md) for functional checks using synthetic inputs; those checks run from source and do not replace the wheel installation checks above.


## ToDo

Here is a non-exhaustive list of potential improvements:

- Document input formats and make project naming conventions configurable

## See also

See [the testing guide](TESTING_GUIDE.md) for reproducible CLI checks and known limitations.
