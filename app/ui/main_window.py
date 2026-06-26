import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
from app.services.storage import get_all_subjects, log_attendance
from app.services.parser import parse_timetable


class MainUI:
    
    def __init__(self, app):
        self.app = app
        self.main_box = toga.Box(style=Pack(direction=COLUMN, margin=15))
        self.build_ui()
    def build_ui(self):
        for child in list(self.main_box.children):
            self.main_box.remove(child)
        header_box = toga.Box(style=Pack(direction=ROW, margin_bottom=15))
        title_label = toga.Label(
            "Dashboard",
            style=Pack(flex=1, font_size=24, font_weight='bold')
        )
        btn_load = toga.Button("Load Timetable", on_press=self.load_timetable)
        header_box.add(title_label)
        header_box.add(btn_load)
        self.main_box.add(header_box)
        subjects = get_all_subjects()
        if not subjects:
            empty_label = toga.Label("No subjects found. Please load a timetable.", style=Pack(margin_top=20))
            self.main_box.add(empty_label)
            return
        for sub in subjects:
            class_box = toga.Box(style=Pack(direction=ROW, margin_bottom=15))                    
            details_box = toga.Box(style=Pack(direction=COLUMN, flex=1))
            name_label = toga.Label(sub.name, style=Pack(font_weight='bold', font_size=16))
            status_text = f"Attendance: {sub.attendance_percentage:.1f}% | Buffer: {sub.remaining_safety_buffer}"
            status_label = toga.Label(status_text, style=Pack(margin_top=2))
            details_box.add(name_label)
            details_box.add(status_label)
            buttons_box = toga.Box(style=Pack(direction=ROW, margin_left=10, align_items='center'))
            btn_present = toga.Button(
                'Present', 
                on_press=lambda w, cid=sub.id: self.mark_attendance(cid, 'present'), 
                style=Pack(margin_right=5)
            )
            btn_absent = toga.Button(
                'Absent', 
                on_press=lambda w, cid=sub.id: self.mark_attendance(cid, 'absent')
            )
            buttons_box.add(btn_present)
            buttons_box.add(btn_absent)
            class_box.add(details_box)
            class_box.add(buttons_box)
            self.main_box.add(class_box)

    async def load_timetable(self, widget):
        try:
            dialog = toga.OpenFileDialog("Select Timetable", file_types=['txt', 'pdf'])
            file_path = await self.app.main_window.dialog(dialog)
            if file_path:
                success = parse_timetable(str(file_path))
                if success:
                    await self.app.main_window.dialog(toga.InfoDialog("Success", "Timetable loaded successfully!"))
                    self.build_ui()
                else:
                    await self.app.main_window.dialog(toga.ErrorDialog("Error", "Failed to parse timetable."))
        except ValueError:
            pass 

    def mark_attendance(self, subject_id, status):
        log_attendance(subject_id, status)
        self.build_ui()


def build_ui(app):
    ui = MainUI(app)
    return ui.main_box