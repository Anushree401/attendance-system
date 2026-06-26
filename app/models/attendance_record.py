from datetime import date 


class AttendanceRecord:

    def __init__(self,id:int,subject_id:int,date_recorded:date,status:str):
        self.id = id
        self.subject_id = subject_id
        self.date_recorded = date_recorded
        if status.lower() not in ['present','absent']:
            raise ValueError("Status must be 'present' or 'absent'")
        self.status = status.lower() 
    
    @property
    def is_present(self):
        return self.status == 'present'
    
    @property 
    def is_absent(self):
        return self.status == 'absent' 