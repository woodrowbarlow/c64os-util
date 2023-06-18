# c64os-util development guide

contributions are welcome. this document serves as a developer guide.

i can usually be reached in the C64 OS discord channel. look for 'voidstar'.

## dependencies

first, install [`git`](https://git-scm.com/) and
[`python`](https://www.python.org/) using the instructions on their websites.

use python to install [`poetry`](https://python-poetry.org/):

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
```

## tests and checks

> note: we use [poe the poet](https://poethepoet.natn.io/) as a taskrunner.
> the examples below invoke `poe` directly -- this assumes you've dropped into
> the poetry environment with `poetry shell`. if not, you'll need to prefix all
> of these like `poetry run poe [...]`.

you can test code style with:

```bash
poe style
```

you can auto-format the code with:

```bash
poe format
```

you can run additional linters with:

```bash
poe lint
```

you can run the test suite with:

```bash
poe test
```

you can run all checks (style, lint, test) all at once with:

```bash
poe check
```

you can generate docs with:

```bash
poe docs
```

the built artifacts are under `docs/_build`.

you can also serve this as a site with live-reloading:

```bash
poe docs-serve
```

and you can perform syntax validation and link-checking with:

```bash
poe docs-check
```

## merge requirements

start at the bottom of this list and work up (design before implementation):

1. everything in `poe check` and `poe docs-check` must run without error.
2. new features should include test cases.
3. new features should include documentation.
4. new APIs should draw inspiration from APIs of similar tools where possible.
