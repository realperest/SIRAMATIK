
import os

def convert_requirements():
    input_path = 'backend/requirements.txt'
    output_path = 'backend/requirements_mac.txt'
    
    try:
        # Try reading as utf-16 first (common on Windows)
        with open(input_path, 'r', encoding='utf-16') as f:
            content = f.read()
    except UnicodeError:
        try:
            # Fallback to utf-8 if utf-16 fails
            with open(input_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"Error reading file: {e}")
            return

    lines = content.splitlines()
    filtered_lines = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # Exclude windows-specific packages
        if 'pywin32' in line.lower():
            continue
        # Exclude audioop-lts (only for python 3.13+, user has 3.12)
        if 'audioop-lts' in line.lower():
            continue
        filtered_lines.append(line)
        
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(filtered_lines))
    
    print(f"Successfully created {output_path} with {len(filtered_lines)} packages.")

if __name__ == '__main__':
    convert_requirements()
