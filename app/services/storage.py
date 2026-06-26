import sqlite3
import sqlite3
from datetime  import datetime 
from app.models.subject import Subject 
from app.models.attendance_record import AttendanceRecord 


DB_NAME = "attendance.db" 


def get_connection(db_path=DB_NAME):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row 
    return conn 


def init_db(db_path=DB_NAME):
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        create table if not exists subjects (
            id integer primary key autoincrement,
            name text not null,
            total_projected_classes integer not null,
            classes_present integer default 0,
            classes_absent integer default 0 
        )
    ''')
    cursor.execute('''
        create table if not exists attendance_logs (
            id integer primary key autoincrement,
            subject_id integer not null,
            date_recorded text not null,
            status text not null check(status in ('present','absent')),
            foreign key (subject_id) references subjects(id)
        )
    ''')
    conn.commit()
    conn.close()


def add_subject(name:str,total_projected_classes:int,db_path=DB_NAME) -> int:
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        insert into subjects (name,total_projected_classes) values (?,?)
    ''',(name,total_projected_classes))
    subject_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return subject_id 


def get_all_subjects(db_path=DB_NAME) -> list[Subject]:
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute('select * from subjects')
    rows = cursor.fetchall()
    conn.close()
    subjects = []
    for row in rows:
        subjects.append(Subject(
            id=row['id'],
            name=row['name'],
            total_projected_classes=row['total_projected_classes'],
            classes_present=row['classes_present'],
            classes_absent=row['classes_absent']
        ))
    return subjects 


def get_subject_by_id(subject_id:int,db_path=DB_NAME) -> Subject:
    conn = get_connection(db_path)
    cursor = conn.cursor() 
    cursor.execute('select * from subjects where id = ?',(subject_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return Subject(
            id=row['id'],
            name=row['name'],
            total_projected_classes=row['total_projected_classes'],
            classes_present=row['classes_present'],
            classes_absent=row['classes_absent']
        )
    return None


def log_attendance(subject_id:int,status:str,date_recorded:str=None,db_path=DB_NAME):
    if status.lower() not in ['present','absent']:
        raise ValueError("Status must be 'present' or 'absent'")
    if date_recorded is None:
        date_recorded = datetime.now().date().isoformat()
    conn = get_connection(db_path)
    cursor = conn.cursor() 
    try:
        cursor.execute('''
            insert into attendance_logs (
                subject_id,
                date_recorded,
                status
            ) values (?,?,?)
        ''',(subject_id,date_recorded,status.lower()))
        if status.lower() == "present":
            cursor.execute('update subjects set classes_present=classes_present+1 where id = ?',(subject_id,))
        else:
            cursor.execute('update subjects set classes_absent=classes_absent+1 where id = ?',(subject_id,))
        conn.commit()
    except sqlite3.Error as e:
        conn.rollback()
        print(f"Database error: {e}")
    finally:
        conn.close()


def get_attendance_log(subject_id:int,db_path=DB_NAME) -> list[AttendanceRecord]:
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute('select * from attendance_logs where subject_id = ? order by date_recorded desc',(subject_id,))
    rows = cursor.fetchall()
    conn.close()
    logs = []
    for row in rows:
        date_obj = datetime.strptime(row['date_recorded'],"%Y-%m-%d").date()
        logs.append(AttendanceRecord(
            id=row['id'],
            subject_id=row['subject_id'],
            date_recorded=date_obj,
            status=row['status']
        ))
    return logs 