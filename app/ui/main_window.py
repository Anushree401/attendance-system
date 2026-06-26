import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
from datetime import datetime
from app.services.storage import get_all_subjects, get_slots_for_day, log_attendance, add_subject, add_timetable_slot

class MainUI:
    def __init__(self, app):
        self.app = app
        self.main_box = toga.Box(style=Pack(direction=COLUMN))
        
        # Instead of OptionContainer (which can crash on some Android versions), we build a robust custom tab bar!
        self.tab_bar = toga.Box(style=Pack(direction=ROW, margin=5))
        btn_today = toga.Button("Today", on_press=self.show_today, style=Pack(flex=1, margin_right=2))
        btn_stats = toga.Button("Stats", on_press=self.show_stats, style=Pack(flex=1, margin_right=2))
        btn_setup = toga.Button("Setup", on_press=self.show_setup, style=Pack(flex=1))
        self.tab_bar.add(btn_today, btn_stats, btn_setup)
        
        self.content_box = toga.Box(style=Pack(flex=1, direction=COLUMN))
        self.main_box.add(self.tab_bar)
        self.main_box.add(self.content_box)
        
        self.today_box = toga.Box(style=Pack(direction=COLUMN, margin=10))
        self.stats_box = toga.Box(style=Pack(direction=COLUMN, margin=10))
        self.setup_box = toga.Box(style=Pack(direction=COLUMN, margin=10))
        
        # Build initial views
        self.build_today_ui()
        self.build_stats_ui()
        self.build_setup_ui()
        
        self.current_tab = "today"
        self.show_today(None)

    def show_today(self, widget):
        self.current_tab = "today"
        self.content_box.clear()
        self.content_box.add(self.today_box)
        self.refresh_all()

    def show_stats(self, widget):
        self.current_tab = "stats"
        self.content_box.clear()
        self.content_box.add(self.stats_box)
        self.refresh_all()
        
    def show_setup(self, widget):
        self.current_tab = "setup"
        self.content_box.clear()
        self.content_box.add(self.setup_box)
        self.refresh_all()

    def refresh_all(self, widget=None):
        self.build_today_ui()
        self.build_stats_ui()
        self.build_setup_ui()

    def build_today_ui(self):
        self.today_box.clear()
        
        header = toga.Box(style=Pack(direction=ROW, margin_bottom=15, align_items='center'))
        title = toga.Label("Today's Classes", style=Pack(flex=1, font_size=24, font_weight='bold'))
        btn_refresh = toga.Button("Refresh", on_press=self.refresh_all)
        header.add(title)
        header.add(btn_refresh)
        self.today_box.add(header)
        
        today_idx = datetime.today().weekday()
        slots = get_slots_for_day(today_idx)
        
        if not slots:
            self.today_box.add(toga.Label("No classes scheduled for today! Enjoy your day off.", style=Pack(margin_top=20)))
            return
            
        scroll = toga.ScrollContainer(style=Pack(flex=1))
        content = toga.Box(style=Pack(direction=COLUMN))
        
        for slot in slots:
            sub = slot['subject']
            
            card = toga.Box(style=Pack(direction=COLUMN, margin_bottom=15))
            
            details_box = toga.Box(style=Pack(direction=ROW, margin_bottom=5))
            time_label = toga.Label(f"{slot['start_time']} - {slot['end_time']}", style=Pack(font_weight='bold', font_size=16, margin_right=10))
            name_label = toga.Label(sub.name, style=Pack(font_size=16, flex=1))
            details_box.add(time_label)
            details_box.add(name_label)
            
            status_label = toga.Label(f"Current: {sub.attendance_percentage:.1f}% | {sub.status_message}", style=Pack(font_size=12, margin_bottom=10))
            
            buttons_box = toga.Box(style=Pack(direction=ROW))
            btn_present = toga.Button('Present', on_press=lambda w, sid=sub.id: self.mark_attendance(sid, 'present'), style=Pack(flex=1, margin_right=5))
            btn_absent = toga.Button('Absent', on_press=lambda w, sid=sub.id: self.mark_attendance(sid, 'absent'), style=Pack(flex=1))
            
            buttons_box.add(btn_present)
            buttons_box.add(btn_absent)
            
            card.add(details_box)
            card.add(status_label)
            card.add(buttons_box)
            
            content.add(card)
            content.add(toga.Divider(style=Pack(margin_bottom=10, margin_top=5)))
            
        scroll.content = content
        self.today_box.add(scroll)

    def build_stats_ui(self):
        self.stats_box.clear()
        
        header = toga.Box(style=Pack(direction=ROW, margin_bottom=15, align_items='center'))
        title = toga.Label("Overall Stats (80% Cap)", style=Pack(flex=1, font_size=24, font_weight='bold'))
        btn_refresh = toga.Button("Refresh", on_press=self.refresh_all)
        header.add(title)
        header.add(btn_refresh)
        self.stats_box.add(header)
        
        subjects = get_all_subjects()
        if not subjects:
            self.stats_box.add(toga.Label("No subjects found. Go to Setup to add some."))
            return
            
        scroll = toga.ScrollContainer(style=Pack(flex=1))
        content = toga.Box(style=Pack(direction=COLUMN))
        
        for sub in subjects:
            card = toga.Box(style=Pack(direction=COLUMN, margin_bottom=15))
            
            header = toga.Box(style=Pack(direction=ROW))
            name_lbl = toga.Label(sub.name, style=Pack(font_weight='bold', font_size=18, flex=1))
            perc_lbl = toga.Label(f"{sub.attendance_percentage:.1f}%", style=Pack(font_weight='bold', font_size=18))
            header.add(name_lbl)
            header.add(perc_lbl)
            
            stats_lbl = toga.Label(f"Conducted: {sub.total_conducted} | Present: {sub.classes_present} | Absent: {sub.classes_absent}", style=Pack(margin_top=5, font_size=12))
            msg_lbl = toga.Label(sub.status_message, style=Pack(margin_top=5, font_style='italic', font_size=12))
            
            card.add(header)
            card.add(stats_lbl)
            card.add(msg_lbl)
            
            content.add(card)
            content.add(toga.Divider(style=Pack(margin_bottom=10, margin_top=5)))
            
        scroll.content = content
        self.stats_box.add(scroll)

    def build_setup_ui(self):
        self.setup_box.clear()
        
        scroll = toga.ScrollContainer(style=Pack(flex=1))
        content = toga.Box(style=Pack(direction=COLUMN))
        
        # Section 1: Add Subject
        title1 = toga.Label("1. Create Subject", style=Pack(font_size=18, font_weight='bold', margin_bottom=10))
        sub_name_box = toga.Box(style=Pack(direction=ROW, margin_bottom=10))
        self.new_sub_input = toga.TextInput(placeholder="Subject Name...", style=Pack(flex=1, margin_right=5))
        btn_add_sub = toga.Button("Add Subject", on_press=self.handle_add_subject)
        sub_name_box.add(self.new_sub_input)
        sub_name_box.add(btn_add_sub)
        
        content.add(title1)
        content.add(sub_name_box)
        content.add(toga.Divider(style=Pack(margin_bottom=20, margin_top=20)))
        
        # Section 2: Add Slot to Subject
        title2 = toga.Label("2. Assign Weekly Class", style=Pack(font_size=18, font_weight='bold', margin_bottom=10))
        
        subjects = get_all_subjects()
        if not subjects:
            content.add(toga.Label("Add a subject first before assigning classes."))
        else:
            content.add(toga.Label("Subject:"))
            self.subject_dropdown = toga.Selection(items=[s.name for s in subjects], style=Pack(margin_bottom=10))
            
            content.add(toga.Label("Day of Week:"))
            days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            self.day_dropdown = toga.Selection(items=days, style=Pack(margin_bottom=10))
            
            content.add(toga.Label("Time Slot:"))
            time_box = toga.Box(style=Pack(direction=ROW, margin_bottom=10))
            self.start_input = toga.TextInput(placeholder="Start (10:00)", style=Pack(flex=1, margin_right=5))
            self.end_input = toga.TextInput(placeholder="End (11:00)", style=Pack(flex=1))
            time_box.add(self.start_input)
            time_box.add(self.end_input)
            
            btn_add_slot = toga.Button("Add Class to Schedule", on_press=self.handle_add_slot)
            
            content.add(self.subject_dropdown)
            content.add(self.day_dropdown)
            content.add(time_box)
            content.add(btn_add_slot)
            
        scroll.content = content
        self.setup_box.add(scroll)

    async def handle_add_subject(self, widget):
        name = self.new_sub_input.value
        if not name.strip():
            await self.app.main_window.dialog(toga.ErrorDialog("Error", "Subject name required."))
            return
        add_subject(name.strip())
        await self.app.main_window.dialog(toga.InfoDialog("Success", f"Added {name}!"))
        self.refresh_all()

    async def handle_add_slot(self, widget):
        sub_name = self.subject_dropdown.value
        day_str = self.day_dropdown.value
        start_t = self.start_input.value
        end_t = self.end_input.value
        
        if not start_t or not end_t:
            await self.app.main_window.dialog(toga.ErrorDialog("Error", "Start and end times are required."))
            return
            
        subjects = get_all_subjects()
        sub_id = next((s.id for s in subjects if s.name == sub_name), None)
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        day_idx = days.index(day_str)
        
        add_timetable_slot(sub_id, day_idx, start_t.strip(), end_t.strip())
        await self.app.main_window.dialog(toga.InfoDialog("Success", f"Added {sub_name} on {day_str}!"))
        self.refresh_all()

    def mark_attendance(self, subject_id, status):
        success = log_attendance(subject_id, status)
        if success:
            self.refresh_all()


def build_ui(app):
    ui = MainUI(app)
    return ui.main_box
