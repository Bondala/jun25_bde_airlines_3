# Base image
FROM ubuntu:22.04

# Prevent interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    nano \
    vim \
    curl \
    wget \
    default-libmysqlclient-dev \
    build-essential \
    pkg-config \
    libssl-dev \
    libffi-dev \
    mysql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
RUN pip3 install --no-cache-dir \
    jupyter \
    flask \
    flask-cors \
    pandas \
    numpy \
    matplotlib \
    sqlalchemy \
    requests \
    ipykernel \
    pymysql \
    cryptography \
    pycountry \
    mysqlclient

# Create working directory
WORKDIR /workspace

# Expose ports
EXPOSE 8888 5000

# Start an interactive shell by default
CMD ["bash"]