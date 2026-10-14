from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton, QLabel

class MainWindow(QMainWindow):
    """Minimal main window with a typed-chat interface.
    This implements Phase 2: a basic typed chat UI. Speech, AI providers, and actions
    are stubs and will be added in subsequent phases.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ANIS AI")
        self.resize(900, 640)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        self.status_label = QLabel("Status: idle")
        layout.addWidget(self.status_label)

        self.chat_view = QTextEdit()
        self.chat_view.setReadOnly(True)
        layout.addWidget(self.chat_view)

        self.input = QLineEdit()
        self.input.setPlaceholderText("Type a message and press Send...")
        layout.addWidget(self.input)

        btn = QPushButton("Send")
        btn.clicked.connect(self._on_send)
        layout.addWidget(btn)

    def _on_send(self):
        text = self.input.text().strip()
        if not text:
            return
        self.chat_view.append(f"You: {text}")
        # TODO: hook into core.assistant to get a real response
        self.chat_view.append(f"ANIS: (stub) I heard: {text}")
        self.input.clear()
