from src.tag_data import tag_data

def main():
    try:
        tag_data("data/jobs_d1.db")
    except Exception as e:
        print(f"Something went wrong: {e}")

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
