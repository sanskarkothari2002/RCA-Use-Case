import os
import re

def extract_errors_from_logs(folder_path, output_file=None):

    error_pattern = re.compile(r'^.*(?:error|failed).*$', re.IGNORECASE | re.MULTILINE)

    errors = set()

    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
    
        if os.path.isfile(file_path) and filename.endswith('.log'):
            try:
                with open(file_path, 'r', errors='ignore') as f:
                    content = f.read()

                    matching_lines = error_pattern.findall(content)

                    for line in matching_lines:
                        errors.add(f"{filename}: {line.strip()}")

            except Exception as e:
                print(f"Error reading {file_path}: {e}")

    collected_errors = sorted(errors)

    if output_file:
        with open(output_file, 'w') as out:
            out.write('\n\n'.join(collected_errors))
        print(f"Errors written to {output_file}")
    else:
        for line in collected_errors:
            print(line)

log_folder = "/Users/sanskar/Downloads/sosreport-rhel9test-2025-08-14-wwztooy/var/log"
output_path = "/Users/sanskar/Downloads/collected_errors.txt"

extract_errors_from_logs(log_folder, output_file=output_path)
