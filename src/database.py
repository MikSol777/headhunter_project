import psycopg2
from typing import List
from dataclasses import dataclass


@dataclass
class DatabaseConfig:
    """Класс данных для конфигурации базы данных."""
    dbname: str
    user: str
    password: str
    host: str = "localhost"
    port: int = 5432


class DatabaseManager:
    """Класс для управления созданием базы данных и таблиц."""

    def __init__(self, config: DatabaseConfig):
        """
        Инициализация менеджера базы данных.

        Args:
            config: Конфигурация базы данных
        """
        self.config = config
        self.conn = None
        self.cur = None

    def connect(self):
        """Установка подключения к базе данных."""
        self.conn = psycopg2.connect(
            dbname=self.config.dbname,
            user=self.config.user,
            password=self.config.password,
            host=self.config.host,
            port=self.config.port
        )
        self.cur = self.conn.cursor()
        self.conn.autocommit = True

    def create_database(self):
        """Создание базы данных, если она не существует."""
        conn = psycopg2.connect(
            dbname="postgres",
            user=self.config.user,
            password=self.config.password,
            host=self.config.host,
            port=self.config.port
        )
        conn.autocommit = True
        cur = conn.cursor()

        cur.execute(f"SELECT 1 FROM pg_database WHERE datname = '{self.config.dbname}'")
        if not cur.fetchone():
            cur.execute(f"CREATE DATABASE {self.config.dbname}")

        cur.close()
        conn.close()

    def create_tables(self):
        """Создание необходимых таблиц в базе данных."""
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS companies (
                id INTEGER PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                url VARCHAR(255)
            )
        """)

        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS vacancies (
                id INTEGER PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                salary_from INTEGER,
                salary_to INTEGER,
                url VARCHAR(255),
                company_id INTEGER REFERENCES companies(id)
            )
        """)

    def insert_company(self, company_id: int, name: str, description: str, url: str):
        """
        Вставка данных о компании в базу данных.

        Args:
            company_id: ID компании
            name: Название компании
            description: Описание компании
            url: URL компании
        """
        self.cur.execute("""
            INSERT INTO companies (id, name, description, url)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE
            SET name = EXCLUDED.name,
                description = EXCLUDED.description,
                url = EXCLUDED.url
        """, (company_id, name, description, url))

    def insert_vacancy(self, vacancy_id: int, title: str, salary_from: int, salary_to: int, url: str, company_id: int):
        """
        Вставка данных о вакансии в базу данных.

        Args:
            vacancy_id: ID вакансии
            title: Название вакансии
            salary_from: Минимальная зарплата
            salary_to: Максимальная зарплата
            url: URL вакансии
            company_id: ID компании
        """
        self.cur.execute("""
            INSERT INTO vacancies (id, title, salary_from, salary_to, url, company_id)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE
            SET title = EXCLUDED.title,
                salary_from = EXCLUDED.salary_from,
                salary_to = EXCLUDED.salary_to,
                url = EXCLUDED.url,
                company_id = EXCLUDED.company_id
        """, (vacancy_id, title, salary_from, salary_to, url, company_id))

    def close(self):
        """Закрытие подключения к базе данных."""
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close() 