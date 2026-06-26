# ATTENDANCE TRACKER SYSTEM FOR MY COLLEGE

This has been an issue I have been facing for MANY semesters... let's see how this performs 

---

## A. Main Idea

The core concept is to build a **completely local, privacy-centric Android application (APK)** that automates attendance management directly from your college timetable. Instead of manually logging course details or guessing how many classes you can afford to miss, the app uses text extraction (OCR/PDF parsing) to convert a timetable document into a digital calendar clone.

By calculating the total scheduled hours for the entire semester, the application acts as a predictive dashboard, telling you exactly how many safety margins (holidays) you have left for every subject to maintain a strict **80% attendance threshold**, all without needing an external backend server.

---

## B. Features

* **Automated Timetable Ingestion:** Upload your college timetable PDF or image; the app automatically extracts the schedule, identifying subject names, times, and weekly frequencies.
* **Semester-Span Forecasting:** Dynamically estimates the total number of classes ($T$) for each subject across the entire academic term based on your timetable structure.
* **One-Tap Daily Counter:** A dynamic home dashboard that displays only the classes scheduled for "Today." You can mark yourself *Present* or *Absent* with a single tap.
* **Proactive Holiday Buffer:** Displays a real-time countdown of exactly how many more classes you can miss ($R$) per subject before slipping below the 80% mark.
* **Offline Privacy:** Zero cloud synchronization, zero peer crowdsourcing, and no accounts required. All data and processing logic live securely within your phone's local storage.

---

## C. Mathematical Implications and Formulas

To handle situations where professor policies are missing, the app establishes a mathematical baseline using the parsed timetable data.

### 1. Estimating Total Semester Classes ($T$)

Let $W$ be the total number of instructional weeks in the college semester calendar, and $f_c$ be the frequency (number of times) a specific course $c$ appears in the weekly timetable matrix. The projected total classes are calculated as:

$$T = W \times f_c$$

### 2. Current Attendance Percentage

Let $P$ represent the number of sessions marked **Present**, and $A$ represent the number of sessions marked **Absent**. The current attendance metric is:

$$\text{Current Attendance \%} = \left( \frac{P}{P + A} \right) \times 100$$

### 3. Maximum Permissible Absences ($M$)

To maintain a strict 80% attendance policy ($\text{Threshold} = 0.80$), the maximum total classes you can miss over the entire semester is bounded by:

$$M = \lfloor T \times (1 - 0.80) \rfloor = \lfloor T \times 0.20 \rfloor$$

*(Note: The floor function $\lfloor \dots \rfloor$ is used because you cannot miss a fraction of a class.)*

### 4. Remaining Safety Buffer / Holidays Left ($R$)

To dynamically calculate how many more times you can miss a class without breaking the policy, the system evaluates:

$$R = M - A$$

* **If $R > 0$:** You have a safe margin of $R$ classes left to miss.
* **If $R = 0$:** You have reached your limit; any further absence will drop your percentage below 80%.
* **If $R < 0$:** Your attendance is critically low, and mathematically, you cannot restore it to 80% unless the total projected classes ($T$) increase due to extra sessions.

---

## D. Tech Stack

Because the application must run entirely offline on an Android device without a persistent Docker server on a PC, the tools are selected for cross-compilation capability:

* **Frontend UI Framework:** **BeeWare** with **Toga**. This allows you to build the user interface completely in Python using a native, cross-platform toolkit that works well for Android and desktop development.
* **Data Extraction Engine:** **pdfplumber** or **PyPDF2** for native text-based PDFs (lightweight, rapid processing). If the timetables are scanned images, an ARM-compiled implementation of **Tesseract OCR** via `pytesseract` is required.
* **Local Database:** **SQLite** (using Python's native `sqlite3` standard library). It reads and writes directly to a single file stored securely within the app's internal sandbox storage on Android.
* **Compilation Toolchain:** **BeeWare** tooling for packaging and deployment, with Toga for the app UI and native cross-platform support.

---

## E. Project Structure

A starter folder structure for the app could look like this:

```text
attendance-system/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── subject.py
│   │   └── attendance_record.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── parser.py
│   │   ├── attendance_logic.py
│   │   └── storage.py
│   ├── ui/
│   │   ├── __init__.py
│   │   └── main_window.py
│   └── utils/
│       ├── __init__.py
│       └── helpers.py
├── data/
│   └── sample_timetables/
├── tests/
├── requirements.txt
└── README.md
```

---

## F. Downloading and Deploying the App

Since this is a custom, private utility built entirely by you, it will bypass the Google Play Store and be deployed locally:

1. **Develop Locally:** You write and debug the Python source files (`main.py`, database models, and Toga UI code) on your development computer.
2. **Compile into an APK:** You run Buildozer inside a Linux terminal or a Docker container on your computer via the command:
```bash
buildozer android debug

```


3. **Transfer the File:** This generation process creates an installer file named something like `attendance_forecaster-1.0-debug.apk` inside your project's `bin/` directory. You transfer this file to your phone via USB cable, Google Drive, or a local network share.
4. **Install on Android:** Open the file manager application on your phone, locate the transferred `.apk` file, and tap it. Your phone will prompt you to allow **"Installation from Unknown Sources"** (since it is a self-signed developer build). Once approved, the application installs directly onto your phone dashboard, ready for completely offline usage.