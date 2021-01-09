import shutil
import math
import textwrap
import random
import re

from mistletoe.base_renderer import BaseRenderer

# https://github.com/miyuchina/mistletoe/blob/master/mistletoe/base_renderer.py

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

# class bracketed_span(SpanToken):
#   pattern = re.compile(r'\[(.*?)\]\{(.*?)\}')
#   parse_inner = False
#   parse_group = 0
#   def __init__(self, match):
#       self.text = EscapeSequence.strip(match.group(1).strip())
#       self.meta = EscapeSequence.strip(match.group(2))

# PREAMBLE = ""

PREAMBLE = """
\\documentclass{article}
\\usepackage{mdframed}
\\usepackage{hyperref}
\\usepackage{ulem}
\\usepackage{xcolor}
\\usepackage{listings}
\\usepackage{etoolbox}
\\usepackage{fancyvrb}
\\usepackage{enumitem,amssymb}
\\usepackage{cprotect}
\\usepackage{pifont}
\\newcommand{\\cmark}{\\ding{51}}%
\\newcommand{\\xmark}{\\ding{55}}%
\\newcommand{\\done}{\\rlap{$\\square$}{\\raisebox{2pt}{\\large\\hspace{1pt}\\cmark}}%
\\hspace{-2.5pt}}
\\setlength{\\parindent}{0pt}
\n\\begin{document}
\\newcommand*{\\headerType}{\\subsection}
\\newcommand*{\\codeFont}{\\fontfamily{otf}\\selectfont}
\\newcommand*{\\hAFont}{\\Huge{\\fontfamily{otf}\\selectfont}}
\\newcommand*{\\hBFont}{\\huge{\\fontfamily{otf}\\selectfont}}
\\newcommand*{\\hCFont}{\\LARGE{\\fontfamily{otf}\\selectfont}}
\\newcommand*{\\hDFont}{\\Large{\\fontfamily{otf}\\selectfont}}
\\newcommand*{\\hEFont}{\\large{\\fontfamily{otf}\\selectfont}}
\\newcommand*{\\hFFont}{\\centerline{\\normalsize{\\fontfamily{otf}\\selectfont}}}
""" 

#\\newcommand{\\wontfix}{\\rlap{$\\square$}{\\large\\hspace{1pt}\\xmark}}\\square$}{\\raisebox{2pt}{\\large\\hspace{1pt}\\cmark}}%

#
#""" #\\AtBeginEnvironment{quote}{\\singlespacing\\small}

POSTAMBLE = "\\end{document}"

TRAILING_WHITESPACE = ""

BLANK_LINE = " \n \\vspace{\\baselineskip} \n " #this isn't an f string so we only need single {}

UNCHECKED_BOX = "$\square$"
CHECKED_BOX = '\\mbox{\\ooalign{$\\checkmark$\\cr\\hidewidth$\\square$\\hidewidth\\cr}}'

def prefixed(prefix):
    
    def outer(fn):
        
        # wraps.
        def decorated(*args, **kwargs):
            result = fn(*args, **kwargs)
            return prefix + result
            
        return decorated
    
    return outer


def sufixed(suffix):
    
    def outer(fn):
        
        # wraps.
        def decorated(*args, **kwargs):
            result = fn(*args, **kwargs)
            return result + suffix
            
        return decorated
    
    return outer

def underlined(text):
    return f"\\underline{{{text}}}"
    
def bold(text):
    return f"\\textbf{{{text}}}"
    
def italics(text):
     return f"\\textit{{{text}}}"

def strikethrough(text):
    return f"\\sout{{{text}}}"

def _(input):
  # input = '\n'.join([_.lstrip() for _ in input.splitlines()])
  # return input.strip()
  return textwrap.dedent(input).strip()


class LatexRenderer(BaseRenderer):

    def __init__(self):
        super().__init__()
        #tokens = self._tokens_from_module(latex_token)
        self.packages = {}
        #super().__init__(*chain(tokens, extras))
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
        #print(f"it's {token.content}")
        rtn = self.render_to_plain(token)
        rtn = re.sub(r'(\\)',r'\\textbackslash ', rtn)
        rtn = re.sub(r'([\&\%\$\#\_\{\}~\^])',r'\\\1', rtn)
        
        # rtn = re.sub('–','--', rtn)
        # rtn = re.sub('—','---', rtn)
        return rtn

        #return '\\begin{verbatim}\n' + self.render_to_plain(token) + '\n\\end{verbatim}\n'     
        #return '\\verb!' + self.render_to_plain(token) + '!\n'         #https://www.overleaf.com/learn/latex/Errors/LaTeX_Error:_%5Cverb_ended_by_end_of_line
   
        
    # inline styles
    
    def render_strong(self, token):
        return bold(self.render_inner(token))


    def render_emphasis(self, token):
        return italics(self.render_inner(token))


    def render_strikethrough(self, token):
        return strikethrough(self.render_inner(token))

        # this doesn't seem to work as well

        # rendered = ''
        # 
        # for c in self.render_inner(token):
        #     rendered += f"{c}\u0336"
        # 
        # return rendered
    
    def render_inline_code(self, token):
        return f"\colorbox{{lightgray}}{{ \\codeFont \\texttt{{{self.render_inner(token)}}} }} " + BLANK_LINE
    
    def render_block_code(self, token):
        return _(f"""\\begin{{lstlisting}}
                    {{\codeFont {self.render_inner(token)} }}
                    \\end{{lstlisting}}""")


    def render_line_break(self, token):
        return '\n' if token.soft else '\\newline\n'

    def render_link(self, token):
      return f"\\href{{{token.target}}}{{{underlined(self.render_inner(token))}}}"

    # @prefixed('\n')
    @sufixed('\n') 
    def render_heading(self, token):
        space = 2
        text = self.render_inner(token)
        
        if token.level == 1:
            return f"\\vspace{{\\baselineskip}}{{\\hAFont \\section*{{{text}}}}}\n" #self.figlet('standard', text.replace(' ', '  '), space=space)

        elif token.level == 2: 
            return f"\\vspace{{\\baselineskip}}{{\\hBFont \\subsection*{{{underlined(text)}}}}}\n"
        
        elif token.level == 3:
            return f"\\vspace{{\\baselineskip}}{{\\hCFont \\subsubsection*{{{text}}}}}\n" #self.figlet('cybermedium', text, space=space)
            
        elif token.level == 4:
            return f"\\vspace{{\\baselineskip}}{{\\hDFont \\subsubsection*{{{(bold(self.render_inner(token).upper()))}}}}}\n"

        elif token.level == 5:
            return _(f"""
              \\vspace{{\\baselineskip}}
              {{\\hBFont  
              \\subsubsection*{{{(bold(self.render_inner(token).upper()))}}}}}
            """)
                    
        elif token.level >= 6:
            return f"\\color{{gray}}\n\\vspace{{\\baselineskip}}{{\\hBFont \\subsubsection*{{{(self.render_inner(token).upper())}}}}}\n\\color{{black}}\n"
        
        else:
            return f"\\vspace{{\\baselineskip}}{underlined(self.render_inner(token))}\n"
        
    
    # def render_banner(self, token):
    #     text = self.render_inner(token)
    #     rendered = ""
    # 
    #     line = "=" * math.ceil((len(text) * 1.35))
    #     padding = math.ceil((len(line) - len(text)) / 2)
    #     inner_line = f"{padding * ' '}{text}{padding * ' '}"
    #     return f"{line}\n\n{inner_line}\n{line}\n"
    # # 
    #     # rendered += '\n\n' + text + '\n' + rendered
        # return rendered
    
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
        #text = self.figlet('com_sen_', self.invert_case(text), space=2)
        
        lines = text.splitlines()
        line = "=" * (max(len(lines[0]), len(lines[-1])) -1)
        
        return f"{line}\n\n{text}\n{line}\n"
    
    
    # def render_escape_sequence(self, token):
    #     if self.render_inner(token) == "\\":
    #         return "QQ"
    #     else:
    #         return super().render_escape_sequence(self, token)
    @prefixed('\n')    
    @sufixed('\n')
    def render_thematic_break(self, token):
        return '\\hrulefill\n'
    
    def render_paragraph(self, token):
        text = self.render_inner(token)
        #print('\n\n\n Here is the text-----------------: \n', text, '\n---------------\n\n\n')
        #\\vspace{{\\baselineskip}} 
        return f'{text}\n\\vspace{{\\baselineskip}}\n'        

    def render_quote(self, token):
        return f"\n\\begin{{quote}}\n{self.render_inner(token)}\n\\end{{quote}}\n"
    
    def render_list(self, token):
      self.packages['listings'] = []
      template = '\\begin{{{tag}}}\n{inner}\\end{{{tag}}}\n'
      tag = 'enumerate' if token.start is not None else 'itemize'
      inner = '\n'.join([self.render(child) for child in token.children])
      return template.format(tag=tag, inner=inner)

      #print(dir(token))
      
      # inner = ''
      # for child in token.children:
      #     inner += '\\item '
      #     inner += self.render_inner(child)
      #     inner += '\n'
      # return template.format(tag=tag, inner=inner)

      # if (token.start):
      #   rendered = f"\\begin{{enumerate}}\n{rendered}\\end{{enumerate}}"
      # else:
      #   rendered = f"\\begin{{itemize}}\n{rendered}\\end{{itemize}}"
        
      # return rendered    
    
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
          "\\end{mdframed}" \
        
        # {innards}
        # \end{{lstlisting}}
        # }}
        # \\end{{mdframed}}\n""")
        # rendered = _(f"""
        # \\begin{{mdframed}}[backgroundcolor=gray!10]
        # {{\\fontfamily{{\sfmonospace}}\\selectfont 
        # \\begin{{lstlisting}}
        # {innards}
        # \end{{lstlisting}}
        # }}
        # \\end{{mdframed}}\n""")
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

    def render_packages(self):
        pattern = '\\usepackage{options}{{{package}}}\n'
        return ''.join(pattern.format(options=options or '', package=package)
                         for package, options in self.packages.items())

    # def render_document(self, token):
    #     template = ('\\documentclass{{article}}\n'
    #                 '{packages}'
    #                 '\\begin{{document}}\n'
    #                 '{inner}'
    #                 '\\end{{document}}\n')
    #     self.footnotes.update(token.footnotes)
    #     return template.format(inner=self.render_inner(token),
    #                            packages=self.render_packages())

    # def render_bracketed_span(self, token):
    #   return token.text