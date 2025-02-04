import json

# Path to your JSON file
json_file_path = '/Users/harshithalle/Smart-PDF-reader/structured_output_pymupdf.json'

# Load the JSON file
with open(json_file_path, 'r') as file:
    data = json.load(file)

# Now you can use the data variable to access the contents of the JSON file
# print(data)
tot = 0

for key, value in data.items():
    tot += len(value)
    print(key,len(value))
    
print(tot)