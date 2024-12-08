import sqlite3
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import re
from PyQt6.QtWidgets import (
    QVBoxLayout, QLabel, QPushButton,
    QWidget, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QMessageBox, QCheckBox, QComboBox, QLineEdit, QDialog,
    QFormLayout,
)


class AdminWindow(QWidget):
    """
    Интерфейс администратора для управления пользователями и ролями.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Управление пользователями")
        self.resize(800, 600)
        self.init_ui()

    def init_ui(self):
        """
        Создает элементы управления пользователями.
        """
        layout = QVBoxLayout()

        # Кнопка для управления ролями
        self.roles_button = QPushButton("Роли")
        self.roles_button.clicked.connect(self.open_roles_dialog)
        layout.addWidget(self.roles_button)

        # Кнопка для добавления нового пользователя
        self.add_user_button = QPushButton("Создать нового пользователя")
        self.add_user_button.clicked.connect(self.open_create_user_dialog)
        layout.addWidget(self.add_user_button)

        # Кнопка настройки выбранного пользователя (показывается только при выборе одного пользователя)
        self.settings_button = QPushButton("Настройки")
        self.settings_button.setEnabled(False)  # Изначально кнопка отключена
        self.settings_button.clicked.connect(self.open_user_settings_dialog)

        # Кнопка удаления выбранных пользователей (показывается при выборе одного или нескольких пользователей)
        self.delete_button = QPushButton("Удалить")
        self.delete_button.setEnabled(False)  # Изначально кнопка отключена
        self.delete_button.clicked.connect(self.delete_users)

        # Панель для кнопок настройки и удаления
        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.settings_button)
        buttons_layout.addWidget(self.delete_button)
        layout.addLayout(buttons_layout)

        # Список пользователей
        self.users_table = QTableWidget()
        self.users_table.setColumnCount(7)
        self.users_table.setHorizontalHeaderLabels(
            ["Выбрать", "ID", "Фамилия И.О.", "Логин", "Почта", "Телефон", "Роль"]
        )
        self.load_users()

        layout.addWidget(self.users_table)
        self.setLayout(layout)

    def load_users(self):
        """
        Загружает пользователей и их роли из базы данных и отображает их в таблице.
        """
        conn = sqlite3.connect("document_management_system.db")
        cursor = conn.cursor()

        # Выполняем JOIN между таблицами Users и Role, чтобы получить имя роли
        query = """
            SELECT Users.Id, Users.LastName, Users.FirstName, Users.MiddleName, Users.Login, 
                   Users.Email, Users.Phone_number, Role.Name
            FROM Users
            JOIN Role ON Users.Role = Role.Id
        """
        cursor.execute(query)
        users = cursor.fetchall()
        conn.close()

        # Очищаем таблицу перед обновлением
        self.users_table.clearContents()
        self.users_table.setRowCount(len(users))

        # Заполняем таблицу данными
        for row_idx, user in enumerate(users):
            self.users_table.setItem(row_idx, 1, QTableWidgetItem(str(user[0])))
            self.users_table.setItem(row_idx, 2, QTableWidgetItem(f"{user[1]} {user[2][0]}. {user[3][0]}."))
            self.users_table.setItem(row_idx, 3, QTableWidgetItem(user[4]))  # Логин
            self.users_table.setItem(row_idx, 4, QTableWidgetItem(user[5]))  # Почта
            self.users_table.setItem(row_idx, 5, QTableWidgetItem(user[6]))  # Телефон
            self.users_table.setItem(row_idx, 6, QTableWidgetItem(user[7]))  # Роль (имя роли)

            # Чекбокс для выбора пользователя
            select_checkbox = QCheckBox()
            select_checkbox.stateChanged.connect(self.update_buttons_state)
            self.users_table.setCellWidget(row_idx, 0, select_checkbox)

    def update_buttons_state(self):
        """
        Обновляет состояние кнопок в зависимости от выбора пользователей.
        """
        selected_rows = self.get_selected_rows()

        # Если выбран один пользователь, показываем кнопку настройки
        if len(selected_rows) == 1:
            self.settings_button.setEnabled(True)
        else:
            self.settings_button.setEnabled(False)

        # Если выбран хотя бы один пользователь, показываем кнопку удаления
        if len(selected_rows) > 0:
            self.delete_button.setEnabled(True)
        else:
            self.delete_button.setEnabled(False)

    def get_selected_rows(self):
        """
        Возвращает список индексов строк с выбранными пользователями.
        """
        selected_rows = []
        for row_idx in range(self.users_table.rowCount()):
            checkbox = self.users_table.cellWidget(row_idx, 0)
            if checkbox.isChecked():
                selected_rows.append(row_idx)
        return selected_rows

    def open_user_settings_dialog(self):
        """
        Открывает диалоговое окно для настройки роли выбранного пользователя.
        """
        selected_rows = self.get_selected_rows()

        if len(selected_rows) == 1:
            user_id = int(self.users_table.item(selected_rows[0], 1).text())
            current_role = self.users_table.item(selected_rows[0], 6).text()

            dialog = EditRoleDialog(user_id, current_role)
            if dialog.exec():
                self.load_users()

    def delete_users(self):
        """
        Удаляет выбранных пользователей.
        """
        selected_rows = self.get_selected_rows()

        if not selected_rows:
            return

        confirmation = QMessageBox.question(
            self, "Подтверждение удаления",
            f"Вы уверены, что хотите удалить {len(selected_rows)} пользователей?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirmation == QMessageBox.StandardButton.Yes:
            conn = sqlite3.connect("document_management_system.db")
            cursor = conn.cursor()

            for row_idx in selected_rows:
                user_id = self.users_table.item(row_idx, 1).text()
                try:
                    cursor.execute("DELETE FROM Users WHERE Id = ?", (user_id,))
                    conn.commit()

                    self.log_action(
                        "Удаление пользователя",
                        f"Пользователь ID {user_id}",
                        f"Пользователь с ID {user_id} был удален.",
                        document_id=user_id
                    )

                except sqlite3.Error as e:
                    QMessageBox.critical(self, "Ошибка базы данных", f"Ошибка при удалении пользователя с ID {user_id}: {e}")

            conn.close()
            self.load_users()

    def open_create_user_dialog(self):
        """
        Открывает диалоговое окно для создания нового пользователя.
        """
        dialog = CreateUserDialog()
        dialog.exec()  # Открытие диалогового окна для регистрации нового пользователя

    def open_roles_dialog(self):
        """
        Открывает диалог для управления ролями.
        """
        dialog = ManageRolesDialog()
        dialog.exec()

class CreateUserDialog(QDialog):
    """
    Диалоговое окно для создания нового пользователя.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Создание нового пользователя")
        self.setGeometry(500, 300, 400, 550)

        layout = QVBoxLayout()

        # Поля ввода для регистрации
        self.first_name_label = QLabel("Имя")
        self.first_name_input = QLineEdit()

        self.last_name_label = QLabel("Фамилия")
        self.last_name_input = QLineEdit()

        self.middle_name_label = QLabel("Отчество")
        self.middle_name_input = QLineEdit()

        self.login_label = QLabel("Логин")
        self.login_input = QLineEdit()
        self.login_requirements = QLabel("Логин: только латиница, цифры и '_'.")
        self.login_requirements.setStyleSheet("color: gray; font-size: 10pt;")

        self.email_label = QLabel("Email")
        self.email_input = QLineEdit()

        self.phone_label = QLabel("Телефон")
        self.phone_input = QLineEdit()

        self.password_label = QLabel("Пароль")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_requirements = QLabel("Пароль: мин. 6 символов, латиница, цифры и символы: !._,:;")
        self.password_requirements.setStyleSheet("color: gray; font-size: 10pt;")

        self.confirm_password_label = QLabel("Подтвердите пароль")
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.role_label = QLabel("Роль")
        self.role_input = QComboBox()
        self.load_roles()

        self.register_button = QPushButton("Зарегистрировать")
        self.register_button.clicked.connect(self.register_user)

        # Добавление всех виджетов в layout
        layout.addWidget(self.first_name_label)
        layout.addWidget(self.first_name_input)
        layout.addWidget(self.last_name_label)
        layout.addWidget(self.last_name_input)
        layout.addWidget(self.middle_name_label)
        layout.addWidget(self.middle_name_input)
        layout.addWidget(self.login_label)
        layout.addWidget(self.login_input)
        layout.addWidget(self.login_requirements)
        layout.addWidget(self.email_label)
        layout.addWidget(self.email_input)
        layout.addWidget(self.phone_label)
        layout.addWidget(self.phone_input)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.password_requirements)
        layout.addWidget(self.confirm_password_label)
        layout.addWidget(self.confirm_password_input)
        layout.addWidget(self.role_label)
        layout.addWidget(self.role_input)
        layout.addWidget(self.register_button)

        self.setLayout(layout)

    def validate_login(self, login):
        pattern = r"^[a-zA-Z0-9_]+$"
        return bool(re.fullmatch(pattern, login))

    def validate_password(self, password):
        if len(password) < 6:
            return False
        if not re.search(r"[A-Z]", password) or not re.search(r"[a-z]", password):
            return False
        if not re.search(r"[0-9]", password):
            return False
        if not re.search(r"[!._,:;]", password):
            return False
        return True

    def load_roles(self):
        """
        Загружает роли из базы данных и добавляет их в выпадающий список.
        """
        conn = sqlite3.connect("document_management_system.db")
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT Id, Name FROM Role")
            roles = cursor.fetchall()
            self.role_input.clear()
            for role_id, role_name in roles:
                self.role_input.addItem(role_name, role_id)  # Отображаем название, а ID храним как данные элемента
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Ошибка базы данных", f"Не удалось загрузить роли: {e}")
        finally:
            conn.close()

    def register_user(self):
        """
        Выполняет регистрацию нового пользователя.
        """
        login = self.login_input.text()
        email = self.email_input.text()
        phone = self.phone_input.text().replace("+7", "8")
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()
        role_id = self.role_input.currentData()  # Получаем ID выбранной роли

        if not self.validate_login(login):
            QMessageBox.warning(self, "Ошибка", "Логин должен содержать только буквы (a-z, A-Z), цифры и '_'.")
            return

        if not self.validate_password(password):
            QMessageBox.warning(
                self, "Ошибка",
                "Пароль должен содержать минимум 6 символов, включать заглавные и строчные буквы, цифры и один из символов !._,:;."
            )
            return

        if password != confirm_password:
            QMessageBox.warning(self, "Ошибка", "Пароли не совпадают.")
            return

        with sqlite3.connect("document_management_system.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Users WHERE Email=? OR Phone_number=?", (email, phone))
            if cursor.fetchone():
                QMessageBox.warning(self, "Ошибка", "Email или телефон уже используются.")
                return

            confirmation_code = str(random.randint(100000, 999999))
            self.send_confirmation_email(email, confirmation_code)

            code_verification_dialog = CodeVerificationDialog(confirmation_code)
            if code_verification_dialog.exec() == QDialog.DialogCode.Accepted:
                cursor.execute(
                    "INSERT INTO Users (Login, Password, FirstName, LastName, MiddleName, Role, Phone_number, Email) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (login, password, self.first_name_input.text(), self.last_name_input.text(),
                     self.middle_name_input.text(), role_id, phone, email)
                )
                conn.commit()
                QMessageBox.information(self, "Успешно", "Регистрация завершена.")
                self.accept()
            else:
                QMessageBox.warning(self, "Ошибка", "Регистрация отменена. Неверный код подтверждения.")

    def send_confirmation_email(self, email, code):
        """
        Отправляет код подтверждения на электронную почту пользователя.
        """
        sender_email = "document0management0system0@gmail.com"
        app_password = "ohhh ffff ffff ffff" #изменен пароль в целях безопасности
        smtp_server = "smtp.gmail.com"
        smtp_port = 465

        subject = "Код подтверждения регистрации"
        message = f"Ваш код подтверждения: {code}"

        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = email
        msg["Subject"] = subject
        msg.attach(MIMEText(message, "plain"))

        try:
            with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
                server.login(sender_email, app_password)
                server.sendmail(sender_email, email, msg.as_string())
            QMessageBox.information(self, "Успешно", "Код подтверждения отправлен на вашу почту.")
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось отправить письмо: {e}")


class CodeVerificationDialog(QDialog):
    """
    Диалоговое окно для ввода и проверки кода подтверждения.
    """
    def __init__(self, confirmation_code):
        super().__init__()
        self.setWindowTitle("Подтверждение почты")
        self.setGeometry(500, 300, 300, 150)
        self.confirmation_code = confirmation_code
        self.attempts = 2

        layout = QVBoxLayout()
        self.label = QLabel("Введите код подтверждения, отправленный на почту:")
        self.code_input = QLineEdit()
        self.verify_button = QPushButton("Подтвердить")
        self.verify_button.clicked.connect(self.verify_code)

        layout.addWidget(self.label)
        layout.addWidget(self.code_input)
        layout.addWidget(self.verify_button)
        self.setLayout(layout)

    def verify_code(self):
        """
        Проверяет введенный код подтверждения.
        """
        entered_code = self.code_input.text()
        if entered_code == self.confirmation_code:
            self.accept()
        else:
            self.attempts -= 1
            if self.attempts > 0:
                QMessageBox.warning(self, "Ошибка", f"Неверный код. У вас осталось {self.attempts} попыток.")
            else:
                QMessageBox.warning(self, "Ошибка", "Неверный код. Попытки исчерпаны.")
                self.reject()


class EditRoleDialog(QDialog):
    """
    Диалоговое окно для редактирования роли пользователя.
    """
    def __init__(self, user_id, current_role):
        super().__init__()
        self.user_id = user_id
        self.current_role = current_role

        self.setWindowTitle("Изменение роли пользователя")
        self.setFixedSize(300, 150)
        self.init_ui()

    def init_ui(self):
        layout = QFormLayout()

        # Выпадающий список для выбора роли
        self.role_combobox = QComboBox()
        self.load_roles()  # Загружаем роли из базы данных
        self.role_combobox.setCurrentText(self.current_role)

        # Кнопка сохранения
        save_button = QPushButton("Сохранить")
        save_button.clicked.connect(self.save_role)

        layout.addRow("Роль:", self.role_combobox)
        layout.addWidget(save_button)

        self.setLayout(layout)

    def load_roles(self):
        """
        Загружает роли из базы данных и добавляет их в выпадающий список.
        """
        conn = sqlite3.connect("document_management_system.db")
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT Id, Name FROM Role")
            roles = cursor.fetchall()
            for role in roles:
                self.role_combobox.addItem(role[1], role[0])  # Добавляем текст роли и ее ID
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Ошибка базы данных", f"Не удалось загрузить роли: {e}")
        finally:
            conn.close()

    def save_role(self):
        """
        Сохраняет новую роль в базе данных, используя ID роли.
        """
        new_role_id = self.role_combobox.currentData()  # Получаем ID выбранной роли
        if new_role_id == self.current_role:
            QMessageBox.information(self, "Изменение роли", "Роль не изменилась.")
            return

        try:
            conn = sqlite3.connect("document_management_system.db")
            cursor = conn.cursor()
            cursor.execute("UPDATE Users SET Role = ? WHERE Id = ?", (new_role_id, self.user_id))
            conn.commit()
            conn.close()
            QMessageBox.information(self, "Изменение роли", "Роль успешно обновлена.")

            self.accept()  # Закрыть окно после сохранения
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Ошибка базы данных", f"Произошла ошибка при изменении роли: {e}")

class ManageRolesDialog(QDialog):
    """
    Диалоговое окно для управления ролями.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Управление ролями")
        self.setGeometry(500, 300, 400, 300)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Таблица для отображения ролей
        self.roles_table = QTableWidget()
        self.roles_table.setColumnCount(3)
        self.roles_table.setHorizontalHeaderLabels(["ID", "Название", "Права доступа"])
        self.load_roles()
        layout.addWidget(self.roles_table)

        # Кнопки для управления ролями
        buttons_layout = QHBoxLayout()

        add_button = QPushButton("Добавить")
        add_button.clicked.connect(self.add_role)
        buttons_layout.addWidget(add_button)

        edit_button = QPushButton("Изменить")
        edit_button.clicked.connect(self.edit_role)
        buttons_layout.addWidget(edit_button)

        delete_button = QPushButton("Удалить")
        delete_button.clicked.connect(self.delete_role)
        buttons_layout.addWidget(delete_button)

        layout.addLayout(buttons_layout)
        self.setLayout(layout)

    def load_roles(self):
        """
        Загружает роли из базы данных и отображает их в таблице.
        """
        conn = sqlite3.connect("document_management_system.db")
        cursor = conn.cursor()
        cursor.execute("SELECT Id, Name, AccessRights FROM Role")
        roles = cursor.fetchall()
        conn.close()

        self.roles_table.setRowCount(len(roles))
        for row_idx, role in enumerate(roles):
            for col_idx, col_data in enumerate(role):
                self.roles_table.setItem(row_idx, col_idx, QTableWidgetItem(str(col_data)))

    def add_role(self):
        """
        Добавление новой роли.
        """
        dialog = RoleDialog()
        if dialog.exec():
            self.load_roles()

    def edit_role(self):
        """
        Изменение выбранной роли.
        """
        selected_row = self.roles_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите роль для редактирования.")
            return
        role_id = int(self.roles_table.item(selected_row, 0).text())
        role_name = self.roles_table.item(selected_row, 1).text()
        access_rights = self.roles_table.item(selected_row, 2).text()

        dialog = RoleDialog(role_id, role_name, access_rights)
        if dialog.exec():
            self.load_roles()

    def delete_role(self):
        """
        Удаление выбранной роли.
        """
        selected_row = self.roles_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите роль для удаления.")
            return
        role_id = int(self.roles_table.item(selected_row, 0).text())

        confirmation = QMessageBox.question(
            self, "Подтверждение удаления",
            "Вы уверены, что хотите удалить эту роль?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirmation == QMessageBox.StandardButton.Yes:
            conn = sqlite3.connect("document_management_system.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Role WHERE Id = ?", (role_id,))
            conn.commit()
            conn.close()
            self.load_roles()

class RoleDialog(QDialog):
    """
    Диалоговое окно для добавления или редактирования роли.
    """
    def __init__(self, role_id=None, role_name="", access_rights=""):
        super().__init__()
        self.role_id = role_id
        self.setWindowTitle("Добавление роли" if role_id is None else "Редактирование роли")
        self.setFixedSize(300, 200)
        self.init_ui(role_name, access_rights)

    def init_ui(self, role_name, access_rights):
        layout = QFormLayout()

        self.name_input = QLineEdit(role_name)
        self.access_input = QLineEdit(access_rights)

        save_button = QPushButton("Сохранить")
        save_button.clicked.connect(self.save_role)

        layout.addRow("Название:", self.name_input)
        layout.addRow("Права доступа:", self.access_input)
        layout.addWidget(save_button)

        self.setLayout(layout)

    def save_role(self):
        """
        Сохраняет роль в базе данных (добавляет новую или обновляет существующую).
        """
        name = self.name_input.text()
        access_rights = self.access_input.text()

        conn = sqlite3.connect("document_management_system.db")
        cursor = conn.cursor()
        if self.role_id is None:
            cursor.execute("INSERT INTO Role (Name, AccessRights) VALUES (?, ?)", (name, access_rights))
        else:
            cursor.execute("UPDATE Role SET Name = ?, AccessRights = ? WHERE Id = ?", (name, access_rights, self.role_id))
        conn.commit()
        conn.close()
        self.accept()
