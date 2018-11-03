FROM python:3.7-alpine

# Set up working directory
WORKDIR /app

# Copy everything into working directory
COPY . /app

# Install everything
RUN pip install pipenv
RUN pipenv install

ENV FLASK_APP=server/server.py

CMD ["pipenv", "run", "launch"]
