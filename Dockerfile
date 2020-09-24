FROM python:3.8

# Let Docker cache things that persist between runs
RUN pip install pipenv

# Set up working directory
WORKDIR /app

# Install everything - lets Docker cache this as a layer
COPY ./Pipfile .
COPY ./Pipfile.lock .
RUN pipenv install

# Copy source code into working directory
COPY . /app

EXPOSE 5000

ENV FLASK_APP=server/server.py

CMD ["pipenv", "run", "launch"]
