# Use an official Python runtime as the base image
FROM --platform=linux/amd64 python:3.9 as base

# Set the working directory in the container
WORKDIR /server

# Copy the requirements.txt file to the container
COPY server/requirements.txt .

# Install the required packages
RUN pip install --no-cache-dir -r requirements.txt

CMD ["./python-server-up.sh"]
