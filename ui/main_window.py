from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton, QLabel, QMessageBox
from core.assistant import default_assistant
from core import action_registry

class MainWindow(QMainWindow):
    """Main window with a typed-chat interface integrated with the assistant.
    When the assistant requests an action that requires confirmation the UI
    will prompt the user.
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
        self.status_label.setText("Status: thinking...")
        resp = default_assistant.handle_text(text)
        # If the assistant asks to run an action
        if resp.action:
            if resp.requires_confirmation:
                confirm = QMessageBox.question(self, "Confirm action", f"{resp.text}\n\nProceed?", QMessageBox.Yes | QMessageBox.No)
                if confirm != QMessageBox.Yes:
                    self.chat_view.append("ANIS: Action cancelled by user.")
                    self.status_label.setText("Status: idle")
                    self.input.clear()
                    return
            # attempt to execute action
            result = action_registry.execute_action(resp.action, resp.action_args or {})
            if result.get("success"):
                self.chat_view.append(f"ANIS: Done, sir. {result.get('summary')}")
            else:
                if result.get("requires_confirmation"):
                    # UI-level confirmation if registry indicates so
                    confirm = QMessageBox.question(self, "Confirm action", f"Action {resp.action} requires confirmation. Proceed?", QMessageBox.Yes | QMessageBox.No)
                    if confirm == QMessageBox.Yes:
                        # bypass permission by re-running handler directly (handler call)
                        action = action_registry.get_action(resp.action)
                        try:
                            r = action.handler(resp.action_args or {})
                            self.chat_view.append(f"ANIS: Done, sir. {r.get('summary')}")
                        except Exception as e:
                            self.chat_view.append(f"ANIS: Failed to execute action: {e}")
                    else:
                        self.chat_view.append("ANIS: Action cancelled by user.")
                else:
                    self.chat_view.append(f"ANIS: Failed to execute action: {result.get('error')}")
        else:
            self.chat_view.append(f"ANIS: {resp.text}")
        self.status_label.setText("Status: idle")
        self.input.clear()
