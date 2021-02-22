FROM ubuntu:bionic

# install tex / latex / xetex and assorted packages
RUN apt-get update
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y \
  texlive-xetex texlive-fonts-extra texlive-latex-recommended \
  texlive-generic-extra lmodern

# maybe add these back later if desirable
# RUN apt-get install -y dvipng latexmk 

# install the Freefont font
RUN apt-get install -y fonts-freefont-ttf fonts-freefont-otf

# entrypoint is the xelatex binary
ENTRYPOINT ["xelatex"]