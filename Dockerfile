# Use a lightweight Python image
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /app

# Copy project content to container
COPY . /app

# Copy the requirements file into the container
COPY requirements.txt /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# port  8000
EXPOSE 8000

# Set environment variable to avoid Python buffering
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=myproject.settings

# commant to run the app 
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
