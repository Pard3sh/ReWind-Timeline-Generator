# basic dockerfile to containarize python script that updates all un-analyzed entries in the ReWind firestore Cloud DB.

# python image for holding the python script
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1

# copy requirements into the container environment, then install all required dependencies in the container environment
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy entire directory into the container environment so that the code can be run
COPY . .

# run the batch job -- will be and must only be done as a cloud job in the google cloud platform
CMD ["python", "job.py"]