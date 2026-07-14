# Use a lightweight, official Python image
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /app

# Install necessary application dependencies
RUN pip install --no-cache-dir gradio pandas openpyxl

# Copy your python script into the container workspace
COPY poly.py .

# Expose the precise port your app runs on
EXPOSE 7436

# Command to run the application
CMD ["python", "poly.py"]
