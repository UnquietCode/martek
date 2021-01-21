import shutil
import math
import textwrap
import random
import re
from contextlib import contextmanager

from mistletoe.base_renderer import BaseRenderer

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
"""

POSTAMBLE = "\\end{document}"

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


class LatexRenderer(BaseRenderer):

    def __init__(self):
        super().__init__()
        self.packages = {}
        self._indent = -1
        
    @property
    def indent(self):
        return '  ' * self._indent
    
    @contextmanager
    def indentation(self):
        self._indent += 1
        yield
        self._indent -= 1

    def render_document(self, token):
        rendered = PREAMBLE

        inner = self.render_inner(token)
        # inner = re.sub(r'(\S+)\n{2,}(\s*)([^\\{\s])', r'\1\mbox{}\\\\\n\n\2\3', inner, flags=re.MULTILINE)
        
        rendered += inner
        rendered += POSTAMBLE
        return rendered


    def render_to_plain(self, token):
        if hasattr(token, 'children'):
            inner = [self.render_to_plain(child) for child in token.children]
            return ''.join(inner)
        else:
            return token.content
    

    def render_raw_text(self, token):
        rtn = self.render_to_plain(token)
        # rtn = re.sub(r'(\\)([^\n])',r'\\textbackslash\1', rtn)

        rtn = re.sub(r'(\\)', r'\\textbackslash ', rtn)
        rtn = re.sub(r'([\&\%\$\#\_\{\}~\^])',r'\\\1', rtn)
        
        return rtn

        
    # inline styles
    
    def render_strong(self, token):
        return bold(self.render_inner(token))


    def render_emphasis(self, token):
        return italics(self.render_inner(token))


    def render_strikethrough(self, token):
        return strikethrough(self.render_inner(token))


    def render_inline_code(self, token):
        return f"\colorbox{{code-background}}{{\\texttt{{{self.render_inner(token)}}}}}"


    def render_line_break(self, token):
        return '\n' if token.soft else '\\mbox{}\n'


    def render_link(self, token):
        return f'\\href{{{token.target}}}{{{self.render_inner(token)}}}'


    def render_auto_link(self, token):
        return f'\\url{{{token.target}}}'


    def render_image(self, token):
        self.packages['graphicx'] = []
        return '\n\\includegraphics[width=\\textwidth,height=\\textheight,keepaspectratio]{{{}}}\n'.format(token.src)


    def render_heading(self, token):
        text = self.render_inner(token)
        
        if token.level == 1:
            heading = f"{{\\section*{{{text}}}}}"

        elif token.level == 2:
            heading = f"{{\\subsection*{{{underlined(text)}}}}}"
        
        elif token.level >= 3:
            heading = f"{{\\subsubsection*{{{text}}}}}"
       
        else:
            heading = f"{underlined(self.render_inner(token))}"
        
        return f"\n{heading}\n"
        
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
        return '\n\\hrulefill\n'
    
    
    def render_paragraph(self, token):
        return f'\n{self.render_inner(token)}\n'


    def render_quote(self, token):
        return f"\n\\begin{{leftbar}}\n\\begin{{quote}}\n{self.render_inner(token)}\n\\end{{quote}}\n\\end{{leftbar}}\n"
    
    
    def render_list(self, token):
        self.packages['listings'] = []
        tag = 'enumerate' if token.start is not None else 'itemize'
        
        with self.indentation():
            rendered = f"\n{self.indent}\\begin{{{tag}}}"
            
            with self.indentation():
                rendered += f"\n{self.render_inner(token)}"
            
            rendered += f"{self.indent}\\end{{{tag}}}\n"
        
        return rendered
    
    
    def render_list_item(self, token):
        line = self.render_inner(token)
        
        if not line.strip():
            line = '---'  # arbitrary non-empty token that is necessary for latex to not complain about having a list with no elements. Design feedback welcome
        
        line = re.sub(r'^(\s*)\[x]', r'\1\\checkedbox{}', line)
        line = re.sub(r'^(\s*)\[ ]', r'\1\\uncheckedbox{}', line)
        
        rendered = f"{self.indent}\\item {line.strip()}\n"
        return rendered


    def render_block_code(self, token):
        innards = self.render_inner(token)
        rendered = \
            "\\begin{lstlisting}[backgroundcolor = \color{gray!10}]\n" \
            f"{innards}\n" \
            "\\end{lstlisting}\n" \

        return rendered


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
        return template.format(inner=head_rendered+inner, align=align)


    def render_table_row(self, token):
        cells = [self.render(child) for child in token.children]
        return ' & '.join(cells) + ' \\\\\n'

    def render_table_cell(self, token):
        return self.render_inner(token)
