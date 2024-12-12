import sqlite3
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import re
from main_window import *
from Create_BD import *


if not os.path.exists("document_management_system.db"):
    print("База данных не найдена. Создаём новую...")
    conn = sqlite3.connect("document_management_system.db")
    conn.close()

class AuthWindow(QWidget):
    """
    Класс для отображения окна авторизации.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Авторизация")
        self.setGeometry(500, 300, 300, 200)

        layout = QVBoxLayout()

        self.login_label = QLabel("Логин")
        self.login_input = QLineEdit()

        self.password_label = QLabel("Пароль")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.login_button = QPushButton("Войти")
        self.register_button = QPushButton("Регистрация")

        self.login_button.clicked.connect(self.login)
        self.register_button.clicked.connect(self.open_registration)

        layout.addWidget(self.login_label)
        layout.addWidget(self.login_input)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_button)
        layout.addWidget(self.register_button)

        self.setLayout(layout)

    def login(self):
        """
         Выполняет проверку введенного логина и пароля,
         и при успешной авторизации открывает главное окно.
        """
        login = self.login_input.text()
        password = self.password_input.text()

        with sqlite3.connect("document_management_system.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Users WHERE Login=? AND Password=?", (login, password))
            user = cursor.fetchone()

            if user:
                QMessageBox.information(self, "Успешно", "Добро пожаловать!")

                user_info = {
                    "id": user[0],
                    "login": user[1],
                    "first_name": user[3],
                    "last_name": user[4],
                    "middle_name": user[5],
                    "role": 'admin' if user[6] == 1 else 'user',
                }

                self.open_main_window(user_info)

            else:
                QMessageBox.warning(self, "Ошибка", "Неверный логин или пароль.")

    def open_main_window(self, user_info):
        """
        Создает и открывает главное окно приложения, передавая информацию о пользователе.
        """
        self.main_window = MainWindow(user_info)
        self.main_window.show()
        self.close()

    def open_registration(self):
        """
        Открывает окно регистрации.
        """
        self.registration_window = RegistrationWindow()
        self.registration_window.show()


class RegistrationWindow(QDialog):
    """
    Класс для отображения окна регистрации нового пользователя.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Регистрация")
        self.setGeometry(500, 300, 400, 500)

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

        self.register_button = QPushButton("Зарегистрироваться")
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
        layout.addWidget(self.register_button)

        self.setLayout(layout)

    def validate_login(self, login):
        """
        Проверяет корректность логина
        """
        pattern = r"^[a-zA-Z0-9_]+$"
        return bool(re.fullmatch(pattern, login))

    def validate_password(self, password):
        """
        Проверяет корректность пароля
        """
        if len(password) < 6:
            return False
        if not re.search(r"[A-Z]", password) or not re.search(r"[a-z]", password):
            return False
        if not re.search(r"[0-9]", password):
            return False
        if not re.search(r"[!._,:;]", password):
            return False
        return True

    def register_user(self):
        """
        Выполняет регистрацию пользователя
        """
        login = self.login_input.text()
        email = self.email_input.text()
        phone = self.phone_input.text().replace("+7", "8")
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()

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
                     self.middle_name_input.text(), 2, phone, email)  # Роль "User"
                )
                conn.commit()
                QMessageBox.information(self, "Успешно", "Регистрация завершена.")
                self.accept()
            else:
                QMessageBox.warning(self, "Ошибка", "Регистрация отменена. Неверный код подтверждения.")

    def send_confirmation_email(self, email, code):
        """
        Отправляет на email код подтверждения для завершения регистрации.
        """
        sender_email = "document0management0system0@gmail.com"
        app_password = "ohhh ffff ffff ffff"  # изменен пароль в целях безопасности
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
    Класс для отображения диалогового окна проверки кода подтверждения.
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
        Проверяет введенный код подтверждения и завершает регистрацию при успехе.
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


app = QApplication(sys.argv)
auth_window = AuthWindow()
auth_window.show()
sys.exit(app.exec())