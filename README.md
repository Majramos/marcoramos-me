# Marco Ramos Portfolio

<div align="center">

![Python Badge](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=fff&style=flat)
![Gitlab Pipeline Status](https://gitlab.com/majramos/marcoramos-me/badges/main/pipeline.svg)
![Gitlab Release](https://gitlab.com/majramos/marcoramos-me/-/badges/release.svg)
![Gitlab Coverage](https://gitlab.com/majramos/marcoramos-me/badges/main/coverage.svg)

</div>

Source code for [marcoramos.me](https://marcoramos.me), Marco Ramos's personal portfolio site.

The site presents professional projects, career and education history, contact details, and social links.

## Features

- A responsive, single-page portfolio.
- Project cards with external repository links.
- A career and education timeline.
- Desktop and mobile navigation.
- Static site metadata, icons, and search files.

## Stack

- Python 3.13 or later
- [uv](https://docs.astral.sh/uv/) for dependency management
- [Jinja2](https://jinja.palletsprojects.com/) for HTML templates
- HTML, CSS, and JavaScript for the site interface
- JSON files for site content

## Local Setup

Install Python 3.13 or later and `uv`.

Clone the repository and install the dependencies:

```bash
git clone https://gitlab.com/majramos/marcoramos-me.git
cd marcoramos-me
uv sync
```

## Build the Site

Build the static site:

```bash
make build
```

The build writes the generated site to `build/`.

Run the build script directly if `make` is not available:

```bash
uv run python scripts/build.py
```

## Update Content

Update the files below, then run `make build`.

| Path | Content |
| --- | --- |
| `src/data/meta.json` | Site metadata, contact details, and social links |
| `src/data/projects.json` | Portfolio projects |
| `src/data/timeline.json` | Career and education history |
| `src/pages/` | Site pages |
| `src/templates/` | Shared Jinja2 templates |
| `src/static/` | CSS, JavaScript, images, and static site files |

Do not edit files in `build/` by hand. The build replaces this directory.

## Quality Checks

Run all local checks:

```bash
make verify
```

Run each check separately when required:

```bash
make fmt
make lint
make style
make test
```

## Contribute

Read [CONTRIBUTING.md](CONTRIBUTING.md) before you propose a change.

Follow the [Code of Conduct](CODE_OF_CONDUCT.md) in all project communication.

## License

This project uses the [GNU General Public License v3.0](LICENSE).
