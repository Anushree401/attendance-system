import sqlite3
from datetime import datetime
from app.models.subject import Subject
from app.models.attendance_record import AttendanceRecord

def get_db_path():
    try:
        import toga
        app = toga.App.app
        if app:
            return str(app.paths.data / "attendance.db")
    except Exception:
        pass
    return "attendance.db"

def get_connection(db_path=None):
    conn = sqlite3.connect(db_path or get_db_path())
    conn.row_factory = sqlite3.Row 
    return conn 

def init_db(db_path=None):
    conn = get_connection(db_path)
    cursor = conn.cursor()
    
    # We drop existing tables to migrate to the new weekly manual schema
    cursor.execute('drop table if exists subjects')
    cursor.execute('drop table if exists attendance_logs')
    cursor.execute('drop table if exists timetable_slots')
    
    cursor.execute('''
        create table subjects (
            id integer primary key autoincrement,
            name text not null,
            classes_present integer default 0,
            classes_absent integer default 0 
        )
    ''')
    cursor.execute('''
        create table attendance_logs (
            id integer primary key autoincrement,
            subject_id integer not null,
            date_recorded text not null,
            status text not null check(status in ('present','absent')),
            foreign key (subject_id) references subjects(id)
        )
    ''')
    cursor.execute('''
        create table timetable_slots (
            id integer primary key autoincrement,
            subject_id integer not null,
            day_of_week integer not null,
            start_time text not null,
            end_time text not null,
            foreign key (subject_id) references subjects(id)
        )
    ''')
    conn.commit()
    conn.close()

def add_subject(name:str, db_path=None) -> int:
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        insert into subjects (name) values (?)
    ''',(name,))
    subject_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return subject_id 

def add_timetable_slot(subject_id:int, day_of_week:int, start_time:str, end_time:str, db_path=None):
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        insert into timetable_slots (subject_id, day_of_week, start_time, end_time) 
        values (?, ?, ?, ?)
    ''', (subject_id, day_of_week, start_time, end_time))
    conn.commit()
    conn.close()

def get_all_subjects(db_path=None) -> list[Subject]:
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
            classes_present=row['classes_present'],
            classes_absent=row['classes_absent']
        ))
    return subjects 

def get_slots_for_day(day_of_week:int, db_path=None):
    """Returns a list of dicts representing classes scheduled for a given day."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        select s.id as subject_id, s.name, t.start_time, t.end_time, s.classes_present, s.classes_absent
        from timetable_slots t
        join subjects s on t.subject_id = s.id
        where t.day_of_week = ?
        order by t.start_time asc
    ''', (day_of_week,))
    rows = cursor.fetchall()
    conn.close()
    
    # We bundle the data into a convenient dict with a populated Subject object for math
    slots = []
    for row in rows:
        subject_obj = Subject(
            id=row['subject_id'],
            name=row['name'],
            classes_present=row['classes_present'],
            classes_absent=row['classes_absent']
        )
        slots.append({
            'subject': subject_obj,
            'start_time': row['start_time'],
            'end_time': row['end_time']
        })
    return slots

def log_attendance(subject_id:int,status:str,date_recorded:str=None,db_path=None):
    if status.lower() not in ['present','absent']:
        raise ValueError("Status must be 'present' or 'absent'")
    if date_recorded is None:
        date_recorded = datetime.now().date().isoformat()
    conn = get_connection(db_path)
    cursor = conn.cursor() 
    try:
        # Prevent double-logging for the same subject on the same exact calendar day 
        # (useful so tapping 'present' multiple times accidentally doesn't inflate stats)
        cursor.execute('''
            select id from attendance_logs where subject_id = ? and date_recorded = ?
        ''', (subject_id, date_recorded))
        if cursor.fetchone():
            return False # Already logged today

        cursor.execute('''
            insert into attendance_logs (subject_id, date_recorded, status) values (?,?,?)
        ''',(subject_id, date_recorded, status.lower()))
        
        if status.lower() == "present":
            cursor.execute('update subjects set classes_present=classes_present+1 where id = ?',(subject_id,))
        else:
            cursor.execute('update subjects set classes_absent=classes_absent+1 where id = ?',(subject_id,))
        conn.commit()
        return True
    except sqlite3.Error as e:
        conn.rollback()
        print(f"Database error: {e}")
        return False
    finally:
        conn.close()