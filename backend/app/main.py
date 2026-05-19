from app.services.llm_service import llm_service

if __name__ == "__main__":
    print(llm_service.invoke("Hello which model are you using"))