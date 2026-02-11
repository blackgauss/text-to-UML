"""Default workflow: route → refine → generate → validate."""

from .. import Pipeline, register
from ..steps import route, refine, generate, validate_and_repair

register("default", Pipeline([
    route,
    refine,
    generate,
    validate_and_repair,
]))
