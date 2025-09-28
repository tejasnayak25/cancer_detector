# 1. Use an official Python runtime as a parent image
# Using a 'slim' version reduces the final image size
FROM python:3.10-slim

# 2. Set the working directory inside the container
WORKDIR /code

# 3. Copy the requirements file first to leverage Docker layer caching
# This step is only re-run if requirements.txt changes
COPY ./requirements.txt /code/requirements.txt

# 4. Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# 5. Copy the rest of your application code into the container
COPY ./app /code/app

# 6. Expose the port the app runs on
EXPOSE 8000

# 7. Define the command to run your application using uvicorn
# The host 0.0.0.0 makes the server accessible from outside the container
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]