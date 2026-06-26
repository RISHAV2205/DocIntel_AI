# test_s3.py
import sys
sys.path.append(".")

from app.services.storage import upload_file, download_file, delete_file

# test upload
test_bytes = b"Hello S3 test"
key = upload_file(test_bytes, "test.txt", user_id=999)
print(f"Uploaded: {key}")

# test download
content = download_file(key)
print(f"Downloaded: {content}")

# test delete
delete_file(key)
print("Deleted")