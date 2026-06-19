#from src.tag_data import tag_data
from src.find_skill_gap import find_skill_gaps

def main():
    ## DAY 1-2 : Tag_data
    # try:
    #     tag_data("data/jobs_d1.db")
    # except Exception as e:
    #     print(f"Something went wrong: {e}")

    ## DAY 3-4 : Find Skill gap
    input_file_path = "data/resume_d3_eval.txt"
    db_url = "data/jobs_d3_eval.db"
    gaps = find_skill_gaps(input_file_path, db_url)
    print(gaps)
    

    ## Testing for prompt model
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
