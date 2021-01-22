import shutil
import math
import textwrap
import random
import re
from contextlib import contextmanager
from typing import List
from functools import reduce

from mistletoe.base_renderer import BaseRenderer

from .elements import Block, Span, Container

# 'Document':       self.render_document,
# 'Strong':         self.render_strong,
# 'Emphasis':       self.render_emphasis,
# 'Strikethrough':  self.render_strikethrough,
# 'LineBreak':      self.render_line_break,
# 'Quote':          self.render_quote,
# 'Paragraph':      self.render_paragraph,
# 'ThematicBreak':  self.render_thematic_break,
# 'InlineCode':     self.render_inline_code,
# 'CodeFence':      self.render_block_code,
# 'Link':           self.render_link,
# 'List':           self.render_list,
# 'ListItem':       self.render_list_item,
# 'Heading':        self.render_heading,

# 'RawText':        self.render_raw_text,
# 'AutoLink':       self.render_auto_link, ???
# 'EscapeSequence': self.render_escape_sequence,    ???
# 'SetextHeading':  self.render_heading,    ???

# 'Image':          self.render_image, ????
# 'BlockCode':      self.render_block_code,
# 'Table':          self.render_table, ????
# 'TableRow':       self.render_table_row, ????????
# 'TableCell':      self.render_table_cell, ??????????


PREAMBLE = """
\\documentclass{article}
\\usepackage{mdframed}
\\usepackage{hyperref}
\\usepackage{ulem}
\\usepackage{xcolor}
\\usepackage{listings}
\\lstset{
  basicstyle=\\ttfamily,
  columns=fullflexible,
  frame=single,
  breaklines=true,
  postbreak=\\mbox{\\textcolor{red}{$\\hookrightarrow$}\\space},
  backgroundcolor=\colorgray!10
}
\\usepackage{etoolbox}
\\usepackage{fancyvrb}
\\usepackage{xunicode}
\\usepackage[english]{babel}
\\usepackage[T1]{fontenc}

\\usepackage{eurosym}
\\usepackage{textcomp}
\\usepackage{enumitem,amssymb}
\\usepackage{cprotect}
\\usepackage{framed}
\\usepackage{graphicx}

\\usepackage{xltxtra}
\\setmainfont{FreeSerif}
\\setmonofont{FreeMono}

\\graphicspath{ {./images/} }
\\newcommand{\\checkedbox}{\\mbox{\\ooalign{$\\checkmark$\\cr\\hidewidth$\\square$\\hidewidth\\cr}}}
\\newcommand{\\uncheckedbox}{$\\square$}
\\setlength{\\parindent}{0pt}

\\begin{document}
\\definecolor{code-background}{gray}{.95}
"""[1:-1]

POSTAMBLE = "\\end{document}"

BLANK_LINE = "\\mbox{}"
NEW_LINE = "\\mbox\\\\\n"
INDENT = "\\indent\n"

def underlined(text):
    return f"\\underline{{{text}}}"
    
def bold(text):
    return f"\\textbf{{{text}}}"
    
def italics(text):
    return f"\\textit{{{text}}}"

def strikethrough(text):
    return f"\\sout{{{text}}}"

def compose(*functions):
    return reduce(lambda f, g: lambda x: f(g(x)), functions, lambda x: x)


class LatexRenderer(BaseRenderer):

    def __init__(self):
        super().__init__()
        self.packages = {}
        self.stack: List[Container] = [Block()]
        
        old_render = self.render
        
        def render(token):
            result = old_render(token)
            return result or ''
        
        self.render = render


    def push(self, *elements):
        for element in elements:
            self.stack[-1].push(element)
    
    def pop(self):
        return self.stack.pop()
    
    @contextmanager
    def span(self, action=None):
        self.start_span(action=action)
        yield
        self.end_span()
    
    def start_span(self, action=None) -> Span:
        span = Span(action=action)
        self.push(span)
        self.stack.append(span)
        
        return span
    
    
    def end_span(self):
        self.stack.pop()
    
    
    def start_block(self, string: str = None) -> Block:
        block = Block()
        
        if string is not None:
            block.prefix = string
        
        # need to un-nest
        for idx in reversed(range(len(self.stack))):
            element = self.stack[idx]
            
            if type(element) is Block:
                element.push(block)
                break

        self.stack.append(block)
        return block
    
    
    def end_block(self, string: str = None):
        block = self.pop()
        
        if string is not None:
            block.suffix = string

    
    def render_document(self, token):
        self.start_block()
        self.push(PREAMBLE, "\n")
        
        inner = self.render_inner(token)
        #inner = re.sub(r'(\S+)\n{2,}(\s*)([^\\{\s])', r'\1\mbox{}\\\\\n\n\2\3', inner, flags=re.MULTILINE)
        
        self.push(inner)
        self.push(POSTAMBLE)
        self.end_block()

        return self.stack[0].render(indent=-2)


    def render_to_plain(self, token):
        if hasattr(token, 'children'):
            inner = [self.render_to_plain(child) for child in token.children]
            return ''.join(inner)
        else:
            return token.content
    
    
    def render_raw_text(self, token):
        rtn = self.render_to_plain(token)

        rtn = re.sub(r'((?<!\\)[#$%&_{}\\])', r'\\\1', rtn)
        rtn = re.sub(r'((?<!\\)~)', r'\\textasciitilde{}', rtn)
        rtn = re.sub(r'((?<!\\)\^)', r'\\textasciicircum{}', rtn)
        rtn = re.sub(r'(\\\\)', r'\\textbackslash{}', rtn)

        self.push(rtn)
    
    # inline styles
    
    def render_strong(self, token):
        with self.span(bold):
            self.render_inner(token)


    def render_emphasis(self, token):
        with self.span(italics):
            self.render_inner(token)


    def render_strikethrough(self, token):
        with self.span(strikethrough):
            self.render_inner(token)
    

    def render_inline_code(self, token):
        def colorbox(text):
            return f"\\colorbox{{code-background}}{{\\texttt{{{text}}}}}"
        
        with self.span(colorbox):
            self.render_inner(token)


    def render_line_break(self, token):
        print("NEWLINE")
        self.push('' if token.soft else '\\mbox{}\n')
        # self.push(BLANK_LINE)
    

    def render_link(self, token):
        def href(text):
            return f'\\href{{{token.target}}}{{{text}}}'
        
        with self.span(href):
            self.render_inner(token)
    
    
    def render_auto_link(self, token):
        self.push(f'\\url{{{token.target}}}')


    def render_image(self, token):
        self.packages['graphicx'] = []
        self.push(f'\\includegraphics[width=\\textwidth,height=\\textheight,keepaspectratio]{{{token.src}}}', '')


    def render_heading(self, token):
        if token.level == 1:
            heading = lambda text: f"{{\\section*{{{text}}}}}"

        elif token.level == 2:
            heading = lambda text: f"{{\\subsection*{{{underlined(text)}}}}}"
        
        elif token.level >= 3:
            heading = lambda text: f"{{\\subsubsection*{{{text}}}}}"
       
        else:
            heading = lambda text: f"{underlined(text)}"

        with self.span(heading):
            self.render_inner(token)
        
    
    @staticmethod
    def invert_case(text):
        new = []
        
        for x in text:
            if x.isupper():
                new.append(x.lower())
            elif x.islower():
                new.append(x.upper())
            else:
                new.append(x)
        
        return ''.join(new)
    

    def render_thematic_break(self, token):
        self.push('', '\\hrulefill', '')
    
    
    def render_paragraph(self, token):
        # self.push('')
        self.render_inner(token)
        self.push("")


    def render_quote(self, token):
        self.start_block(f"\\begin{{leftbar}}\n\\begin{{quote}}")
        self.render_inner(token)
        self.end_block("\\end{{quote}}\n\\end{{leftbar}}")
    
    
    def render_list(self, token):
        self.packages['listings'] = []
        tag = 'enumerate' if token.start is not None else 'itemize'
        
        self.push('')
        self.start_block(f"\\begin{{{tag}}}")
        self.render_inner(token)
        self.end_block(f"\\end{{{tag}}}")
        self.push('')
    
        
    def render_list_item(self, token):
        
        def coalesce(text):
            if not text.strip():
                return '---'
            else:
                return text
       
        def replace_checkboxes(text):
            text = re.sub(r'^(\s*)\[x]', r'\1\\checkedbox{}', text)
            text = re.sub(r'^(\s*)\[ ]', r'\1\\uncheckedbox{}', text)
            return text
       
        with self.span():
            self.push("\\item ")
            
            with self.span(compose(coalesce, replace_checkboxes)):
                self.render_inner(token)

      
    def render_block_code(self, token):
        self.start_block("\\begin{lstlisting}[backgroundcolor = \\color{gray!10}]")
        self.render_inner(token)
        self.end_block("\\end{lstlisting}\n")


    def render_table(self, token):
        def render_align(column_align):
            if column_align != [None]:
                cols = [get_align(col) for col in token.column_align]
                return '{{{}}}'.format(' '.join(cols))
            else:
                return ''

        def get_align(col):
            if col is None:
                return 'l'
            elif col == 0:
                return 'c'
            elif col == 1:
                return 'r'
            raise RuntimeError('Unrecognized align option: ' + col)

        template = ('\\begin{{tabular}}{align}\n'
                    '{inner}'
                    '\\end{{tabular}}\n')
        if hasattr(token, 'header'):
            head_template = '{inner}\\hline\n'
            head_inner = self.render_table_row(token.header)
            head_rendered = head_template.format(inner=head_inner)
        else: head_rendered = ''
        inner = self.render_inner(token)
        align = render_align(token.column_align)
        self.push(template.format(inner=head_rendered+inner, align=align))


    def render_table_row(self, token):
        cells = [self.render(child) for child in token.children]
        return ' & '.join(cells) + ' \\\\\n'

    def render_table_cell(self, token):
        return self.render_inner(token)
