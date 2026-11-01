# UI styles for ANIS AI - dangerous cyberpunk dark theme

STYLE = """
QWidget {
    background: #05070b;
    color: #e7ecff;
    font-family: 'Segoe UI', Tahoma, Arial;
    selection-background-color: #ff3b5c;
    selection-color: #ffffff;
}

QMainWindow {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #070a10, stop:0.5 #0d1117, stop:1 #05070b);
}

QLabel#title {
    font-size: 24px;
    font-weight: 800;
    letter-spacing: 2px;
    color: #ff4d6d;
    text-transform: uppercase;
    text-shadow: 0 0 12px rgba(255, 77, 109, 0.9);
}

QLabel#status {
    color: #7df9ff;
    font-weight: 600;
    letter-spacing: 1px;
}

QTextEdit {
    background-color: #0b1016;
    border: 1px solid #1c2431;
    border-radius: 10px;
    padding: 10px;
    color: #edf4ff;
    selection-background-color: #ff3b5c;
    box-shadow: inset 0 0 12px rgba(0, 0, 0, 0.6);
}

QLineEdit {
    background-color: #0b1016;
    border: 1px solid #2b394d;
    border-radius: 10px;
    padding: 8px 10px;
    color: #f4f7ff;
    selection-background-color: #ff3b5c;
}

QLineEdit:focus {
    border: 1px solid #ff5c7a;
    box-shadow: 0 0 10px rgba(255, 92, 122, 0.6);
}

QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #1d2b39, stop:1 #111922);
    border: 1px solid #30455d;
    border-radius: 10px;
    color: #edf4ff;
    padding: 8px 14px;
    font-weight: 600;
}

QPushButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #2e3d4f, stop:1 #17212b);
    border: 1px solid #ff4d6d;
}

QPushButton#micro {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #00f5d4, stop:1 #00b4d8);
    color: #041c20;
    font-weight: 700;
    border: none;
    box-shadow: 0 0 14px rgba(0, 245, 212, 0.7);
}

QPushButton#micro:checked {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #ff4d6d, stop:1 #ff7b54);
    color: white;
    box-shadow: 0 0 16px rgba(255, 77, 109, 0.8);
}

QPushButton#stop {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #ff4d6d, stop:1 #ff2e63);
    border: none;
    color: white;
    box-shadow: 0 0 14px rgba(255, 77, 109, 0.7);
}

QComboBox {
    background-color: #0b1016;
    border: 1px solid #2b394d;
    border-radius: 10px;
    padding: 6px 10px;
    color: #edf4ff;
}

QComboBox QAbstractItemView {
    background-color: #111922;
    color: #edf4ff;
    selection-background-color: #ff3b5c;
}

QListWidget {
    background-color: #090d12;
    border: 1px solid #1f2a37;
    border-radius: 10px;
    color: #dfeaf7;
}

QListWidget::item {
    padding: 8px;
    border-bottom: 1px solid rgba(255,255,255,0.04);
}

QListWidget::item:selected {
    background: rgba(255, 77, 109, 0.2);
    color: white;
}

QFrame {
    background: rgba(14, 17, 22, 0.9);
    border: 1px solid #1b2530;
    border-radius: 14px;
}

#orb {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #ff2e63, stop:0.45 #ff7b54, stop:1 #7d5cff);
    border-radius: 60px;
    min-width: 120px;
    min-height: 120px;
    border: 2px solid rgba(255,255,255,0.2);
    box-shadow: 0 0 25px rgba(255, 72, 109, 0.75);
}

QMessageBox {
    background: #0a0d12;
}

QMessageBox QLabel {
    color: #edf4ff;
}

"""
