-- Cơ sở dữ liệu - Lucenda (Nhóm 4)

-- I. Tạo cơ sở dữ liệu
CREATE DATABASE lucenda_database;
USE lucenda_database

-- II. Tạo bảng các dữ liệu
-- II.1 Bảng các cơ sở dữ liệu gốc
-- II.1.1 Bảng Users
CREATE TABLE Users (
    id_user CHAR(5) PRIMARY KEY,
    name NVARCHAR(50),
    gender NVARCHAR(5),
    dob DATE,
    email_contact VARCHAR(50),
    password VARCHAR(20),
    account VARCHAR(20),
    language NVARCHAR(20)
);

-- II.1.2 Bảng Events
CREATE TABLE Events (
    id_event CHAR(5) PRIMARY KEY,
    name_event NVARCHAR(50),
    detail NVARCHAR(100),
    time_event DATETIME,
    time_created DATETIME,
    loop DATE,
    in_trash BIT
);

-- II.1.3 Bảng Calendars
CREATE TABLE Calendars (
    id_calendar CHAR(5) PRIMARY KEY,
    name_calendar NVARCHAR(50),
    time_created DATETIME,
    in_trash BIT
);

-- II.2 Bảng mối quan hệ giữa các Database
-- II.2.1 Quan hệ giữa Users và Events
-- II.2.1.1 Bảng used_eve: Quan hệ N:N giữa Users và Events
CREATE TABLE Used_Eve (
    id_user CHAR(5),
    id_event CHAR(5),
    notification BIT,
    PRIMARY KEY (id_user, id_event),
    FOREIGN KEY (id_user) REFERENCES Users(id_user),
    FOREIGN KEY (id_event) REFERENCES Events(id_event)
);

-- II.2.1.2 Bảng creator_eve: 1:N từ Users đến Events
CREATE TABLE Creator_Eve (
    id_user CHAR(5),
    id_event CHAR(5) UNIQUE,
    PRIMARY KEY (id_event),
    FOREIGN KEY (id_user) REFERENCES Users(id_user),
    FOREIGN KEY (id_event) REFERENCES Events(id_event)
);

-- II.2.2 Quan hệ giữa Users và Calendars
-- II.2.2.1 Bảng used_calen: Quan hệ N:N giữa Users và Calendars
CREATE TABLE Used_Calen (
    id_user CHAR(5),
    id_calendar CHAR(5),
    PRIMARY KEY (id_user, id_calendar),
    FOREIGN KEY (id_user) REFERENCES Users(id_user),
    FOREIGN KEY (id_calendar) REFERENCES Calendars(id_calendar)
);

-- II.2.2.2 Bảng creator_calen: 1:N từ Users đến Calendars
CREATE TABLE Creator_Calen (
    id_user CHAR(5),
    id_calendar CHAR(5) UNIQUE,
    PRIMARY KEY (id_calendar),
    FOREIGN KEY (id_user) REFERENCES Users(id_user),
    FOREIGN KEY (id_calendar) REFERENCES Calendars(id_calendar)
);

-- II.2.3 Quan hệ giữa Events và Calendars
-- II.2.3.1 Bảng include: Quan hệ N:N giữa Events và Calendars
CREATE TABLE Include (
    id_event CHAR(5),
    id_calendar CHAR(5),
    PRIMARY KEY (id_event, id_calendar),
    FOREIGN KEY (id_event) REFERENCES Events(id_event),
    FOREIGN KEY (id_calendar) REFERENCES Calendars(id_calendar)
);

-- III. Tạo dữ liệu nháp
-- III.1 Bảng dữ liệu góc
-- III.1.1 Users
INSERT INTO Users (id_user, name, gender, dob, email_contact, password, account, language) VALUES
('U001', N'Nguyễn Văn A', N'Nam', '1999-05-20', 'vana@example.com', '123abc', 'vana123', N'Vietnamese'),
('U002', N'Lê Thị B', N'Nữ', '2000-10-15', 'thib@example.com', '456def', 'leb456', N'English'),
('U003', N'John Smith', N'Male', '1995-08-01', 'johnsmith@example.com', 'js789', 'john_smith', N'English');

-- III.1.2 Events
INSERT INTO Events (id_event, name_event, detail, time_event, time_created, loop, in_trash) VALUES
('E001', N'Họp lớp', N'Họp lớp cấp 3 tại quán cà phê', '2025-08-01 18:00:00', '2025-07-28 10:00:00', NULL, 0),
('E002', N'Sinh nhật mẹ', N'Tổ chức sinh nhật cho mẹ ở nhà', '2025-09-12 19:00:00', '2025-07-30 15:00:00', '2026-09-12', 0),
('E003', N'Meeting Project', N'Họp dự án nhóm nghiên cứu', '2025-07-31 14:00:00', '2025-07-29 09:00:00', NULL, 0);

-- III.1.3 Calendars
INSERT INTO Calendars (id_calendar, name_calendar, time_created, in_trash) VALUES
('C001', N'Lịch cá nhân', '2025-07-01 09:00:00', 0),
('C002', N'Lịch gia đình', '2025-07-05 08:30:00', 0),
('C003', N'Lịch công việc', '2025-07-10 14:45:00', 0);

-- III.2 Bảng dữ liệu mô tả mối quan hệ
-- III.2.1 Mối quan hệ giữa Users và Events
-- III.2.1.1 Used_Eve
INSERT INTO Used_Eve (id_user, id_event, notification) VALUES
('U001', 'E001', 0),
('U002', 'E001', 1),
('U002', 'E002', 0),
('U003', 'E003', 0);

-- III.2.1.2 Creator_Eve
INSERT INTO Creator_Eve (id_user, id_event) VALUES
('U001', 'E001'),
('U002', 'E002'),
('U003', 'E003');

-- III.2.2 Mối quan hệ giữa Users và Calendars
-- III.2.2.1 Used_Calen
INSERT INTO Used_Calen (id_user, id_calendar) VALUES
('U001', 'C001'),
('U001', 'C003'),
('U002', 'C002'),
('U003', 'C003');

-- III.2.2.2 Creator_Calen
INSERT INTO Creator_Calen (id_user, id_calendar) VALUES
('U001', 'C001'),
('U002', 'C002'),
('U003', 'C003');

-- III.2.3 Mối quan hệ giữa Events và Calendars
-- III.2.3.1 Include
INSERT INTO Include (id_event, id_calendar) VALUES
('E001', 'C001'),
('E002', 'C002'),
('E003', 'C003');

-- IV. Các câu truy vấn
-- IV.1 Truy vấn dữ liệu giao diện phần mềm
-- IV.1.1 Truy vấn scene đăng nhập/đăng ký
-- IV.1.1.1 Tìm thông tin người dùng xem có tồn tại không để đăng nhập
SELECT *
FROM Users
WHERE account = 'vana123'
  AND password = '123abc';

-- IV.1.2 Truy vấn dữ liệu trên home scene
-- IV.1.2.1 Tìm tên người dùng từ tài khoản mật khẩu
SELECT name
FROM Users
WHERE account = 'vana123'
  AND password = '123abc';

-- IV.1.3 Truy vấn dữ liệu trên event scene
-- IV.1.3.1 Tìm tất cả các event mà người dùng 'U001' tạo ra sự kiện đó
SELECT E.*
FROM Events E
JOIN Creator_Eve CE ON E.id_event = CE.id_event
WHERE CE.id_user = 'U001';

-- IV.1.3.2 Tìm tất cả các event mà người dùng 'U001' có thể truy cập
SELECT E.*
FROM Events E
JOIN Used_Eve UE ON E.id_event = UE.id_event
WHERE UE.id_user = 'U001';

-- IV.1.3.3 Tìm tất cả event của người dùng 'U001' mà đang không ở thùng rác
SELECT E.*
FROM Events E
JOIN Creator_Eve CE ON E.id_event = CE.id_event
WHERE CE.id_user = 'U001'
  AND E.in_trash = 0;

-- IV.1.4 Truy vấn dữ liệu trên calendar scene
-- IV.1.4.1 Tìm tất cả các lịch mà người dùng 'U001' là người tạo
SELECT C.*
FROM Calendars C
JOIN Creator_Calen CC ON C.id_calendar = CC.id_calendar
WHERE CC.id_user = 'U001';

-- IV.1.4.2 Tìm tất cả các lịch mà người dùng 'U001' có quyền truy cập
SELECT C.*
FROM Calendars C
JOIN Used_Calen UC ON C.id_calendar = UC.id_calendar
WHERE UC.id_user = 'U001';

-- IV.1.4.3 Tìm tất cả các lịch mà 'U001' tạo ra và không bị đưa vào thùng rác
SELECT C.*
FROM Calendars C
JOIN Creator_Calen CC ON C.id_calendar = CC.id_calendar
WHERE CC.id_user = 'U001'
  AND C.in_trash = 0;

-- IV.1.5 Truy vấn dữ liệu trên about us scene

-- IV.1.6 Truy vấn dữ liệu trên profile scene

-- IV.2 Truy vấn dữ liệu xử lý back-end
ALTER TABLE Users ALTER COLUMN password VARCHAR(20);
SELECT * FROM Users;