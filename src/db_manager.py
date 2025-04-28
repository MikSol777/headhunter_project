import psycopg2
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class Vacancy:
    """Класс данных, представляющий вакансию."""
    company_name: str
    title: str
    salary_from: Optional[int]
    salary_to: Optional[int]
    url: str


class DBManager:
    """Класс для управления операциями с базой данных."""

    def __init__(self, dbname: str, user: str, password: str, host: str = "localhost", port: int = 5432):
        """
        Инициализация подключения к базе данных.

        Args:
            dbname: Имя базы данных
            user: Пользователь базы данных
            password: Пароль базы данных
            host: Хост базы данных (по умолчанию: localhost)
            port: Порт базы данных (по умолчанию: 5432)
        """
        self.conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
        self.cur = self.conn.cursor()

    def get_companies_and_vacancies_count(self) -> List[Dict[str, Any]]:
        """
        Получение списка всех компаний и количества их вакансий.

        Returns:
            Список словарей, содержащих название компании и количество вакансий
        """
        self.cur.execute("""
            SELECT c.name, COUNT(v.id) as vacancy_count
            FROM companies c
            LEFT JOIN vacancies v ON c.id = v.company_id
            GROUP BY c.id, c.name
            ORDER BY vacancy_count DESC
        """)
        return [{"company": row[0], "vacancies": row[1]} for row in self.cur.fetchall()]

    def get_all_vacancies(self) -> List[Vacancy]:
        """
        Получение списка всех вакансий с названием компании, должностью, зарплатой и URL.

        Returns:
            Список объектов Vacancy
        """
        self.cur.execute("""
            SELECT c.name, v.title, v.salary_from, v.salary_to, v.url
            FROM vacancies v
            JOIN companies c ON v.company_id = c.id
            ORDER BY c.name, v.title
        """)
        return [Vacancy(*row) for row in self.cur.fetchall()]

    def get_avg_salary(self) -> float:
        """
        Получение средней зарплаты по всем вакансиям.

        Returns:
            Средняя зарплата в виде числа с плавающей точкой
        """
        self.cur.execute("""
            SELECT AVG((COALESCE(salary_from, 0) + COALESCE(salary_to, 0)) / 2)
            FROM vacancies
            WHERE salary_from IS NOT NULL OR salary_to IS NOT NULL
        """)
        return float(self.cur.fetchone()[0] or 0)

    def get_vacancies_with_higher_salary(self) -> List[Vacancy]:
        """
        Получение списка вакансий с зарплатой выше средней.

        Returns:
            Список объектов Vacancy
        """
        avg_salary = self.get_avg_salary()
        self.cur.execute("""
            SELECT c.name, v.title, v.salary_from, v.salary_to, v.url
            FROM vacancies v
            JOIN companies c ON v.company_id = c.id
            WHERE (COALESCE(v.salary_from, 0) + COALESCE(v.salary_to, 0)) / 2 > %s
            ORDER BY (COALESCE(v.salary_from, 0) + COALESCE(v.salary_to, 0)) / 2 DESC
        """, (avg_salary,))
        return [Vacancy(*row) for row in self.cur.fetchall()]

    def get_vacancies_with_keyword(self, keyword: str) -> List[Vacancy]:
        """
        Получение списка вакансий, содержащих ключевое слово в названии.

        Args:
            keyword: Ключевое слово для поиска

        Returns:
            Список объектов Vacancy
        """
        self.cur.execute("""
            SELECT c.name, v.title, v.salary_from, v.salary_to, v.url
            FROM vacancies v
            JOIN companies c ON v.company_id = c.id
            WHERE LOWER(v.title) LIKE LOWER(%s)
            ORDER BY c.name, v.title
        """, (f'%{keyword}%',))
        return [Vacancy(*row) for row in self.cur.fetchall()]

    def __del__(self):
        """Закрытие подключения к базе данных при уничтожении объекта."""
        self.cur.close()
        self.conn.close() 