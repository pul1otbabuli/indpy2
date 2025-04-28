CREATE TABLE Cases (
    case_id INTEGER PRIMARY KEY AUTOINCREMENT,
    case_number TEXT UNIQUE NOT NULL,
    opening_date DATE NOT NULL,
    description TEXT
);

CREATE TABLE Parties (
    party_id INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    role TEXT NOT NULL,
    contact_info TEXT,
    FOREIGN KEY (case_id) REFERENCES Cases(case_id)
);

CREATE TABLE Judges (
    judge_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    qualification TEXT
);

CREATE TABLE CaseJudges (
    case_id INTEGER NOT NULL,
    judge_id INTEGER NOT NULL,
    PRIMARY KEY (case_id, judge_id),
    FOREIGN KEY (case_id) REFERENCES Cases(case_id),
    FOREIGN KEY (judge_id) REFERENCES Judges(judge_id)
);

INSERT INTO Cases (case_number, opening_date, description) VALUES
('Д123-2023', '2023-05-10', 'Дело о разделе имущества'),
('Г456-2024', '2024-01-15', 'Иск о защите прав потребителей'),
('У789-2025', '2025-03-20', 'Уголовное дело по статье 158 УК');

INSERT INTO Parties (case_id, name, role, contact_info) VALUES
(1, 'Иванов И.И.', 'Истец', 'ivanov@example.com'),
(1, 'Петрова А.А.', 'Ответчик', 'petrova@example.com'),
(2, 'ООО "Рога и Копыта"', 'Истец', 'info@rogakopyta.ru'),
(2, 'Сидоров Б.В.', 'Ответчик', 'sidorov@example.com'),
(3, 'Смирнов В.Г.', 'Обвиняемый', 'smirnov@example.com');

INSERT INTO Judges (name, qualification) VALUES
('Степанова Е.П.', 'Судья первой инстанции'),
('Кузнецов О.С.', 'Председатель судебной коллегии'),
('Морозова И.А.', 'Судья высшей квалификации');

-- Заполнение связующей таблицы "Дела и Судьи"
INSERT INTO CaseJudges (case_id, judge_id) VALUES
(1, 1),
(1, 2),
(2, 2),
(3, 3);
