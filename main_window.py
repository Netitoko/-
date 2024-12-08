import sys
import os
import sqlite3
import pandas as pd
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QLabel, QPushButton,
    QTabWidget, QWidget, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QMessageBox, QCheckBox, QComboBox, QLineEdit, QCalendarWidget, QDialog,
    QFormLayout, QColorDialog, QHeaderView, QFileDialog
)
from PyQt6.QtCore import Qt, QDate, QDateTime
from PyQt6.QtGui import QColor
from admin_window import AdminWindow


class MainWindow(QMainWindow):
    """
    Основной класс для интерфейса системы управления документами.
    """
    def __init__(self, user_info):
        super().__init__()
        self.user_info = user_info
        self.file_path = None
        self.setWindowTitle("Система учёта документов")
        self.setGeometry(300, 150, 800, 600)

        self.init_ui()

    def init_ui(self):
        """
        Создает пользовательский интерфейс.
        """
        main_widget = QWidget()
        main_layout = QVBoxLayout()

        # Верхняя панель
        self.create_top_panel(main_layout)

        # Вкладки
        self.tabs = QTabWidget()
        self.init_tabs()
        main_layout.addWidget(self.tabs)

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

    def create_top_panel(self, layout):
        """
        Отображает информацию о пользователе и добавляет кнопку выхода.
        """
        top_panel = QHBoxLayout()

        # ФИО пользователя
        user_label = QLabel(
            f'{self.user_info["last_name"]} {self.user_info["first_name"][0]}.{self.user_info["middle_name"][0]}.'
        )
        user_label.setStyleSheet("font-size: 14pt;")
        user_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        # Кнопка выхода
        logout_button = QPushButton("Выход")
        logout_button.clicked.connect(self.logout)

        # Лейаут для кнопок (все элементы выравниваем справа)
        right_panel = QHBoxLayout()
        right_panel.addWidget(logout_button)
        right_panel.setAlignment(Qt.AlignmentFlag.AlignRight)

        # Добавление элементов в верхнюю панель
        top_panel.addWidget(user_label, alignment=Qt.AlignmentFlag.AlignLeft)
        top_panel.addLayout(right_panel)

        # Добавление панели в основной layout
        layout.addLayout(top_panel)

    def init_tabs(self):
        """
        Инициализирует вкладки приложения
        """
        # Вкладка "Поиск"
        search_tab = QWidget()
        search_layout = QVBoxLayout()

        self.init_search_filters(search_layout)

        self.search_results_table = QTableWidget()
        self.search_results_table.setColumnCount(5)
        self.search_results_table.setColumnCount(6)
        self.search_results_table.setHorizontalHeaderLabels(["ID", "Название", "Тип", "Автор", "Статус", "Файл"])
        self.search_results_table.horizontalHeader().setStretchLastSection(True)
        search_layout.addWidget(self.search_results_table)

        search_tab.setLayout(search_layout)
        self.tabs.addTab(search_tab, "Поиск")

        # Вкладка "Регистрация"
        registration_tab = QWidget()
        registration_layout = QVBoxLayout()
        self.init_registration_form(registration_layout)
        registration_tab.setLayout(registration_layout)
        self.tabs.addTab(registration_tab, "Регистрация")

        # Вкладка "Календарь"
        calendar_tab = QWidget()
        calendar_layout = QVBoxLayout()

        self.calendar = QCalendarWidget()
        self.calendar.clicked.connect(self.show_events_on_date)
        calendar_layout.addWidget(self.calendar)

        create_event_button = QPushButton("Создать событие")
        create_event_button.clicked.connect(self.create_event)
        calendar_layout.addWidget(create_event_button)

        calendar_tab.setLayout(calendar_layout)
        self.tabs.addTab(calendar_tab, "Календарь")

        # Вкладка "История действий" для администратора
        if self.user_info["role"] == "admin":
            self.init_action_history_tab()

            # Вкладка "Администрирование" для администратора
            admin_tab = AdminWindow()
            self.tabs.addTab(admin_tab, "Администрирование")

    def init_search_filters(self, layout):
        """
        Добавляет фильтры для поиска документов.
        """
        filters_layout = QVBoxLayout()

        self.my_documents_checkbox = QCheckBox("Мои документы")
        filters_layout.addWidget(self.my_documents_checkbox)

        self.search_status_combobox = QComboBox()
        self.search_status_combobox.addItem("Все")
        self.populate_status_combobox(self.search_status_combobox)

        self.search_type_combobox = QComboBox()
        self.search_type_combobox.addItems(["Все", "Отчёт", "Поручение", "Распоряжение", "Заявление"])

        filters_layout.addWidget(QLabel("Статус документа:"))
        filters_layout.addWidget(self.search_status_combobox)

        filters_layout.addWidget(QLabel("Тип документа:"))
        filters_layout.addWidget(self.search_type_combobox)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Введите ID или название документа")
        filters_layout.addWidget(self.search_input)

        search_button = QPushButton("🔍 Искать")
        search_button.clicked.connect(self.perform_search)
        filters_layout.addWidget(search_button)

        layout.addLayout(filters_layout)

    def perform_search(self):
        """
        Выполняет поиск документов по заданным фильтрам.
        """
        conn = sqlite3.connect("document_management_system.db")
        cursor = conn.cursor()

        query = """
        SELECT Document.Id, Document.Name, Document.Type, 
               Users.LastName || ' ' || Users.FirstName, Status.Name, Document.Name 
        FROM Document
        JOIN Users ON Document.Author = Users.Id
        JOIN Status ON Document.Status = Status.Id WHERE 1=1
        """

        if self.my_documents_checkbox.isChecked():
            query += f"AND Users.Id = {self.user_info['id']} "

        if self.search_status_combobox.currentText() != "Все":
            query += f"AND Status.Name = '{self.search_status_combobox.currentText()}' "

        if self.search_type_combobox.currentText() != "Все":
            query += f"AND Document.Type = '{self.search_type_combobox.currentText()}' "

        if self.search_input.text():
            query += f"AND (Document.Id = ? OR Document.Name LIKE ?) "
            cursor.execute(query, (self.search_input.text(), f"%{self.search_input.text()}%"))
        else:
            cursor.execute(query)

        results = cursor.fetchall()
        self.search_results_table.setRowCount(len(results))
        self.search_results_table.setColumnCount(7)
        self.search_results_table.setHorizontalHeaderLabels(
            ["ID", "Название", "Тип", "Автор", "Статус", "Скачать", "Удалить"])

        for row_idx, row_data in enumerate(results):
            for col_idx, col_data in enumerate(row_data[:-1]):
                self.search_results_table.setItem(row_idx, col_idx, QTableWidgetItem(str(col_data)))

            download_button = QPushButton("Скачать")
            download_button.clicked.connect(lambda _, doc_id=row_data[0]: self.download_file(doc_id))
            self.search_results_table.setCellWidget(row_idx, 5, download_button)

            delete_button = QPushButton("Удалить")
            delete_button.clicked.connect(lambda _, doc_id=row_data[0]: self.delete_file(doc_id))
            self.search_results_table.setCellWidget(row_idx, 6, delete_button)

        conn.close()

        self.log_action(
            "Поиск документов",
            self.search_input.text(),
            f"Пользователь выполнил поиск с фильтром '{self.search_input.text()}'.",
            document_id=None
        )

    def download_file(self, doc_id):
        """
        Скачивает файл документа по указанному ID
        """
        try:
            conn = sqlite3.connect("document_management_system.db")
            cursor = conn.cursor()

            cursor.execute("SELECT Name, Content, FileType FROM Document WHERE Id = ?", (doc_id,))
            result = cursor.fetchone()

            if result:
                file_name, file_content, file_extension = result

                file_name_with_extension = file_name + file_extension

                file_path, _ = QFileDialog.getSaveFileName(self, "Сохранить файл", file_name_with_extension,
                                                           "Все файлы (*.*)")

                if file_path:
                    with open(file_path, "wb") as file:
                        file.write(file_content)
                    QMessageBox.information(self, "Успех", f"Файл {file_name_with_extension} успешно сохранён.")

                    self.log_action(
                        "Скачивание документа",
                        file_name,
                        f"Документ '{file_name}' был скачан.",
                        document_id=doc_id
                    )
            else:
                QMessageBox.warning(self, "Ошибка", "Файл не найден в базе данных.")

            conn.close()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить файл: {str(e)}")

    def delete_file(self, doc_id):
        """
        Удаляет файл документа из базы данных.
        """
        try:
            # Получаем имя файла из базы данных
            conn = sqlite3.connect("document_management_system.db")
            cursor = conn.cursor()
            cursor.execute("SELECT Name FROM Document WHERE Id = ?", (doc_id,))
            result = cursor.fetchone()
            conn.close()

            if result is None:
                QMessageBox.warning(self, "Ошибка", f"Документ с ID {doc_id} не найден.")
                return

            file_name = result[0]  # Имя файла

            confirmation = QMessageBox.question(
                self, "Подтверждение удаления",
                f"Вы уверены, что хотите удалить файл {file_name} с ID {doc_id}?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if confirmation != QMessageBox.StandardButton.Yes:
                return

            conn = sqlite3.connect("document_management_system.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Document WHERE Id = ?", (doc_id,))
            conn.commit()
            conn.close()

            QMessageBox.information(self, "Успех", "Файл успешно удалён.")

            self.log_action(
                "Удаление документа",
                file_name,
                f"Документ '{file_name}' был удалён.",
                document_id=doc_id
            )

            self.perform_search()
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось удалить файл: {e}")

    def init_registration_form(self, layout):
        """
        Создает форму для регистрации нового документа.
        """
        form_layout = QFormLayout()

        # Поле для названия документа
        self.document_name_input = QLineEdit()
        self.document_name_input.setPlaceholderText("Введите название документа")
        form_layout.addRow("Название документа:", self.document_name_input)

        # Имя автора (автоматически)
        author_label = QLabel(
            f'{self.user_info["last_name"]} {self.user_info["first_name"][0]}.{self.user_info["middle_name"][0]}.'
        )
        form_layout.addRow("Автор:", author_label)

        # Дата загрузки (автоматически)
        self.upload_date_label = QLabel(QDateTime.currentDateTime().toString("yyyy-MM-dd"))
        form_layout.addRow("Дата загрузки:", self.upload_date_label)

        # Поле для выбора статуса
        self.registration_status_combobox = QComboBox()
        self.populate_status_combobox(self.registration_status_combobox)
        form_layout.addRow("Статус:", self.registration_status_combobox)

        # Поле для выбора типа документа
        self.type_combobox = QComboBox()
        self.type_combobox.addItems(["Отчёт", "Поручение", "Распоряжение", "Заявление"])
        form_layout.addRow("Тип документа:", self.type_combobox)

        # Поле для загрузки файла
        self.file_upload_button = QPushButton("Загрузить файл")
        self.file_upload_button.clicked.connect(self.upload_file)
        self.file_path_label = QLabel("Файл не выбран")
        file_layout = QHBoxLayout()
        file_layout.addWidget(self.file_upload_button)
        file_layout.addWidget(self.file_path_label)
        form_layout.addRow("Файл:", file_layout)

        layout.addLayout(form_layout)

        # Кнопка для сохранения документа
        save_button = QPushButton("Сохранить документ")
        save_button.clicked.connect(self.save_document)
        layout.addWidget(save_button)

    def upload_file(self):
        """
        Загружает файл документа с компьютера пользователя.
        """
        file_path, _ = QFileDialog.getOpenFileName(self, "Выберите файл документа", "", "Все файлы (*.*)")
        if file_path:
            self.file_path_label.setText(file_path)
            self.file_path = file_path

    def save_document(self):
        """
        Сохраняет информацию о новом документе в базу данных.
        """
        if not self.document_name_input.text():
            QMessageBox.warning(self, "Ошибка", "Введите название документа.")
            return
        if not self.file_path:
            QMessageBox.warning(self, "Ошибка", "Выберите файл для загрузки.")
            return

        try:
            file_name, file_extension = os.path.splitext(self.file_path)
            file_extension = file_extension.lower()

            with open(self.file_path, "rb") as file:
                file_data = file.read()

            conn = sqlite3.connect("document_management_system.db")
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO Document (Name, Type, Author, CreationDate, Content, Status, Version, FileType)
                VALUES (?, ?, ?, DATE('now'), ?, (SELECT Id FROM Status WHERE Name = ?), 1, ?)
                """,
                (
                    self.document_name_input.text(),
                    self.type_combobox.currentText(),
                    self.user_info["id"],
                    file_data,
                    self.registration_status_combobox.currentText(),
                    file_extension
                )
            )
            conn.commit()
            conn.close()
            QMessageBox.information(self, "Успех", "Документ успешно зарегистрирован.")

            self.log_action(
                "Добавление документа",
                self.document_name_input.text(),
                f"Документ '{self.document_name_input.text()}' был добавлен пользователем.",
                document_id=cursor.lastrowid
            )

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при сохранении документа: {str(e)}")

    def populate_status_combobox(self, combobox):
        """
        Заполняет выпадающий список доступными статусами.
        """
        try:
            conn = sqlite3.connect("document_management_system.db")
            cursor = conn.cursor()
            cursor.execute("SELECT Name FROM Status")
            statuses = cursor.fetchall()
            combobox.addItems([status[0] for status in statuses])
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка подключения к базе данных: {e}")
        finally:
            conn.close()

    def show_events_on_date(self, date: QDate):
        """
        Показывает события, связанные с выбранной датой.
        """
        selected_date = date.toString('yyyy-MM-dd')

        events = self.get_events_for_date(selected_date)

        # Показываем диалог с событиями
        events_dialog = EventsDialog(events, selected_date, show_create_button=False)
        events_dialog.exec()

    def get_events_for_date(self, date: str):
        """
        Получает события из базы данных по выбранной дате.
        """
        conn = sqlite3.connect("document_management_system.db")
        cursor = conn.cursor()

        try:
            cursor.execute(
                "SELECT Title, Description, StartTime, EndTime, Color FROM CalendarEvent WHERE EventDate = ?", (date,))
            events = cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            events = []
        finally:
            conn.close()

        return events

    def create_event(self):
        """
        Открывает диалоговое окно для создания нового события.
        """
        event_creation_dialog = EventCreationDialog(self.user_info['id'])
        event_creation_dialog.exec()

        self.log_action(
            "Создание события",
            "Событие",
            f"Пользователь создал новое событие.",
            document_id=None
        )

    def load_action_history(self):
        """
        Загружает историю действий пользователей и отображает в таблице.
        """
        try:
            # Подключение к базе данных
            conn = sqlite3.connect("document_management_system.db")
            cursor = conn.cursor()

            # Выполняем запрос для получения данных из таблицы Action
            cursor.execute('''
                SELECT 
                    Action.Type, 
                    Action.Object, 
                    Action.DateTime, 
                    Users.LastName || ' ' || Users.FirstName
                FROM Action
                JOIN Users ON Action.Users = Users.Id
                ORDER BY Action.DateTime DESC
            ''')
            actions = cursor.fetchall()

            # Очищаем таблицу перед обновлением
            self.history_table.setRowCount(0)

            # Если записей нет, таблица остается пустой
            if not actions:
                return  # Просто завершаем метод, не выводя предупреждений

            # Заполняем таблицу данными
            self.history_table.setRowCount(len(actions))
            for row_idx, action in enumerate(actions):
                for col_idx, col_data in enumerate(action):
                    self.history_table.setItem(row_idx, col_idx, QTableWidgetItem(str(col_data)))

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить историю действий: {e}")
        finally:
            conn.close()

    def log_action(self, action_type, object_name, description="", document_id=None):
        """
        Логирует действия пользователя в базу данных.
        """
        try:
            conn = sqlite3.connect("document_management_system.db")
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO Action (Type, Object, DateTime, Users, Document, Description)
                VALUES (?, ?, datetime('now'), ?, ?, ?)
            ''', (action_type, object_name, self.user_info['id'], document_id, description))
            conn.commit()
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось записать действие: {e}")
        finally:
            conn.close()

    def init_action_history_tab(self):
        """
        Создает вкладку для отображения истории действий.
        """
        # Создаем виджет и layout для вкладки
        history_tab = QWidget()
        history_layout = QVBoxLayout()

        # Кнопка экспорта
        export_button = QPushButton("Экспорт в Excel")
        export_button.clicked.connect(self.export_action_history_to_excel)
        history_layout.addWidget(export_button)

        # Создаем горизонтальный layout для кнопок
        buttons_layout = QHBoxLayout()

        # Кнопка обновления
        update_button = QPushButton("Обновить")
        update_button.clicked.connect(self.load_action_history)
        buttons_layout.addWidget(update_button)

        # Кнопка очистки
        clear_button = QPushButton("Очистить")
        clear_button.clicked.connect(self.clear_action_history)
        buttons_layout.addWidget(clear_button)

        # Добавляем кнопки в основной layout
        history_layout.addLayout(buttons_layout)

        # Создаем таблицу для отображения истории действий
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(4)
        self.history_table.setHorizontalHeaderLabels(["Тип действия", "Объект", "Дата и время", "Пользователь"])
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.history_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        # Добавляем таблицу в layout
        history_layout.addWidget(self.history_table)

        # Устанавливаем layout на вкладку
        history_tab.setLayout(history_layout)

        # Добавляем вкладку в основной интерфейс
        self.tabs.addTab(history_tab, "История действий")

        # Загружаем данные в таблицу при открытии
        self.load_action_history()

    def export_action_history_to_excel(self):
        """
        Экспортирует историю действий в файл Excel.
        """
        try:
            conn = sqlite3.connect("document_management_system.db")
            cursor = conn.cursor()

            # Выполняем запрос для получения данных из таблицы Action
            cursor.execute('''
                SELECT 
                    Action.Type AS "Тип действия", 
                    Action.Object AS "Объект", 
                    Action.DateTime AS "Дата и время", 
                    Users.LastName || ' ' || Users.FirstName AS "Пользователь"
                FROM Action
                JOIN Users ON Action.Users = Users.Id
                ORDER BY Action.DateTime DESC
            ''')
            actions = cursor.fetchall()

            # Проверяем, есть ли данные для экспорта
            if not actions:
                QMessageBox.warning(self, "Экспорт невозможен", "История действий пуста. Нет данных для экспорта.")
                return

            # Заголовки для колонок
            headers = [description[0] for description in cursor.description]

            # Создаем DataFrame из данных
            df = pd.DataFrame(actions, columns=headers)

            # Диалог для выбора имени и пути файла
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Сохранить файл",
                "История_действий.xlsx",
                "Excel Files (*.xlsx)"
            )

            if file_path:
                # Сохраняем данные в файл
                df.to_excel(file_path, index=False)
                QMessageBox.information(self, "Экспорт выполнен",
                                        f"История действий успешно сохранена в файл:\n{file_path}")

            self.log_action(
                "Экспорт истории",
                "История действий",
                f"Пользователь экспортировал историю действий в файл '{file_path}'.",
                document_id=None
            )

            conn.close()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось экспортировать историю действий: {e}")

    def clear_action_history(self):
        """
        Очищает таблицу истории действий.
        """
        confirmation = QMessageBox.question(
            self, "Подтверждение очистки",
            "Вы уверены, что хотите удалить все записи из истории действий?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirmation == QMessageBox.StandardButton.Yes:
            try:
                # Подключение к базе данных
                conn = sqlite3.connect("document_management_system.db")
                cursor = conn.cursor()

                # Удаляем все записи из таблицы Action
                cursor.execute("DELETE FROM Action")
                conn.commit()
                conn.close()

                # Очищаем таблицу в интерфейсе
                self.history_table.setRowCount(0)

                # Логируем очистку истории
                self.log_action(
                    "Очистка истории",
                    "",
                    "Пользователь очистил всю историю действий.",
                    document_id=None
                )

                QMessageBox.information(self, "Успех", "История действий была успешно очищена.")
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось очистить историю действий: {e}")

    def logout(self):
        """
        Выполняет выход пользователя из системы.
        """
        reply = QMessageBox.question(
            self, "Подтверждение выхода", "Вы уверены, что хотите выйти?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.close()

class BaseEventDialog(QDialog):
    """
    Базовый класс для создания и отображения событий.
    """
    def __init__(self, user_id=None, events=None, selected_date=None, show_create_button=True):
        super().__init__()
        self.user_id = user_id
        self.events = events
        self.selected_date = selected_date
        self.show_create_button = show_create_button
        self.selected_color = '#FFFFFF'

    def select_color(self):
        """
        Открывает диалог для выбора цвета.
        """
        color = QColorDialog.getColor()
        if color.isValid():
            self.selected_color = color.name()

    def create_event(self, title_input, description_input, date_input, start_time_input, end_time_input):
        """
        Создает событие в базе данных.
        """
        title = title_input.text()
        description = description_input.text()
        date = date_input.text()
        start_time = start_time_input.text()
        end_time = end_time_input.text()

        conn = sqlite3.connect("document_management_system.db")
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO CalendarEvent (Title, Description, EventDate, StartTime, EndTime, CreatedBy, Color)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (title, description, date, start_time, end_time, self.user_id, self.selected_color))

        conn.commit()
        conn.close()

        self.accept()


class EventCreationDialog(BaseEventDialog):
    """
    Диалоговое окно для создания нового события.
    """
    def __init__(self, user_id):
        super().__init__(user_id=user_id)

        self.setWindowTitle("Создание события")
        self.setGeometry(400, 200, 400, 300)

        self.layout = QFormLayout()

        # Поля ввода
        self.title_input = QLineEdit()
        self.description_input = QLineEdit()
        self.date_input = QLineEdit()
        self.start_time_input = QLineEdit()
        self.end_time_input = QLineEdit()

        # Кнопка выбора цвета
        self.color_picker_button = QPushButton("Выбрать цвет")
        self.color_picker_button.clicked.connect(self.select_color)

        # Добавляем виджеты в форму
        self.layout.addRow("Название:", self.title_input)
        self.layout.addRow("Описание:", self.description_input)
        self.layout.addRow("Дата (yyyy-mm-dd):", self.date_input)
        self.layout.addRow("Время начала (hh:mm):", self.start_time_input)
        self.layout.addRow("Время окончания (hh:mm):", self.end_time_input)
        self.layout.addRow("", self.color_picker_button)

        self.create_button = QPushButton("Создать")
        self.create_button.clicked.connect(lambda: self.create_event(self.title_input, self.description_input,
                                                                     self.date_input, self.start_time_input, self.end_time_input))
        self.layout.addRow("", self.create_button)

        self.setLayout(self.layout)


class EventsDialog(BaseEventDialog):
    """
    Диалоговое окно для отображения списка событий на выбранную дату.
    """
    def __init__(self, events, selected_date, show_create_button=True):
        super().__init__(events=events, selected_date=selected_date, show_create_button=show_create_button)

        self.setWindowTitle(f"События на {selected_date}")
        self.setGeometry(400, 200, 600, 400)

        self.layout = QVBoxLayout()

        self.events_table = QTableWidget()
        self.events_table.setColumnCount(4)
        self.events_table.setHorizontalHeaderLabels(["Название", "Описание", "Время начала", "Время окончания"])

        self.events_table.setRowCount(len(events))
        for row_idx, event in enumerate(events):
            row_color = event[4]
            for col_idx, col_data in enumerate(event[:-1]):
                item = QTableWidgetItem(str(col_data))
                self.events_table.setItem(row_idx, col_idx, item)

            for col_idx in range(4):
                self.events_table.item(row_idx, col_idx).setBackground(QColor(row_color))

        self.events_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.events_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self.layout.addWidget(self.events_table)

        if show_create_button:
            self.create_event_button = QPushButton("Создать новое событие")
            self.create_event_button.clicked.connect(lambda: self.create_event(self.title_input, self.description_input,
                                                                             self.date_input, self.start_time_input, self.end_time_input))
            self.layout.addWidget(self.create_event_button)

        self.setLayout(self.layout)


if __name__ == "__main__":
    user_info_example = {
        "id": 1,
        "first_name": "Арина",
        "last_name": "Петрухина",
        "middle_name": "Александровна",
        "role": "admin",
    }

    app = QApplication(sys.argv)
    window = MainWindow(user_info_example)
    window.show()
    sys.exit(app.exec())