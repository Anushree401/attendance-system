import math

class Subject:
    def __init__(self, id: int, name: str, classes_present: int = 0, classes_absent: int = 0):
        self.id = id
        self.name = name
        self.classes_present = classes_present
        self.classes_absent = classes_absent

    @property
    def total_conducted(self) -> int:
        return self.classes_present + self.classes_absent

    @property
    def attendance_percentage(self) -> float:
        if self.total_conducted == 0:
            return 100.0
        return (self.classes_present / self.total_conducted) * 100

    @property
    def status_message(self) -> str:
        """
        Calculates how many classes the student can safely miss to stay above 80%, 
        or how many they must consecutively attend to reach 80%.
        """
        P = self.classes_present
        T = self.total_conducted
        
        if T == 0:
            return "No classes recorded yet."
            
        if self.attendance_percentage >= 80.0:
            # (P) / (T + x) >= 0.80 => x <= (P - 0.8T) / 0.8
            can_miss = math.floor((P - 0.8 * T) / 0.8)
            if can_miss > 0:
                return f"On track! You can afford to miss {can_miss} upcoming classes."
            else:
                return "On track! You are right on the 80% line. Don't miss the next one!"
        else:
            # (P + y) / (T + y) >= 0.80 => 0.2y >= 0.8T - P => y >= (0.8T - P) / 0.2
            must_attend = math.ceil((0.8 * T - P) / 0.2)
            return f"Danger! You must attend {must_attend} classes in a row to hit 80%."