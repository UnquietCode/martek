import sys
import mistletoe
from mistletoe.ast_renderer import ASTRenderer
from unquietcode.tools.martek import LatexRenderer 
from mistletoe.latex_renderer import LaTeXRenderer

def main():
  file_ = sys.argv[1]
  
  with open(file_, 'r') as fin:
      data = fin.read()
  rendered = mistletoe.markdown(data, LatexRenderer)
  ast = mistletoe.markdown(data, ASTRenderer)
  
  # print(ast)
  # print(rendered)

  f = open("test.tex", "w")
  f.write(rendered)
  f.close()


if __name__ == '__main__':
    main()
