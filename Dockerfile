# Use an official Python runtime as a parent image
FROM python:3.9-slim

RUN pip3 install pandas pyarrow fastparquet
RUN pip3 install azure-storage-blob

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

RUN chmod u+x ./convertcsvtopasquet.py

# Install any needed packages specified in requirements.txt
#RUN pip install --no-cache-dir -r requirements.txt

# Run app.py when the container launches
CMD ["python", "./convertcsvtopasquet.py"]