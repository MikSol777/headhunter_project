import requests
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class Company:
    """Класс данных, представляющий компанию."""
    id: int
    name: str
    description: Optional[str]
    url: str


@dataclass
class HHVacancy:
    """Класс данных, представляющий вакансию с hh.ru."""
    id: int
    title: str
    salary_from: Optional[int]
    salary_to: Optional[int]
    url: str
    company_id: int


class HHAPI:
    """Класс для взаимодействия с API HeadHunter."""

    BASE_URL = "https://api.hh.ru"

    def __init__(self):
        """Инициализация клиента API hh.ru."""
        self.session = requests.Session()

    def get_company(self, company_id: int) -> Company:
        """
        Получение информации о компании по ID.

        Args:
            company_id: ID компании на hh.ru

        Returns:
            Объект Company
        """
        response = self.session.get(f"{self.BASE_URL}/employers/{company_id}")
        response.raise_for_status()
        data = response.json()
        return Company(
            id=data["id"],
            name=data["name"],
            description=data.get("description"),
            url=data["alternate_url"]
        )

    def get_company_vacancies(self, company_id: int) -> List[HHVacancy]:
        """
        Получение всех вакансий компании.

        Args:
            company_id: ID компании на hh.ru

        Returns:
            Список объектов HHVacancy
        """
        vacancies = []
        page = 0
        while True:
            response = self.session.get(
                f"{self.BASE_URL}/vacancies",
                params={
                    "employer_id": company_id,
                    "page": page,
                    "per_page": 100
                }
            )
            response.raise_for_status()
            data = response.json()
            vacancies.extend([
                HHVacancy(
                    id=v["id"],
                    title=v["name"],
                    salary_from=v["salary"]["from"] if v.get("salary") else None,
                    salary_to=v["salary"]["to"] if v.get("salary") else None,
                    url=v["alternate_url"],
                    company_id=company_id
                )
                for v in data["items"]
            ])
            if page >= data["pages"] - 1:
                break
            page += 1
        return vacancies 