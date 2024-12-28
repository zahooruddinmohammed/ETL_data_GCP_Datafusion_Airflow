import csv
import random
import string
from faker import Faker
from google.cloud import storage
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize Faker
fake = Faker()

# Password character set
password_characters = string.ascii_letters + string.digits

# Helper functions
def sanitize_data(value):
    """Sanitize data to remove unwanted characters."""
    return value.replace('"', '').replace(',', '') if isinstance(value, str) else value

def safe_generate(generator_func, default="N/A"):
    """Safely generate data with a fallback default."""
    try:
        value = generator_func()
        return sanitize_data(value) if value else default
    except Exception:
        return default

def generate_password(length=8):
    """Generate a secure password."""
    return ''.join(random.choice(password_characters) for _ in range(length))

def upload_to_gcs(bucket_name, source_file_name, destination_blob_name):
    """Upload a file to a GCS bucket."""
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)

        blob.upload_from_filename(source_file_name)
        logging.info(f'File {source_file_name} uploaded to {destination_blob_name} in {bucket_name}.')
    except Exception as e:
        logging.error(f"Error uploading file to GCS: {e}")

# Parameters
num_employees = 100
bucket_name = 'bkt-fkemployee-data'
source_file_name = 'employee_data.csv'
destination_blob_name = 'employee_data.csv'

# Generate and save employee data to CSV
with open(source_file_name, mode='w', newline='') as file:
    fieldnames = ['first_name', 'last_name', 'department', 'email', 'phone_number', 'salary', 'password']
    writer = csv.DictWriter(file, fieldnames=fieldnames)

    writer.writeheader()
    for _ in range(num_employees):
        writer.writerow({
            "first_name": safe_generate(fake.first_name),
            "last_name": safe_generate(fake.last_name),
            "department": safe_generate(fake.job),
            "email": safe_generate(fake.email),
            "phone_number": safe_generate(fake.phone_number),
            "salary": safe_generate(lambda: fake.random_number(digits=5), "0"),
            "password": generate_password()
        })

# Upload the CSV file to GCS
upload_to_gcs(bucket_name, source_file_name, destination_blob_name)
