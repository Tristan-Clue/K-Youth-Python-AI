import sys
from src.prompt_model import prompt_model

def main():
    if (len(sys.argv) == 3):
        try:
            print("calling function")
            response = (prompt_model(sys.argv[1], sys.argv[2]))
            print(response)

        except Exception as e:
            print(f"An error occurred: {e}")
    else:
        print("Usage: python main.py <model> <prompt>")
        return 1

if __name__ == "__main__":
    main()
