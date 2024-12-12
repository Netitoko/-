import sqlite3

def convert_to_blob(file_path):
    try:
        with open(file_path, 'rb') as file:
            blob_data = file.read()
        return blob_data
    except FileNotFoundError:
        print(f"Файл {file_path} не найден.")
        return None

conn = sqlite3.connect('document_management_system.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS Role (
    Id INTEGER PRIMARY KEY AUTOINCREMENT,
    Name TEXT NOT NULL,
    AccessRights TEXT
);
''')

cursor.execute("SELECT COUNT(*) FROM Role")
if cursor.fetchone()[0] == 0:
    cursor.execute('''
    INSERT INTO Role (Name, AccessRights) VALUES
        ('admin', 'полный доступ'),
        ('user', 'ограниченный доступ');
    ''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS Status (
    Id INTEGER PRIMARY KEY AUTOINCREMENT,
    Name TEXT NOT NULL,
    Description TEXT
);   
''')

cursor.execute("SELECT COUNT(*) FROM Status")
if cursor.fetchone()[0] == 0:
    cursor.execute('''
    INSERT INTO Status (Name, Description) VALUES
        ('Создан', 'Документ был создан и ожидает обработки.'),
        ('На рассмотрении', 'Документ находится на рассмотрении у ответственного лица.'),
        ('Согласован', 'Документ согласован всеми необходимыми сторонами.'),
        ('Отклонен', 'Документ был отклонен и требует доработки.'),
        ('Выполнен', 'Документ выполнен и закрыт.'),
        ('Архивирован', 'Документ завершен и перемещен в архив.'),
        ('Удален', 'Документ был удален из системы.');
    ''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS Users (
    Id INTEGER PRIMARY KEY AUTOINCREMENT,
    Login TEXT NOT NULL UNIQUE,
    Password TEXT NOT NULL,
    FirstName TEXT NOT NULL,
    LastName TEXT NOT NULL,
    MiddleName TEXT,
    Role INTEGER NOT NULL,
    Phone_number TEXT NOT NULL UNIQUE,
    Email TEXT,
    FOREIGN KEY (Role) REFERENCES Role(Id)
);
''')

cursor.execute("SELECT COUNT(*) FROM Users")
if cursor.fetchone()[0] == 0:
    cursor.execute('''
    INSERT INTO Users (Login, Password, FirstName, LastName, MiddleName, Role, Phone_number, Email) VALUES
        ('Netitoko', 'XzFt3AKA!', 'Арина', 'Петрухина', 'Александровна', 1, '89873455592', 'netito8642@gmail.com'),
        ('Matvey_01', 'XzFt3AKA!', 'Матвей', 'Петрухин', 'Александрович', 2, '89876200293', 'pma8642@gmail.com'),
        ('A_Irina', 'XzFt3AKA!', 'Ирина', 'Алхимова', 'Сергеевна', 2, '89177588880', 'irina_8642@mail.ru');
    ''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS Document (
    Id INTEGER PRIMARY KEY AUTOINCREMENT,
    Name TEXT NOT NULL,
    Type TEXT,
    Author INTEGER NOT NULL,
    CreationDate DATE NOT NULL,
    Content BLOB,
    Status INTEGER NOT NULL,
    Version INTEGER,
    FileType TEXT,
    FOREIGN KEY (Author) REFERENCES Users(Id),
    FOREIGN KEY (Status) REFERENCES Status(Id)
);
''')

cursor.execute("SELECT COUNT(*) FROM Document")
if cursor.fetchone()[0] == 0:
    cursor.execute('''
    INSERT INTO Document (Name, Type, Author, CreationDate, Content, Status, Version, FileType) VALUES
        ('Документ 1', 'Поручение', 1, '2024-12-01', NULL, 1, 1, '.docx'),
        ('Документ 2', 'Отчет', 1, '2024-12-05', NULL, 2, 1, '.pdf'),
        ('Документ 3', 'Заявление', 3, '2024-12-05', NULL, 3, 1, '.zip'),
        ('Документ 4', 'Отчет', 3, '2024-12-15', NULL, 4, 1, '.pdf'),
        ('Документ 5', 'Распоряжение', 2, '2024-12-10', NULL, 5, 1, '.pdf');
    ''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS Action (
    Id INTEGER PRIMARY KEY AUTOINCREMENT,
    Type TEXT NOT NULL,
    Object TEXT,
    Document INTEGER,
    Users INTEGER NOT NULL,
    DateTime DATETIME NOT NULL,
    Description TEXT,
    FOREIGN KEY (Document) REFERENCES Document(Id),
    FOREIGN KEY (Users) REFERENCES Users(Id)
);
''')

cursor.execute("SELECT COUNT(*) FROM Action")
if cursor.fetchone()[0] == 0:
    cursor.execute('''
    INSERT INTO Action (Type, Object, Document, Users, DateTime, Description) VALUES
        ('Поиск документов', '', 1, 1, '2024-12-01 10:00:00', 'Поиск документов'),
        ('Поиск документов', '5', 2, 1, '2024-12-05 14:00:00', 'Поиск документов'),
        ('Удаление', 'Документ 5', 3, 2, '2024-12-10 09:00:00', 'Удален документ');
    ''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS CalendarEvent (
    Id INTEGER PRIMARY KEY AUTOINCREMENT,
    Title TEXT NOT NULL,
    Description TEXT,
    EventDate DATE NOT NULL,
    StartTime TIME NOT NULL,
    EndTime TIME NOT NULL,
    CreatedBy INTEGER NOT NULL,
    Color TEXT,
    FOREIGN KEY (CreatedBy) REFERENCES Users(Id)
);
''')

cursor.execute("SELECT COUNT(*) FROM CalendarEvent")
if cursor.fetchone()[0] == 0:
    cursor.execute('''
        INSERT INTO CalendarEvent (Title, Description, EventDate, StartTime, EndTime, CreatedBy, Color)
        VALUES
            ('Совещание по проекту', 'Обсуждение деталей нового проекта', '2024-12-01', '10:00', '12:00', 1, '#FF5733'),
            ('Собрание команды', 'Командное собрание для обсуждения планов', '2024-12-03', '14:00', '16:00', 1, '#33FF57'),
            ('Презентация нового продукта', 'Презентация для руководства', '2024-12-05', '09:00', '11:00', 1, '#5733FF'),
            ('Открытие нового офиса', 'Открытие нового офисного здания', '2024-12-10', '18:00', '20:00', 2, '#FF33A1');
        ''')

conn.commit()
conn.close()

print("База данных и таблицы успешно созданы!")