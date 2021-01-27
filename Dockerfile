FROM idkwhatever:latest

RUN apt-get update
RUN apt-get install -y python3.8 python3.8-distutils wget
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.8 2
RUN wget https://bootstrap.pypa.io/get-pip.py
RUN python3 get-pip.py

ADD requirements.txt .
RUN pip3 install -r requirements.txt
RUN rm requirements.txt 

RUN mkdir /app
WORKDIR /app

ADD unquietcode ./unquietcode
ADD script2.py .
ENTRYPOINT ["python3", "script2.py"]


# FROM python:3

# WORKDIR /usr/local/

# ARG oauth_token

# CMD ["import", "os"]
# CMD ["export", ".github-oauth-token.json"]

# COPY script.py .
# ADD unquietcode /usr/local/unquietcode 
# COPY requirements.txt .
# RUN pip3 install -r requirements.txt
# COPY /root/.github-oauth-token.json .
# CMD ["python3", "./script.py"] #this assumes we already have the github info loaded

# #This is a start but we eventually want to generalize this so we can do this on any repo
# COPY /root/.github-oauth-token.json . 

# RUN pip3 install --no-cache-dir -r requirements.txt

# CMD ["python3", "./script.py", "unquietcode/martek"]

# #generalized to take a repo and