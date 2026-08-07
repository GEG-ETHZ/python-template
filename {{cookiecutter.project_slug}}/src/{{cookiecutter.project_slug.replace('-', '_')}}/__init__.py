"""{{ cookiecutter.project_short_description }}"""

from importlib.metadata import version

import {{ cookiecutter.project_slug.replace('-', '_') }}

__version__ = version("{{ cookiecutter.project_slug.replace('-', '_') }}")
