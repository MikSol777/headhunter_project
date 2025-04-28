import os
from dotenv import load_dotenv
from typing import List
from src.database import DatabaseConfig, DatabaseManager
from src.hh_api import HHAPI, Company, HHVacancy
from src.db_manager import DBManager


def get_company_ids() -> List[int]:
    """
    Get list of company IDs to fetch data for.

    Returns:
        List of company IDs
    """
    # Примеры ID компаний с hh.ru
    return [
        1740,   # Яндекс
        78638,  # Тинькофф
        3529,   # Сбер
        15478,  # ВКонтакте
        84585,  # Авито
        2180,   # Ozon
        3776,   # МТС
        2748,   # Ростелеком
        3127,   # Мегафон
        907345  # Альфа-Банк
    ]


def main():
    # Загрузка переменных окружения
    load_dotenv(encoding='utf-8')
    
    # Configuration
    config = DatabaseConfig(
        dbname=os.getenv('DB_NAME', 'headhunter_project'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', ''),
        host=os.getenv('DB_HOST', 'localhost'),
        port=int(os.getenv('DB_PORT', '5432'))
    )

    # Initialize database
    db_manager = DatabaseManager(config)
    
    try:
        # Создание базы данных и таблиц
        print("Создание базы данных...")
        db_manager.create_database()
        db_manager.connect()
        db_manager.create_tables()
        
        # Initialize API client
        hh_api = HHAPI()

        # Fetch and store data
        for company_id in get_company_ids():
            print(f"Обработка компании с ID {company_id}...")
            
            # Get company info
            company = hh_api.get_company(company_id)
            db_manager.insert_company(
                company_id=company.id,
                name=company.name,
                description=company.description,
                url=company.url
            )

            # Get company vacancies
            vacancies = hh_api.get_company_vacancies(company_id)
            for vacancy in vacancies:
                db_manager.insert_vacancy(
                    vacancy_id=vacancy.id,
                    title=vacancy.title,
                    salary_from=vacancy.salary_from,
                    salary_to=vacancy.salary_to,
                    url=vacancy.url,
                    company_id=company_id
                )

            print(f"Обработано {len(vacancies)} вакансий")
        
        print("\nАнализ данных:")
        print("1. Количество вакансий по компаниям:")
        for company in db_manager.get_companies_and_vacancies_count():
            print(f"   {company['name']}: {company['vacancies']} вакансий")
        
        avg_salary = db_manager.get_avg_salary()
        print(f"\n2. Средняя зарплата: {avg_salary:.2f} руб.")
        
        print("\n3. Вакансии с зарплатой выше средней:")
        for vacancy in db_manager.get_vacancies_with_higher_salary():
            print(f"   {vacancy.company_name} - {vacancy.title}")
            print(f"   Зарплата: {vacancy.salary_from}-{vacancy.salary_to} руб.")
            print(f"   URL: {vacancy.url}\n")
        
        keyword = "Python"
        print(f"\n4. Вакансии с ключевым словом '{keyword}':")
        for vacancy in db_manager.get_vacancies_with_keyword(keyword):
            print(f"   {vacancy.company_name} - {vacancy.title}")
            print(f"   Зарплата: {vacancy.salary_from}-{vacancy.salary_to} руб.")
            print(f"   URL: {vacancy.url}\n")
            
    except Exception as e:
        print(f"Произошла ошибка: {e}")
    finally:
        db_manager.close()

    # Initialize DBManager for queries
    db = DBManager(
        dbname=config.dbname,
        user=config.user,
        password=config.password,
        host=config.host,
        port=config.port
    )

    # Example queries
    print("\nCompanies and their vacancy counts:")
    for company in db.get_companies_and_vacancies_count():
        print(f"{company['company']}: {company['vacancies']} vacancies")

    print("\nAverage salary:", db.get_avg_salary())

    print("\nVacancies with higher than average salary:")
    for vacancy in db.get_vacancies_with_higher_salary():
        print(f"{vacancy.company_name} - {vacancy.title}: {vacancy.salary_from}-{vacancy.salary_to}")

    keyword = "python"
    print(f"\nVacancies with keyword '{keyword}':")
    for vacancy in db.get_vacancies_with_keyword(keyword):
        print(f"{vacancy.company_name} - {vacancy.title}: {vacancy.salary_from}-{vacancy.salary_to}")


if __name__ == "__main__":
    main()
