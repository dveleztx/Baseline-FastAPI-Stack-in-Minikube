# Pull official base image
FROM python:3.8.11-slim-buster

# Set working directory
WORKDIR /usr/src/app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONGUNBUFFERED 1

# Install system dependencies
RUN apt update \
    && apt -y install netcat gcc postgresql \
    && apt clean

# Install python dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# Add app
COPY . .

# Expose
EXPOSE 8000

# Add entrypoint
RUN chmod +x /usr/src/app/entrypoint.sh

# Run entrypoint.sh
ENTRYPOINT ["/usr/src/app/entrypoint.sh"]
