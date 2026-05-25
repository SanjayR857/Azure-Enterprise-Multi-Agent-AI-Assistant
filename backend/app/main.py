from app.services.llm_service import llm_service

if __name__ == "__main__":
    try:
        query = input("Please enter your query: ")
        print(llm_service.chat(query))
    except Exception as e:
        print(f"An error occurred: {e}")

