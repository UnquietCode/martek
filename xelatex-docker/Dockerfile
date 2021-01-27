FROM ubuntu:bionic

RUN apt-get update
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y \
  texlive-xetex texlive-fonts-extra texlive-latex-recommended \
  texlive-generic-extra lmodern

# RUN apt-get install -y dvipng latexmk 
RUN apt-get install -y fonts-freefont-ttf fonts-freefont-otf

ENTRYPOINT ["xelatex"]