FROM python:3.7

# Set up working directory
WORKDIR /app

# Install everything - lets Docker cache this as a layer
COPY ./Pipfile .
COPY ./Pipfile.lock .
RUN pip install pipenv
RUN pipenv install

# Copy source code into working directory
COPY . /app

EXPOSE 5000

ENV FLASK_APP=server/server.py

CMD ["pipenv", "run", "launch"]
