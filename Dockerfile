FROM python:3.6-slim

# Set up working directory
WORKDIR /app

# Copy everything into working directory
COPY . /app
