FROM python:3.7

# Set up working directory
WORKDIR /app

# Copy everything into working directory
COPY . /app

# Install everything
RUN apt-get update
RUN pip install pipenv
RUN pipenv install

ENV FLASK_APP=server/server.py

CMD ["pipenv", "run", "launch"]
