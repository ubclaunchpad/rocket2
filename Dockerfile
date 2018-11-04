FROM python:3.7-alpine

# Set up working directory
WORKDIR /app

# Copy everything into working directory
COPY . /app

# Install everything
RUN pip install pipenv
RUN pipenv install

EXPOSE 5000

CMD ["pipenv", "run", "launch"]
