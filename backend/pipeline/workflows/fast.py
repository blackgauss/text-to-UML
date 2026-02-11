"""Fast workflow: route → passthrough → constrain → generate → validate (no refine)."""

from .. import Pipeline, register
from ..steps import route, passthrough, constrain, generate, validate_and_repair

register("fast", Pipeline([
    route,
    passthrough,
    constrain,
    generate,
    validate_and_repair,
]))
