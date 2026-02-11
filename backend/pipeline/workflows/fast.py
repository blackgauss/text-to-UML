"""Fast workflow: route → passthrough → generate → validate (no refine)."""

from .. import Pipeline, register
from ..steps import route, passthrough, generate, validate_and_repair

register("fast", Pipeline([
    route,
    passthrough,
    generate,
    validate_and_repair,
]))
