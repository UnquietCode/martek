FROM unquietcode/xelatex:latest

# install Python
RUN apt-get update
RUN apt-get install -y python3.8 python3.8-distutils wget
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.8 2

# install pip
RUN wget https://bootstrap.pypa.io/get-pip.py
RUN python3 get-pip.py
RUN rm get-pip.py

# install project dependencies
ADD requirements.txt .
RUN pip3 install -r requirements.txt
RUN rm requirements.txt 

# create source folder
RUN mkdir /app
WORKDIR /app

# install source code
ADD unquietcode /app/unquietcode
ADD run.py /app

ENTRYPOINT ["python3", "run.py"]