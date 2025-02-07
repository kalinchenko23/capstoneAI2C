# Use an official Python base image
FROM python:3.10

# Set the working directory inside the container
WORKDIR /app

# Copy the application files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set the default command to run the app
EXPOSE 8000

# Run the FastAPI app with Uvicorn
CMD ["uvicorn", "api_service:app", "--host", "0.0.0.0", "--port", "8000"]