# use a lightweight offical python iamge
FROM Python:3.13-slim

# Prevent Python from writing temporary .pyc files to disk
ENV PYTHONDONTWRITEBYTECODE=1

# Prevent Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /app

# install standard linux build tools needed by some libraries
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

# Copy your requirements.txt from your local machine into the container
COPY requirements.txt .

# Install the Python dependencies (without caching to keep the image small)
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code into the container
COPY . .

# Expose the port your app runs on
EXPOSE 8000

# Run your app (FastAPI)
CMD ["uvicorn", "main:app", "--host", "[IP_ADDRESS]", "--port", "8000", "--reload"]