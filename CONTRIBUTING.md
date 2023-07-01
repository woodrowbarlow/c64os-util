# c64os-util development guide

first, install [`git`](https://git-scm.com/) and
[`python`](https://www.python.org/) using the instructions on their websites.

use python to install `poetry`:

```bash
python -m pip install poetry
```

you can test it with:

```bash
poetry --version
# if that fails, try this:
python -m poetry --version
```

then use git to fetch the code:

```bash
git clone git@github.com:woodrowbarlow/c64os-util.git
cd c64os-util
```

now install the project-specific dependencies:

```bash
# the `--with docs` below is optional:
poetry install --with dev --with docs
# optional; runs linters before each commit:
pre-commit install
```
