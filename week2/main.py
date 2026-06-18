import sys
from src.prompt_model import prompt_model
from src.tag_data import tag_data



def main():
    limits = extract_rate_limits("rate_limits.txt")
    #print(limits)
    try:
        print(get_batch_size("phi3", 100, limits))
    except Exception as e:
        print("error")

    # if (len(sys.argv) == 3):
    #     try:
    #         print("calling function")
    #         response = (prompt_model(sys.argv[1], sys.argv[2]))
    #         print(response)

    #     except Exception as e:
    #         print(f"An error occurred: {e}")
    # else:
    #     print("Usage: python main.py <model> <prompt>")
    #     return 1

if __name__ == "__main__":
    main()
