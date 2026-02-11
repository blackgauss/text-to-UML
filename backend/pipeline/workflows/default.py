"""Default workflow: route → refine → constrain → generate → validate."""

from .. import Pipeline, register
from ..steps import route, refine, constrain, generate, validate_and_repair

register("default", Pipeline([
    route,
    refine,
    constrain,
    generate,
    validate_and_repair,
]))
