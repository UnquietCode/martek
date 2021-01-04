import sys
import mistletoe
from mistletoe.ast_renderer import ASTRenderer
from unquietcode.tools.markt import TerminalRenderer




def main():
    file_ = sys.argv[1]
    
    with open(file_, 'r') as fin:
        data = fin.read()
    
    rendered = mistletoe.markdown(data, TerminalRenderer)
    ast = mistletoe.markdown(data, ASTRenderer)
    
    print(ast)
    print(rendered)





if __name__ == '__main__':
    main()
