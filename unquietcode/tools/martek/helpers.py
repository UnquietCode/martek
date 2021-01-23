import mistletoe

from . import LatexRenderer


def render_markdown(text):
    rendered = mistletoe.markdown(text, LatexRenderer)
    return rendered