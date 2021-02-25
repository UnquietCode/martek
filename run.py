import os
import sys
import subprocess
import select
from tempfile import TemporaryDirectory

import mistletoe

from unquietcode.tools.martek import LatexRenderer


def main():

    # read from standard in (note that select() only works for unix systems)
    stdin = ""

    while sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
        data = sys.stdin.read()
        
        if data:
            stdin += data
        else:
            break
    
    # reading from stdin
    if stdin := stdin.strip():
        if len(sys.argv) > 2:
            print("usage: cat markdown.md | martek <output.pdf>")
            exit(1)
        elif len(sys.argv) == 2:
            pdf_file_path = sys.argv[1]
        else:
            pdf_file_path = os.path.join(os.getcwd(), 'output.pdf')
        
        markdown_data = stdin
    
    # reading file paths passed as arguments
    else:
        if len(sys.argv) > 3 or len(sys.argv) < 2:
            print("usage: martek <input.md> (output.pdf)")
            exit(2)
        elif len(sys.argv) == 3:
            file_path_1 = sys.argv[1]
            file_path_2 = sys.argv[2]
            
            if file_path_1.lower().endswith(".md"):
                md_file = file_path_1
                pdf_file_path = file_path_2
            elif file_path_2.lower().endswith(".md"):
                md_file = file_path_2
                pdf_file_path = file_path_1
            else:
                print("usage: martek <input.md> (output.pdf)")
                exit(3)
            
            if not pdf_file_path.lower().endswith(".pdf"):
                pdf_file_path += ".pdf"
        else:
            md_file = sys.argv[1]
            path_parts = os.path.split(md_file)
            file_name = path_parts[-1]
            base_dir = md_file[0:-1*(len(file_name))]
            pdf_file_name = file_name[0:file_name.rindex('.')] + ".pdf"
            pdf_file_path = os.path.join(base_dir, pdf_file_name)
        
        if md_file.endswith(".pdf"):
            raise Exception("markdown file is missing, did you mean to send it over stdin?")
        
        with open(md_file, 'r') as markdown_file:
            markdown_data = markdown_file.read()
        
    # render the markdown file to LaTeX
    rendered = mistletoe.markdown(markdown_data, LatexRenderer)
        
    with TemporaryDirectory() as tmp:

        # write out the Tex file
        tex_file_path = f"{tmp}/data.tex"
        tmp_pdf_path = f"{tmp}/data.pdf"

        with open(tex_file_path, 'w') as tex_file:
            tex_file.write(rendered)
            
        # process the Tex file into a PDF
        try:
            result = subprocess.check_output(['xelatex', 'data.tex'], cwd=tmp)
            print(result)
        except subprocess.CalledProcessError as ex:
            if ex.stdout:
                print(ex.stdout.decode("utf-8"))
            
            if ex.stderr:
                print(ex.stderr.decode("utf-8"))
            
            raise
        
        # write the PDF content to the correct location
        umask_original = os.umask(0o000)

        with open(tmp_pdf_path, 'rb') as tmp_pdf_file:
            with os.fdopen(os.open(pdf_file_path, os.O_WRONLY | os.O_CREAT, 0o666), 'wb') as pdf_file:
                pdf_file.write(tmp_pdf_file.read())

        os.umask(umask_original)


if __name__ == '__main__':
    main()