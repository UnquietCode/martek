import hashlib
import json
import os
import re
import subprocess
from datetime import datetime
from optparse import OptionParser
from os.path import dirname, exists, join, realpath, relpath, splitext

import mistletoe
import requests
from mistletoe.ast_renderer import ASTRenderer
from unquietcode.tools.martek import LatexRenderer

# This is a script that downloads all the GitHub issues in a
# particular repository and generates a PDF for each one; the idea is
# to produce easily printable versions of all the issues for a
# repository.

with open(join(os.environ['HOME'], '.github-oauth-token.json')) as f:
    token = json.load(f)['token']

standard_headers = {'User-Agent': 'github-issues-printer/1.0',
                    'Authorization': 'bearer {0}'.format(token)}

cwd = os.getcwd()
repo_directory = realpath(join(dirname(__file__)))
tex_directory = relpath(join(repo_directory, 'tex'), cwd)
images_directory = relpath(join(tex_directory, 'images'), cwd)
pdfs_directory = relpath(join(repo_directory, 'pdfs'), cwd)

def mkdir(d):
    try:
        os.mkdir(d)
    except FileExistsError:
        pass

mkdir(tex_directory)
mkdir(images_directory)
mkdir(pdfs_directory)

def replace_image(match, download=True):
    """Rewrite an re match object that matched an image tag
    Download the image and return a version of the tag rewritten
    to refer to the local version.  The local version is named
    after the MD5sum of the URL.
    
    >>> m = re.search(r'\!\[(.*?)\]\((.*?)\)',
    ...               'an image coming up ![caption](http://blah/a/foo.png)')
    >>> replace_image(m, download=False)
    '![caption](github-print-issues/images/b62082dd8a02ea495f5e3c293eb6ee67.png)'
    """

    caption = match.group(1)
    url = match.group(2)
    hashed_url = hashlib.md5(url.encode('utf-8')).hexdigest()
    extension = splitext(url)[1]
    if not extension:
        raise Exception("No extension at the end of {0}".format(url))
    image_filename = join(images_directory, hashed_url) + extension
    if download:
        if not exists(image_filename):
            r = requests.get(url)
            with open(image_filename, 'wb') as f:
                f.write(r.content)
    return "![{0}]({1})".format(caption, image_filename)

def replace_images(md):
    """Rewrite a Markdown string to replace any images with local versions
    'md' should be a GitHub Markdown string; the return value is a version
    of this where any references to images have been downloaded and replaced
    by a reference to a local copy.
    """

    return re.sub(r'\!\[(.*?)\]\((.*?)\)', replace_image, md)

def make_markdown_quote(to_quote):
    return '>' + to_quote #latex handles the newlines for us so it's ok to just put everything in one block quote line
    #return '>' + '\n>'.join(textwrap.wrap(str, 80, break_long_words=False))
    #return ''.join([">" + str[i:i+80] + "\n" for i in range(0, len(str), 80)])

def encode(to_encode):
    return to_encode.encode('utf-8')

def main(repo):

    page = 1
    while True:
        issues_url = 'https://api.github.com/repos/{0}/issues'.format(repo)
        r = requests.get(issues_url,
                         params={'per_page': '100',
                                 'page': str(page),
                                 'state': 'open'},
                         headers=standard_headers)
        if r.status_code != 200:
            raise Exception("HTTP status {0} on fetching {1}".format(
                r.status_code,
                issues_url))

        issues_json = r.json()
        for issue in issues_json:
            number = issue['number']
            title = issue['title']
            body = issue['body']

            # if number != 14:
            #     continue

            # TODO use temp file instead of writing .tex file
            # ntf = tempfile.NamedTemporaryFile(suffix='.tex', delete=True)
            # md_filename = ntf.name

            md_content = ""
            md_content += "# #{0} – {1}\n".format(number, title)
            md_content += "**Reported by @{0}**\n".format(issue['user']['login'])
            
            if issue['milestone']:
                md_content += '**Milestone: {0}**\n'.format(issue['milestone']['title'])
           
            md_content += "\n"
            
            # Increase the indent level of any Markdown heading
            body = re.sub(r'^(#+)', r'#\1', body)
            body = replace_images(body)
            
            md_content += body
            md_content += "\n\n"
            if issue['comments'] > 0:
                comments_request = requests.get(issue['comments_url'],
                                                headers=standard_headers)
                for comment in comments_request.json():
                    #print(json.dumps(comment, indent=2)) 
                    USER = comment['user']['login']
                    RAW_DATETIME = comment['created_at']
                    DATETIME_OBJ = datetime.strptime(RAW_DATETIME, '%Y-%m-%dT%H:%M:%SZ')
                    DATE = DATETIME_OBJ.date() #2021-01-09T20:41:02Z
                    DATE_WORDS = DATE.strftime('%A %d %B %Y')
                    md_content += ("\n### @{0} wrote on {1}".format(USER, DATE_WORDS))
                    md_content += '\n\n'
                    comment_body = comment['body']
                    comment_body = re.sub(r'^(#+)', r'###\1', comment_body)
                    comment_body = replace_images(comment_body)
                    md_content += comment_body
                    md_content += "\n\n"

            # render to .tex file
            md_file_path = "./pdfs/issue_{}.md".format(number)
            file = open(md_file_path, "w")
            file.write(md_content)
            file.close()

            tex_file_path = "./tex/issue_{}.tex".format(number)

            with open(md_file_path, 'r') as fin:
                data = fin.read()
                rendered = mistletoe.markdown(data, LatexRenderer)
                ast = mistletoe.markdown(data, ASTRenderer)

                f = open(tex_file_path, "w")
                f.write(rendered)
                f.close()

            subprocess.check_call(['xelatex', '-output-directory=./pdfs', tex_file_path])

        page += 1
        if 'Link' not in r.headers:
            break

usage = """Usage: %prog [options] REPOSITORY
Repository should be username/repository from GitHub, e.g. mysociety/pombola"""
parser = OptionParser(usage=usage)
parser.add_option("-t", "--test", action="store_true", dest="test", default=False, help="Run doctests")
(options, args) = parser.parse_args()

if len(args) != 1:
    parser.print_help()
else:
    main(args[0])
