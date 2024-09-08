# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory and copy the current directory contents into the container
WORKDIR /app
COPY . /app

# Install all packages specified in requirements.txt
RUN python3.9 -m pip install --no-cache-dir -r requirements.txt

# Make port 8080 available to the world outside this container
EXPOSE 8080

# Set the entrypoint to the Python app
ENTRYPOINT ["gunicorn", "--bind", "0.0.0.0:8080", "ptaf2xml:app"]
