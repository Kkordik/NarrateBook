import json
import base64
import zlib

# Example strings (need to be short enough)
string1 = "str1"
string2 = "str2"

# Create JSON and compress
json_str = json.dumps({"first": string1, "second": string2})
compressed = zlib.compress(json_str.encode())

# Base64 encode
encoded = base64.urlsafe_b64encode(compressed).decode()

# Check length constraint
if len(encoded) <= 64:
    telegram_link = f"https://t.me/botname?start={encoded}"
    print(telegram_link)
else:
    print("Encoded data exceeds 64 characters")

# Assuming 'encoded' is the received Base64 string
compressed = base64.urlsafe_b64decode(encoded)
json_str = zlib.decompress(compressed).decode()

# Parse JSON
data = json.loads(json_str)

string1 = data["first"]
string2 = data["second"]

print(string1, string2)