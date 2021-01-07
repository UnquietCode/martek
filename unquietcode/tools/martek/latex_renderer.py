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

# class BracketedSpan(SpanToken):
    # pattern = re.compile(r'\[(.*?)\]\{(.*?)\}')
    # parse_inner = False
    # parse_group = 0
#   def __init__(self, match):
#       self.text = EscapeSequence.strip(match.group(1).strip())
#       self.meta = EscapeSequence.strip(match.group(2))



PREAMBLE = """
\\documentclass{article}
\\usepackage{mdframed}
\\usepackage{hyperref}
\\usepackage{ulem}
\\usepackage{xcolor}
\\usepackage{listings}
\\usepackage{etoolbox}
\n\\begin{document}""" #\\AtBeginEnvironment{quote}{\\singlespacing\\small}
#\\newcommand*{\\code_font}{\\fontfamily{otf}\\selectfont}

POSTAMBLE = "\\end{document}"

TRAILING_WHITESPACE = ""


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
  return textwrap.dedent(input).strip()


class LatexRenderer(BaseRenderer):

    def __init__(self):
        super().__init__()
        
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
        return self.render_to_plain(token)
        
        
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
        return f"\\lstinline{{{self.render_inner(token)}}} "
    
    def render_block_code(self, token):
        return _(f"""\\begin{{lstlisting}}
                    {{\code_font {self.render_inner(token)} }}
                    \\end{{lstlisting}}""")


    def render_line_break(self, token):
        return '\\\\\n'

    def render_link(self, token):
      return f"\\href{{{token.target}}}{{{underlined(self.render_inner(token))}}}"

    # @prefixed('\n')
    @sufixed('\n') 
    def render_heading(self, token):
        space = 2
        text = self.render_to_plain(token)
        
        if token.level == 1:
            return f"\\part*{{{text}}}\n" #self.figlet('standard', text.replace(' ', '  '), space=space)

        elif token.level == 2: 
            return f"\\section*{{{underlined(text)}}}\n"
        
        elif token.level == 3:
            return f"\\subsection*{{{text}}}\n" #self.figlet('cybermedium', text, space=space)
            
        elif token.level == 4:
            return f"\\subsubsection*{{{(bold(self.render_inner(token).upper()))}}}\n"

        elif token.level == 5:
            return _(f"""
              \\paragraph*{{{(bold(self.render_inner(token).upper()))}}}
              \\vspace{{\\baselineskip}}
            """)
                    
        elif token.level >= 6:
            return f"\\subparagraph*{{{(self.render_inner(token).upper())}}}\n\\vspace{{\\baselineskip}}"
        
        else:
            return f"{underlined(self.render_inner(token))}\n"
        
    
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
        return f'{text}'        

    def render_quote(self, token):
        return f"\n\\begin{{quote}}\n{self.render_inner(token)}\n\\end{{quote}}\n"
    
    def render_list(self, token):
      #print(dir(token))
      rendered = ''
      for child in token.children:
          rendered += '\\item '
          rendered += self.render_inner(child)
          rendered += '\n'

      if (token.start):
        rendered = f"\\begin{{enumerate}}\n{rendered}\\end{{enumerate}}"
      else:
        rendered = f"\\begin{{itemize}}\n{rendered}\\end{{itemize}}"
        
      return rendered    
    
    def render_list_item(self, token):
        rendered = ""
        line = self.render_inner(token)
        
        if line.strip():
            rendered += f"\item {line.strip()} \n"
        
        return rendered
        
    
    def render_block_code(self, token):
        innards = self.render_inner(token)
        rendered = f"\n\\begin{{mdframed}}[backgroundcolor=gray!10]\n\\begin{{lstlisting}}\n{innards}\n\\end{{lstlisting}}\n\\end{{mdframed}}\n"
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