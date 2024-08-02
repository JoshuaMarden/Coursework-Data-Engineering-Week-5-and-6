# Use the latest Python image
FROM python:latest

# Copy the requirements file
COPY requirements.txt .

# Install the Python dependencies
RUN pip3 install -r requirements.txt

# Copy the application files
COPY config.py .
COPY import_data.py .
COPY extract_from_xml.py .
COPY refine_data.py .
COPY export_data.py . 
COPY send_email.py .
COPY pipeline.py .

# Set environment variables
ENV PORT=5439 HOST=0.0.0.0

# Expose port 5439 (this is for the application, not for S3)
EXPOSE 5439

# Command to run
CMD ["python3", "pipeline.py"]