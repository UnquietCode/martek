import shutil
import math
import textwrap
import random
import re

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
\\newcommand{\\cmark}{\\ding{51}}%
\\newcommand{\\xmark}{\\ding{55}}%
\\newcommand{\\done}{\\rlap{$\\square$}{\\raisebox{2pt}{\\large\\hspace{1pt}\\cmark}}%
\\hspace{-2.5pt}}
\\setlength{\\parindent}{0pt}
\n\\begin{document}
\\definecolor{code-background}{gray}{.95}
"""

POSTAMBLE = "\\end{document}"

NEW_LINE = "\\mbox\\\\\n"
INDENT = "\\indent\n"
BLANK_LINE = NEW_LINE + NEW_LINE

UNCHECKED_BOX = "$\square$"
CHECKED_BOX = '\\mbox{\\ooalign{$\\checkmark$\\cr\\hidewidth$\\square$\\hidewidth\\cr}}'

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
        self.render_map['BlockCode'] = self.render_banner
    
    def render_document(self, token):
        rendered = PREAMBLE
        rendered += self.render_inner(token)
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
        rtn = re.sub(r'(\\)',r'\\textbackslash ', rtn)
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
        return f"\colorbox{{code-background}}{{\\texttt{{{self.render_inner(token)}}}}}" + BLANK_LINE


    def render_line_break(self, token):
        return '\n' if token.soft else '\\newline\n'


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
            return f"\n{{\\section*{{{text}}}}}\n"

        elif token.level == 2:
            return f"\n{{\\subsection*{{{underlined(text)}}}}}\n"
        
        elif token.level >= 3:
            return f"\n{{\\subsubsection*{{{text}}}}}\n"
       
        else:
            return f"\n{underlined(self.render_inner(token))}\n"
    
        
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
    
    
    def render_banner(self, token):
        text = self.render_inner(token)
        lines = text.splitlines()
        line = "=" * (max(len(lines[0]), len(lines[-1])) -1)
        
        return f"{line}\n\n{text}\n{line}\n"

    def render_thematic_break(self, token):
        return '\n\\hrulefill\n'
    
    
    def render_paragraph(self, token):
        text = self.render_inner(token)
        return f'{text}\\\\\n'


    def render_quote(self, token):
        return f"\n\\begin{{leftbar}}\n\\begin{{quote}}\n{self.render_inner(token)}\n\\end{{quote}}\n\\end{{leftbar}}\n"
    
    
    def render_list(self, token):
        self.packages['listings'] = []
        template = '\\begin{{{tag}}}\n{inner}\\end{{{tag}}}\n'
        tag = 'enumerate' if token.start is not None else 'itemize'
        inner = '\n'.join([self.render(child) for child in token.children])
        return template.format(tag=tag, inner=inner)

    
    def render_list_item(self, token):
        rendered = ""
        line = self.render_inner(token)
        
        line = line.strip()
        if line:
            print(line[:3])
            if line[:3] == '[x]':
                line = CHECKED_BOX + line[3:]
            elif line[:3] == '[ ]':
                line = UNCHECKED_BOX + line[3:]
            rendered += f"\\item {line} \n"

        return rendered
    
    
    def render_block_code(self, token):
        innards = self.render_inner(token)
        rendered = \
            "\\begin{mdframed}[backgroundcolor=gray!10]\n" \
            "\\begin{lstlisting}\n" \
            f"{innards}\n" \
            "\\end{lstlisting}\n" \
            "\\end{mdframed}"
        
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