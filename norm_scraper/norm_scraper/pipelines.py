import asyncio
import json
import os
import psycopg2
import pandas as pd
from datetime import datetime
from email.encoders import encode_base64
from typing import Optional
from psycopg2 import Error
from sqlalchemy import create_engine
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from aiosmtplib import SMTP


class PostgresPipeline(object):
    def __init__(self):
        self.user_base = os.getenv('user_base')
        self.password_base = os.getenv('password_base')
        self.host_base = os.getenv('host_base')
        self.port_base = os.getenv('port_base')
        self.name_database = os.getenv('name_database')
        self.connection = None
        self.cursor = None
        self.engine = None

    def create_base(self):
        try:
            with psycopg2.connect(user=self.user_base, password=self.password_base,
                                  host=self.host_base, port=self.port_base,
                                  database=self.name_database) as self.connection:
                self.execute_create_base()
        except (Exception, Error) as error:
            print("Ошибка при работе с PostgreSQL", error)
        finally:
            if self.connection:
                self.cursor.close()
                self.connection.close()
                print("Соединение с PostgreSQL закрыто")

    def execute_create_base(self):
        self.cursor = self.connection.cursor()
        print("Информация о сервере PostgreSQL")
        print(self.connection.get_dsn_parameters(), "\n")
        self.cursor.execute("SELECT version();")
        record = self.cursor.fetchone()
        print("Вы подключены к - ", record, "\n")

    def create_table(self):
        try:
            with psycopg2.connect(user=self.user_base, password=self.password_base,
                                  host=self.host_base, port=self.port_base,
                                  database=self.name_database) as self.connection:
                self.execute_create_table()
        except (Exception, Error) as error:
            print("Ошибка при работе с PostgreSQL", error)
        finally:
            if self.connection:
                self.cursor.close()
                self.connection.close()
                print("Соединение с PostgreSQL закрыто")

    def execute_create_table(self):
        self.cursor = self.connection.cursor()
        # SQL-запрос для создания новой таблицы
        create_table_query = '''CREATE TABLE cameranorm (
        ID           SERIAL PRIMARY KEY,
        article      TEXT DEFAULT '', -- Артикул
        title        TEXT DEFAULT '', -- Наименование
        description  TEXT DEFAULT '', -- Описание
        current_retail       DECIMAL(14, 2) DEFAULT '0', -- Текущая розничная цена
        current_dealer       DECIMAL(14, 2) DEFAULT '0', -- Текущая оптовая цена
        old_retail       DECIMAL(14, 2) DEFAULT '0', -- Предыдущая розничная цена
        old_dealer       DECIMAL(14, 2) DEFAULT '0', -- Предыдущая оптовая цена
        availability DECIMAL(14, 2) DEFAULT '0', -- Наличие
        price_list   TEXT DEFAULT 'Нет в прайсах', -- Наименование прайс-листа
        grp          TEXT DEFAULT 'Нет в группах', -- Наименование группы
        photo        TEXT DEFAULT '', -- Фото на сайте
        link         TEXT DEFAULT '', -- Ссылка на сайте
        brand        TEXT DEFAULT 'NORM', -- Бренд
        date_update  TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Значение текущего времени по умолчанию
        source       TEXT DEFAULT 'cameranorm', -- Название источника
        type_change  TEXT DEFAULT 'Новый товар' -- тип изменения (Новый товар - при создании новой позиции)
        ); '''
        rename_table_query = '''ALTER TABLE norm_original RENAME TO cameranorm; '''
        delete_table_query = '''DELETE FROM analog; '''
        update_table_query = '''UPDATE cameranorm SET source = 'cameranorm'; '''
        self.cursor.execute(create_table_query)
        self.connection.commit()
        print(f"Таблица: norm успешно создана в PostgreSQL")

    def create_table_analog(self):
        try:
            with psycopg2.connect(user=self.user_base, password=self.password_base,
                                  host=self.host_base, port=self.port_base,
                                  database=self.name_database) as self.connection:
                self.execute_create_table_analog()
        except (Exception, Error) as error:
            print("Ошибка при работе с PostgreSQL", error)
        finally:
            if self.connection:
                self.cursor.close()
                self.connection.close()
                print("Соединение с PostgreSQL закрыто")

    def execute_create_table_analog(self):
        self.cursor = self.connection.cursor()
        # SQL-запрос для создания новой таблицы analog
        create_table_query = '''
            CREATE TABLE IF NOT EXISTS analog (
                id SERIAL PRIMARY KEY,
                article VARCHAR(256),
                brand VARCHAR(256),
                article_cross VARCHAR(256),
                brand_cross VARCHAR(256),
                source VARCHAR(256),
                composite_key TEXT UNIQUE
            );

            -- Индекс по уникальному полю composite_key
            CREATE INDEX idx_composite_key ON analog(composite_key);
            '''

        self.cursor.execute(create_table_query)
        self.connection.commit()
        print(f"Таблица: analog успешно создана в PostgreSQL")

    def open_spider(self, spider):
        self.connection = psycopg2.connect(user=self.user_base, password=self.password_base,
                                           host=self.host_base, port=self.port_base,
                                           database=self.name_database)
        self.cursor = self.connection.cursor()

    def close_spider(self, spider):
        self.cursor.close()
        self.connection.close()

    def process_item(self, item, spider):
        query = """
        INSERT INTO cameranorm (
            article, title, description, current_retail, current_dealer, 
            old_retail, old_dealer, availability, price_list, grp, photo, link, brand, date_update, source, type_change
        ) VALUES (
            %(article)s, %(title)s, %(description)s, %(current_retail)s::numeric, %(current_dealer)s::numeric, 
            %(current_retail)s::numeric, %(current_dealer)s::numeric, %(availability)s::numeric, 'Нет в прайсах', 
            'Нет в группах', %(photo)s, %(link)s, %(brand)s, NOW(), 'cameranorm', 'Новый товар'
        ) ON CONFLICT (article) DO UPDATE SET
            title = EXCLUDED.title,
            description = EXCLUDED.description,
            current_retail = EXCLUDED.current_retail,
            current_dealer = EXCLUDED.current_dealer,
            availability = EXCLUDED.availability,
            photo = EXCLUDED.photo,
            link = EXCLUDED.link,
            brand = EXCLUDED.brand,
            date_update = NOW();
        """

        # Подготовка параметров для безопасной передачи
        prepared_data = {
            'article': item['article'],
            'title': item['title'],
            'description': item['description'],
            'current_retail': float(item['current_retail']),  # Convert to numeric explicitly
            'current_dealer': float(item['current_dealer']),
            'availability': int(item['availability']),
            'photo': item['photo'],
            'link': item['link'],
            'brand': item['brand']
        }

        try:
            self.cursor.execute(query, prepared_data)
            self.connection.commit()
        except Exception as e:
            # Логирование ошибки
            spider.logger.error(f"Error executing SQL: {str(e)}")
            self.connection.rollback()

        return item

    def change_statuses(self):
        try:
            with psycopg2.connect(user=self.user_base, password=self.password_base,
                                  host=self.host_base, port=self.port_base,
                                  database=self.name_database) as self.connection:
                self.execute_change_statuses()
        except (Exception, Error) as error:
            print("Ошибка при работе с PostgreSQL", error)
        finally:
            if self.connection:
                self.cursor.close()
                self.connection.close()
                print("Соединение с PostgreSQL закрыто")

    def execute_change_statuses(self):
        self.cursor = self.connection.cursor()
        today_date = datetime.now().date()

        query_get_records = """
                        SELECT id, current_retail, current_dealer, old_retail, old_dealer, date_update FROM cameranorm;
                        """
        self.cursor.execute(query_get_records)
        records = self.cursor.fetchall()

        for record in records:
            row_id, curr_retail, curr_dealer, old_retail, old_dealer, update_date = record

            if today_date > update_date.date():
                new_status = 'Убрали с сайта'
            else:
                retail_changed = False
                dealer_changed = False
                status_part = ''

                # Розничная цена изменилась?
                if curr_retail < old_retail:
                    retail_changed = True
                    percent = (1 - curr_retail / old_retail) * 100
                    status_part = f'Подешевела розница на {percent}%'
                elif curr_retail > old_retail:
                    retail_changed = True
                    percent = (1 - old_retail / curr_retail) * 100
                    status_part = f'Подорожала розница на {percent}%'

                # Оптовая цена изменилась?
                if curr_dealer < old_dealer:
                    dealer_changed = True
                    percent = (1 - curr_dealer / old_dealer) * 100
                    if retail_changed:
                        status_part += f' и подешевела оптовая цена на {percent}%'
                    else:
                        status_part = f'Подешевела оптовая на {percent}%'
                elif curr_dealer > old_dealer:
                    dealer_changed = True
                    percent = (1 - old_dealer / curr_dealer) * 100
                    if retail_changed:
                        status_part += f' и подорожала оптовая цена на {percent}%'
                    else:
                        status_part = f'Подорожала оптовая на {percent}%'

                # Цены не изменились
                if not retail_changed and not dealer_changed:
                    new_status = 'Нет изменений'
                else:
                    new_status = status_part

            # Обновление статуса
            update_query = f"""
                        UPDATE cameranorm SET type_change=%s WHERE id=%s;
                        """
            self.cursor.execute(update_query, (new_status, row_id))

        self.connection.commit()

    def fetch_data_from_db(self) -> Optional[pd.DataFrame]:
        """
        Извлекает данные из базы данных *PostgresQL* по заданному запросу.

        Эта функция извлекает записи из таблицы **cameranorm**, где поле **type_change** отличается
        от значений *Нет изменений* и *Убрали с сайта*. Результат возвращается в виде:

        :param self: экземпляр текущего класса.
        :return:
        • **pandas.DataFrame**: таблица данных, содержащая выбранные записи.
        • **None**: если база данных пуста или возникла ошибка при выполнении запроса.
        :raises Exception: возникает, если возникли проблемы с подключением к базе данных или выполнением SQL-запроса.
        """
        try:
            self.engine = create_engine(
                f"postgresql+psycopg2://{self.user_base}:{self.password_base}@"
                f"{self.host_base}:{self.port_base}/"
                f"{self.name_database}")
            sql_query = """
                            SELECT *
                            FROM cameranorm
                            WHERE type_change NOT IN ('Нет изменений', 'Убрали с сайта');
                        """
            df = pd.read_sql(sql_query, con=self.engine)
            if len(df) > 0:
                return df
            else:
                return None
        except Exception as e:
            print("Ошибка при работе с базой данных:", str(e))
            return None
        finally:
            if self.engine:
                self.engine.dispose()
                print("Соединение с базой данных закрыто.")

    @staticmethod
    def create_excel_file(df):
        """Создаем Excel-файл с записями."""
        file_path = 'NORM.xlsx'
        df.to_excel(file_path, index=False)
        print(f"Сформирован файл {file_path}")
        return file_path

    @staticmethod
    async def send_mail(file_path: str):
        to_emails_str = os.getenv('TO_EMAILS')
        to_emails = json.loads(to_emails_str)
        message = MIMEMultipart()
        message["From"] = os.getenv('FROM_EMAIL')
        message["To"] = ", ".join(to_emails)
        message["Subject"] = 'Изменившиеся позиции товаров NORM'
        message_text = "<h1>Добрый день! Приложены товары, у которых произошли изменения по бренду NORM.</h1>"

        # Основной контент письма (HTML-текст)
        html_content = f"<html><body>{message_text}</body></html>"
        message.attach(MIMEText(html_content, "html", "utf-8"))

        # Добавляем вложение, если оно было передано
        if file_path:
            with open(file_path, "rb") as file:
                # Создаем новый MIMEBase объект для вложения
                part = MIMEBase("application", "octet-stream")
                part.set_payload(file.read())
                encode_base64(part)
                part.add_header("Content-Disposition", f"attachment; filename={os.path.basename(file_path)}")
                message.attach(part)

        try:
            smtp_client = SMTP(hostname="smtp.mail.ru", port=465, use_tls=True)
            async with smtp_client:
                await smtp_client.login(os.environ["FROM_EMAIL"], os.environ["EMAIL_PASSWORD"])
                await smtp_client.send_message(message)

            # Удаляем файл после успешной отправки
            os.remove(file_path)
        except Exception as e:
            print(f"Произошла ошибка при отправке письма: {str(e)}")

    def send_message(self, excel_file: str):
        asyncio.run(self.send_mail(excel_file))
