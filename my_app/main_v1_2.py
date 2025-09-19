from typing import List, Any

def process_data(data):
    return data

def concatenate_strings(strings: List[str]) -> str:
    return ''.join(strings)

def display_message(message: str):
    print(message)
    
def main():
    data = process_data("example data")
    print(data)
    strings = ["hello", "world"]
    concatenated = concatenate_strings(strings)
    display_message(concatenated)

if __name__ == "__main__":
    main()
