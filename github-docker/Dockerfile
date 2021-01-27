FROM part2:latest

# RUN mkdir /app
# WORKDIR /app



VOLUME auth
#ADD /auth/.github-oauth-token.json .
#ADD auth .
ADD script3.py .

ENTRYPOINT [ "python3", "script3.py"]