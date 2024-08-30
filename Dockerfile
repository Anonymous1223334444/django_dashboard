# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.9-slim

EXPOSE 8000

LABEL maintainer="dashboard.com"

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Copy the requirements file first to leverage Docker's cache
COPY requirements.txt /tmp/requirements.txt

# Install dependencies and create a virtual environment
RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    apt-get update && \
    apt-get install -y gcc libpq-dev \
        libpango1.0-dev libpangoft2-1.0-0 libharfbuzz-dev && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    rm -rf /tmp && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /var/cache/apt/*

# Copy the application code
COPY ./app /app

# Create a non-root user and set permissions
ARG DEV=false
RUN adduser -u 5678 --disabled-password --gecos "" appuser && \
    chown -R appuser /app

ENV PATH="/py/bin:$PATH"
USER appuser

# Define the command to run the application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app.wsgi"]
