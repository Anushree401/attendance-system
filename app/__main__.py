import toga
from app.ui.main_window import build_ui
from app.services.storage import init_db


class AttendanceApp(toga.App):
    
    def startup(self):
        try:
            init_db()
            print("Database initialized successfully.")
        except Exception as e:
            print(f"Failed to init database: {e}")
        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = build_ui(self)
        self.main_window.show()


def main():
    return AttendanceApp('Attendance Forecaster', 'org.beeware.attendance')

if __name__ == '__main__':
    main().main_loop()