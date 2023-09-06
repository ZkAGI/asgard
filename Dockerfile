# Use an official Python runtime as the base image
FROM python:3.8-slim-buster

# Create and set the working directory inside the container
WORKDIR /app

# Copy the application requirements.txt to the container
COPY requirements.txt /app/

# Install application dependencies
RUN pip install -r requirements.txt

# Copy the application code into the container
COPY . /app/

# Copy the entry point script into the container
COPY docker-entrypoint.sh /app/

# Make the entry point script executable
RUN chmod +x /app/docker-entrypoint.sh

# Set the entry point for the container
ENTRYPOINT ["/app/docker-entrypoint.sh"]
