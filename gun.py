import os
import requests

def download_file_from_github(github_url, local_path):
    """Download a file from GitHub raw URL to a local path."""
    try:
        response = requests.get(github_url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        with open(local_path, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded file from GitHub to {local_path}")
    except requests.exceptions.RequestException as e:
        print(f"Error downloading file: {e}")

def load_guns(file_path):
    """Load guns from a file."""
    guns = []
    try:
        with open(file_path, 'r') as f:
            for line in f:
                if line.strip():
                    parts = line.strip().split('|')
                    if len(parts) == 3:
                        gun_id, gun_hex, gun_name = parts
                        guns.append((gun_hex.strip(), gun_name.strip()))
    except Exception as e:
        print(f"Error reading guns.txt file: {e}")
    return guns

def find_full_sequence(file_path, hex_value):
    """Find the full sequence of a gun (5 bytes before + hex value)."""
    try:
        with open(file_path, 'rb') as f:
            data = f.read()
            index = data.find(bytes.fromhex(hex_value))
            if index != -1 and index >= 5:
                return data[index - 5:index + len(bytes.fromhex(hex_value))].hex()
    except Exception as e:
        print(f"Error processing file: {e}")
    return None

def replace_full_sequence_in_file(file_path, output_folder, gun1_full_value, gun2_full_value):
    """Replace gun1's full sequence with gun2's full sequence."""
    try:
        with open(file_path, 'rb') as f:
            data = f.read()

        old_sequence = bytes.fromhex(gun1_full_value)
        new_sequence = bytes.fromhex(gun2_full_value)

        if old_sequence in data:
            data = data.replace(old_sequence, new_sequence)
            output_file_path = os.path.join(output_folder, os.path.basename(file_path))
            with open(output_file_path, 'wb') as f:
                f.write(data)
            print(f"Replaced {gun1_full_value} with {gun2_full_value} in {output_file_path}")
        else:
            print(f"{gun1_full_value} not found in file: {file_path}")
    except Exception as e:
        print(f"Error editing file: {e}")

def process_files(folder_path, output_folder, gun1, gun1_name, gun2, gun2_name, result_path):
    results = []
    gun1_file = None
    gun1_full_value = None
    gun2_full_value = None

    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.dat'):
                file_path = os.path.join(root, file)
                
                # Find gun1 full sequence
                gun1_sequence = find_full_sequence(file_path, gun1)
                if gun1_sequence:
                    gun1_full_value = gun1_sequence
                    results.append(f"{gun1_name} - {gun1_full_value}")
                    gun1_file = file_path
                
                # Find gun2 full sequence
                gun2_sequence = find_full_sequence(file_path, gun2)
                if gun2_sequence:
                    gun2_full_value = gun2_sequence
                    results.append(f"{gun2_name} - {gun2_full_value}")

    # Save results to result.txt
    try:
        with open(result_path, 'w') as f:
            f.write("\n".join(results) + "\n")
        print(f"Results saved to {result_path}")
    except Exception as e:
        print(f"Error writing to result.txt: {e}")

    # Replace sequences in gun1's file
    if gun1_file and gun1_full_value and gun2_full_value:
        print(f"\nModifying file: {gun1_file}")
        replace_full_sequence_in_file(gun1_file, output_folder, gun1_full_value, gun2_full_value)

def search_and_select_guns(guns):
    """Search and select a gun from the list."""
    def search_guns(keyword):
        return [
            (hex_code, name) for hex_code, name in guns
            if keyword.lower() in name.lower() or keyword.lower() in hex_code.lower()
        ]

    def display_results(results):
        print("\nAvailable guns:")
        for idx, (hex_code, name) in enumerate(results, start=1):
            print(f"{idx}: {name} | {hex_code}")

    print("\nSearch and select a gun:")
    while True:
        keyword = input("Enter gun name or hex code (or type 'list' to show all): ")
        if keyword.lower() == 'list':
            results = guns  # Show all guns
        else:
            results = search_guns(keyword)

        if results:
            display_results(results)
            selection = input("\nSelect a gun by number: ")
            if selection.isdigit():
                selection = int(selection) - 1
                if 0 <= selection < len(results):
                    selected_hex, selected_name = results[selection]
                    print(f"Selected: {selected_name} | {selected_hex}")
                    return selected_hex, selected_name
        else:
            print("No guns found. Try again.")

# Main script
if __name__ == "__main__":
    # GitHub URLs for your files
    github_guns_file = "https://raw.githubusercontent.com/katagirikun/Skinobb/main/AUTOGUN/result/guns.txt"
    github_result_file = "https://raw.githubusercontent.com/katagirikun/Skinobb/main/AUTOGUN/result/result.txt"

    # Local paths for downloaded files
    local_guns_file = "AUTOGUN/result/guns.txt"
    local_result_file = "AUTOGUN/result/result.txt"
    output_folder = "AUTOGUN/result/"  # Output folder for modified files

    # Download files from GitHub
    download_file_from_github(github_guns_file, local_guns_file)
    download_file_from_github(github_result_file, local_result_file)

    guns = load_guns(local_guns_file)
    if not guns:
        print("No guns found. Check the file format.")
    else:
        print("Select Gun1:")
        gun1, gun1_name = search_and_select_guns(guns)
        print("\nSelect Gun2:")
        gun2, gun2_name = search_and_select_guns(guns)
        process_files("AUTOGUN/", output_folder, gun1, gun1_name, gun2, gun2_name, local_result_file)
