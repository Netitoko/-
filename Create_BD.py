import sqlite3


conn = sqlite3.connect('document_management_system.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS Role (
    Id INTEGER PRIMARY KEY AUTOINCREMENT,
    Name TEXT NOT NULL,
    AccessRights TEXT
);
''')

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

cursor.execute('''
INSERT INTO Users (Login, Password, FirstName, LastName, MiddleName, Role, Phone_number, Email) VALUES
    ('Netitoko', 'XzFt3AKA!', 'Арина', 'Петрухина', 'Александровна', 1, '89853450293', 'netitokoo@gmail.com'),
    ('Matvey_01', 'XzFt3AKA!', 'Матвей', 'Петрухин', 'Александрович', 2, '+79856208880', 'pma25122015@gmail.com'),
    ('A_IrinaSergeevna', 'XzFt3AKA!', 'Ирина', 'Алхимова', 'Сергеевна', 2, '+79167585592', 'irina_alhimova@mail.ru');
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

cursor.execute('''
INSERT INTO Document (Name, Type, Author, CreationDate, Content, Status, Version, FileType) VALUES
    ('Документ 1', 'Отчёт', 1, '2024-12-09', '', 1, 1, '.docx');
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

cursor.execute('''
INSERT INTO Action (Type, Object, Document, Users, DateTime, Description) VALUES
    ('Поиск документов', '', '', 1, '2024-12-09 08:34:14', 'Пользователь выполнил поиск с фильтром'),
    ('Добавление документа', 'Документ 1', 2, 1, '2024-12-09 08:39:42', "'Документ 1' был добавлен пользователем."); 
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

cursor.execute('''
INSERT INTO CalendarEvent (Title, Description, EventDate, StartTime, EndTime, CreatedBy, Color)
VALUES
    ('Совещание по проекту', 'Обсуждение деталей нового проекта', '2024-11-01', '10:00', '12:00', 1, '#FF5733'),
    ('Собрание команды', 'Командное собрание для обсуждения планов', '2024-11-03', '14:00', '16:00', 1, '#33FF57'),
    ('Презентация нового продукта', 'Презентация для руководства', '2024-11-05', '09:00', '11:00', 1, '#5733FF'),
    ('Открытие нового офиса', 'Открытие нового офисного здания', '2024-11-10', '18:00', '20:00', 2, '#FF33A1');
''')

conn.commit()
conn.close()

print("База данных и таблицы успешно созданы!")