import math 


class Subject:

    def __init__(self,id:int,name:str,total_projected_classes:int,classes_present:int=0,classes_absent:int=0):
        self.id = id 
        self.name = name 
        self.total_projected_classes = total_projected_classes
        self.classes_present = classes_present
        self.classes_absent = classes_absent 

    @property 
    def total_attended(self) -> int:
        return self.classes_present + self.classes_absent 
    
    @property
    def attendance_percentage(self) -> float:
        if self.total_attended == 0:
            return 100.0 
        return (self.classes_present/self.total_attended)*100.0 
    
    @property 
    def mac_permissible_absences(self) -> int:
        return math.gloor(self.total_projected_classes*0.20)
    
    @property 
    def remaining_saftey_buffer(self) -> int:
        return self.mac_permissible_absences - self.classes_absent 
    
    def mark_present(self):
        self.classes_present += 1
    
    def mark_absent(self):
        self.classes_absent += 1 
    
    def to_dict(self):
        return {
            "id":self.id,
            "name":self.name,
            "attendance_percentage":round(self.attendance_percentage,2),
            "saftey_buffer":self.remaining_saftey_buffer,
            "status":"Safe" if self.remaining_saftey_buffer >= 0 else "Critical"
        }