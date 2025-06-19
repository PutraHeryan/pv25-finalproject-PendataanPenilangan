import sys
import sqlite3
import csv
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QGridLayout, QLabel, QLineEdit, QPushButton, QTableWidget, 
    QTableWidgetItem, QHeaderView, QStatusBar, QMessageBox, QFileDialog,
    QSpinBox, QComboBox, QDateEdit, QTextEdit
)
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtCore import Qt, QDate

# Informasi Mahasiswa (sesuaikan dengan data Anda)
STUDENT_NAME = "Putra Heryan Gagah Perkasa"
STUDENT_ID = "F1D022087"

class MainWindow(QMainWindow):
    """Kelas utama untuk jendela aplikasi."""

    def __init__(self):
        super().__init__()
        self.db_name = 'pelanggaran.db'
        self.init_db()
        self.init_ui()
        self.load_data()

    def init_ui(self):
        """Inisialisasi semua komponen antarmuka pengguna (UI)."""
        self.setWindowTitle("Sistem Pendataan Pelaku Penilangan")
        self.setGeometry(100, 100, 900, 700)

        # Membuat Menu Bar
        self.create_menu_bar()

        # Membuat Status Bar
        self.create_status_bar()

        # Widget utama dan layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)

        # Form untuk input data
        form_layout = QGridLayout()
        form_layout.setSpacing(10)

        # Input fields
        self.nama_input = QLineEdit()
        self.nama_input.setPlaceholderText("Masukkan nama lengkap pelanggar")
        
        self.usia_input = QSpinBox()
        self.usia_input.setRange(0, 99)
        
        self.gender_input = QComboBox()
        self.gender_input.addItems(["Pria", "Wanita"])
        
        self.tanggal_input = QDateEdit(calendarPopup=True)
        self.tanggal_input.setDate(QDate.currentDate())
        
        self.detail_input = QTextEdit()
        self.detail_input.setPlaceholderText("Contoh: Tidak memakai helm, melanggar lampu merah.")
        self.detail_input.setFixedHeight(80)

        # Menambahkan widget ke form layout
        form_layout.addWidget(QLabel("Nama Pelanggar:"), 0, 0)
        form_layout.addWidget(self.nama_input, 0, 1)
        form_layout.addWidget(QLabel("Usia:"), 1, 0)
        form_layout.addWidget(self.usia_input, 1, 1)
        form_layout.addWidget(QLabel("Gender:"), 2, 0)
        form_layout.addWidget(self.gender_input, 2, 1)
        form_layout.addWidget(QLabel("Tanggal Kejadian:"), 3, 0)
        form_layout.addWidget(self.tanggal_input, 3, 1)
        form_layout.addWidget(QLabel("Detail Pelanggaran:"), 4, 0)
        form_layout.addWidget(self.detail_input, 4, 1, 1, 2) # Span 2 kolom
        
        # Tombol
        button_layout = QHBoxLayout()
        add_button = QPushButton("➕ Tambah Data")
        add_button.clicked.connect(self.add_data)
        
        export_button = QPushButton("📄 Export ke CSV")
        export_button.clicked.connect(self.export_to_csv)

        button_layout.addStretch()
        button_layout.addWidget(add_button)
        button_layout.addWidget(export_button)
        button_layout.addStretch()

        # Tabel untuk menampilkan data
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(5)
        self.table_widget.setHorizontalHeaderLabels(["Nama", "Usia", "Gender", "Tanggal Kejadian", "Detail Pelanggaran"])
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_widget.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers) # Data tidak bisa diedit langsung di tabel
        self.table_widget.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table_widget.setObjectName("data_table") # Menambahkan nama objek untuk styling

        # Menambahkan semua layout ke layout utama
        main_layout.addLayout(form_layout)
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.table_widget)

    def create_menu_bar(self):
        """Membuat dan mengkonfigurasi QMenuBar."""
        menu_bar = self.menuBar()

        # Menu File
        file_menu = menu_bar.addMenu("File")
        export_action = QAction("Export ke CSV", self)
        export_action.triggered.connect(self.export_to_csv)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()

        exit_action = QAction("Keluar", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Menu Bantuan
        help_menu = menu_bar.addMenu("Bantuan")
        about_action = QAction("Tentang", self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)

    def create_status_bar(self):
        """Membuat dan menampilkan informasi di QStatusBar."""
        status_bar = QStatusBar()
        self.setStatusBar(status_bar)
        status_bar.showMessage(f"Nama: {STUDENT_NAME} | NIM: {STUDENT_ID}")

    def init_db(self):
        """Membuat database SQLite dan tabel jika belum ada."""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            query = """
            CREATE TABLE IF NOT EXISTS pelanggaran (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nama TEXT NOT NULL,
                usia INTEGER NOT NULL,
                gender TEXT NOT NULL,
                tanggal TEXT NOT NULL,
                detail TEXT
            )
            """
            cursor.execute(query)
            conn.commit()
        except sqlite3.Error as e:
            self.show_error_message("Database Error", f"Gagal menginisialisasi database: {e}")
        finally:
            if conn:
                conn.close()

    def load_data(self):
        """Memuat data dari database dan menampilkannya di tabel."""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("SELECT nama, usia, gender, tanggal, detail FROM pelanggaran")
            rows = cursor.fetchall()
            
            self.table_widget.setRowCount(0) # Membersihkan tabel sebelum memuat data baru
            self.table_widget.setRowCount(len(rows))
            for row_idx, row_data in enumerate(rows):
                for col_idx, col_data in enumerate(row_data):
                    item = QTableWidgetItem(str(col_data))
                    self.table_widget.setItem(row_idx, col_idx, item)
        except sqlite3.Error as e:
            self.show_error_message("Load Data Error", f"Gagal memuat data dari database: {e}")
        finally:
            if conn:
                conn.close()

    def add_data(self):
        """Menambahkan data baru dari form ke database."""
        nama = self.nama_input.text().strip()
        usia = self.usia_input.value()
        gender = self.gender_input.currentText()
        tanggal = self.tanggal_input.date().toString("yyyy-MM-dd")
        detail = self.detail_input.toPlainText().strip()

        if not nama:
            self.show_error_message("Input Tidak Valid", "Nama tidak boleh kosong.")
            return

        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO pelanggaran (nama, usia, gender, tanggal, detail)
                VALUES (?, ?, ?, ?, ?)
            """, (nama, usia, gender, tanggal, detail))
            conn.commit()
            self.statusBar().showMessage(f"Data '{nama}' berhasil ditambahkan!", 3000)
            self.clear_inputs()
            self.load_data() # Refresh tabel
        except sqlite3.Error as e:
            self.show_error_message("Database Error", f"Gagal menambahkan data: {e}")
        finally:
            if conn:
                conn.close()
    
    def clear_inputs(self):
        """Membersihkan semua field input setelah data ditambahkan."""
        self.nama_input.clear()
        self.usia_input.setValue(17)
        self.gender_input.setCurrentIndex(0)
        self.tanggal_input.setDate(QDate.currentDate())
        self.detail_input.clear()

    def export_to_csv(self):
        """Mengekspor data dari tabel ke file CSV."""
        path, _ = QFileDialog.getSaveFileName(self, "Simpan File CSV", "", "CSV Files (*.csv)")

        if path:
            try:
                with open(path, 'w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    
                    # Tulis header
                    header = [self.table_widget.horizontalHeaderItem(i).text() for i in range(self.table_widget.columnCount())]
                    writer.writerow(header)

                    # Tulis data
                    for row in range(self.table_widget.rowCount()):
                        row_data = [self.table_widget.item(row, col).text() for col in range(self.table_widget.columnCount())]
                        writer.writerow(row_data)
                
                self.statusBar().showMessage(f"Data berhasil diekspor ke {path}", 5000)
            except Exception as e:
                self.show_error_message("Export Error", f"Gagal mengekspor file: {e}")

    def show_about_dialog(self):
        """Menampilkan dialog 'Tentang'."""
        QMessageBox.about(self, "Tentang Aplikasi",
                          "<b>Sistem Pendataan Pelaku Penilangan</b>"
                          "<p>Aplikasi ini dibuat untuk memenuhi tugas besar pemrosesan virtual."
                          f"<p>Dibuat oleh: {STUDENT_NAME} ({STUDENT_ID})"
                          "<p>Dibangun dengan PyQt6 dan SQLite.")

    def show_error_message(self, title, message):
        """Menampilkan dialog pesan error."""
        # Style untuk QMessageBox agar sesuai tema gelap
        msg_box = QMessageBox(self)
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #2c2c2c;
                color: #f0f0f0;
            }
            QMessageBox QLabel {
                color: #f0f0f0;
            }
            QMessageBox QPushButton {
                background-color: #007bff;
                color: white;
                padding: 5px 10px;
                border-radius: 3px;
            }
        """)
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.exec()

def apply_stylesheet(app):
    style = """
    QMainWindow, QWidget {
        background-color: #1e1e1e; /* Latar belakang utama yang sangat gelap */
    }
    QLabel {
        font-size: 14px;
        color: #e0e0e0; /* Warna teks terang */
    }
    QLineEdit, QSpinBox, QComboBox, QDateEdit, QTextEdit {
        padding: 8px;
        border: 1px solid #444;
        border-radius: 5px;
        font-size: 14px;
        background-color: #2c2c2c; /* Latar belakang input lebih terang */
        color: #f0f0f0; /* Warna teks input terang */
    }
    QLineEdit:focus, QSpinBox:focus, QComboBox:focus, QTextEdit:focus {
        border: 1px solid #007bff; /* Highlight biru saat aktif */
    }
    QPushButton {
        background-color: #007bff;
        color: white;
        font-size: 14px;
        font-weight: bold;
        padding: 10px 15px;
        border-radius: 5px;
        border: none;
    }
    QPushButton:hover {
        background-color: #0056b3;
    }
    QPushButton:pressed {
        background-color: #004494;
    }
    QTableWidget {
        background-color: #2c2c2c;
        color: #f0f0f0;
        border: 1px solid #444;
        gridline-color: #444;
        font-size: 13px;
    }
    QTableWidget::item:selected {
        background-color: #007bff; /* Warna seleksi baris */
        color: #ffffff;
    }
    QHeaderView::section {
        background-color: #3a3a3a;
        color: #e0e0e0;
        padding: 8px;
        border: 1px solid #444;
        font-weight: bold;
    }
    QStatusBar {
        background-color: #1e1e1e;
        color: #e0e0e0;
        font-weight: bold;
        border-top: 1px solid #444;
    }
    QMenuBar {
        background-color: #2c2c2c;
        color: #e0e0e0;
    }
    QMenuBar::item:selected {
        background-color: #007bff;
        color: white;
    }
    QMenu {
        background-color: #2c2c2c;
        color: #e0e0e0;
        border: 1px solid #444;
    }
    QMenu::item:selected {
        background-color: #007bff;
    }
    """
    app.setStyleSheet(style)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    apply_stylesheet(app) # Menerapkan style
    window = MainWindow()
    window.show()
    sys.exit(app.exec())