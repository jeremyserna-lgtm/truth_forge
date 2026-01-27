# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the project files into the container
COPY . .

# Install uv, the package manager
RUN pip install uv

# Install dependencies using uv
RUN uv pip install --system --extra dev -r pyproject.toml

# Add the src directory to the PYTHONPATH
ENV PYTHONPATH="${PYTHONPATH}:/app/src"

# Command to run the application
CMD ["python3", "scripts/run_organism_cycle.py"]
