from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QTextEdit,
    QLineEdit,
    QPushButton,
    QLabel,
    QMessageBox,
    QHBoxLayout,
    QComboBox,
    QListWidget,
    QSplitter,
    QFrame,
    QGridLayout,
)
from PySide6.QtCore import Qt, QTimer, Signal, QObject, QThread

from core.assistant import default_assistant
from core import action_registry
from core.state import AssistantState
from speech.microphone import MockMicrophone
from speech.speech_to_text import MockSpeechToText
from speech.text_to_speech import MockTextToSpeech
from memory import database
from ui.styles import STYLE


class FunctionThread(QThread):
    result = Signal(object)

    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs

    def run(self):
        try:
            r = self.fn(*self.args, **self.kwargs)
            self.result.emit({"success": True, "result": r})
        except Exception as e:
            self.result.emit({"success": False, "error": str(e)})


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ANIS AI")
        self.resize(1100, 720)

        # Load DB and preferences
        database.initialize_db()

        # Speech components (mockable)
        self.microphone = MockMicrophone()
        self.stt = MockSpeechToText()
        self.tts = MockTextToSpeech()

        # State
        self.state = AssistantState.IDLE
        self.current_worker = None
        self.current_tts_thread = None

        # UI
        central = QWidget()
        self.setCentralWidget(central)
        central.setStyleSheet(STYLE)

        main_layout = QHBoxLayout(central)

        # Left: conversation and controls
        left_frame = QFrame()
        left_frame.setFrameShape(QFrame.StyledPanel)
        left_layout = QVBoxLayout(left_frame)

        header = QHBoxLayout()
        title = QLabel("ANIS AI")
        title.setObjectName("title")
        header.addWidget(title)
        header.addStretch()
        self.status_label = QLabel("Status: idle")
        header.addWidget(self.status_label)
        left_layout.addLayout(header)

        # Orb + conversation split
        top_split = QHBoxLayout()

        # Orb
        self.orb = QLabel()
        self.orb.setObjectName("orb")
        self.orb.setFixedSize(120, 120)
        top_split.addWidget(self.orb)

        # Conversation
        convo_layout = QVBoxLayout()
        self.chat_view = QTextEdit()
        self.chat_view.setReadOnly(True)
        convo_layout.addWidget(self.chat_view)

        input_row = QHBoxLayout()
        self.input = QLineEdit()
        self.input.setPlaceholderText("Type a message and press Send...")
        input_row.addWidget(self.input)
        send_btn = QPushButton("Send")
        send_btn.clicked.connect(self._on_send)
        input_row.addWidget(send_btn)
        convo_layout.addLayout(input_row)

        top_split.addLayout(convo_layout)
        left_layout.addLayout(top_split)

        # Controls row
        controls = QHBoxLayout()
        self.micro_btn = QPushButton("Mic")
        self.micro_btn.setObjectName("micro")
        self.micro_btn.setCheckable(True)
        self.micro_btn.clicked.connect(self._on_toggle_mic)
        controls.addWidget(self.micro_btn)

        self.ptt_btn = QPushButton("Push-to-talk")
        self.ptt_btn.setCheckable(True)
        self.ptt_btn.pressed.connect(self._on_ptt_pressed)
        self.ptt_btn.released.connect(self._on_ptt_released)
        controls.addWidget(self.ptt_btn)

        self.stop_speech_btn = QPushButton("Stop Speaking")
        self.stop_speech_btn.setObjectName("stop")
        self.stop_speech_btn.clicked.connect(self._on_stop_speaking)
        controls.addWidget(self.stop_speech_btn)

        self.cancel_btn = QPushButton("Cancel Task")
        self.cancel_btn.clicked.connect(self._on_cancel_task)
        controls.addWidget(self.cancel_btn)

        # Language selector
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["en", "hi", "as", "ne"])
        pref = database.get_preference("language")
        if pref:
            idx = self.lang_combo.findText(pref)
            if idx >= 0:
                self.lang_combo.setCurrentIndex(idx)
        self.lang_combo.currentTextChanged.connect(self._on_language_changed)
        controls.addWidget(self.lang_combo)

        left_layout.addLayout(controls)

        # Activity panel
        left_layout.addWidget(QLabel("Recent activity"))
        self.activity_list = QListWidget()
        left_layout.addWidget(self.activity_list)

        main_layout.addWidget(left_frame, 3)

        # Right: settings and diagnostics
        right_frame = QFrame()
        right_layout = QVBoxLayout(right_frame)
        right_layout.addWidget(QLabel("Settings"))
        settings_btn = QPushButton("Open Settings")
        settings_btn.clicked.connect(self._open_settings)
        right_layout.addWidget(settings_btn)

        right_layout.addWidget(QLabel("Memory"))
        mem_btn = QPushButton("Open Memory DB")
        mem_btn.clicked.connect(self._open_memory)
        right_layout.addWidget(mem_btn)

        right_layout.addStretch()
        main_layout.addWidget(right_frame, 1)

        # Orb animation timer
        self._orb_phase = 0
        self._orb_timer = QTimer()
        self._orb_timer.timeout.connect(self._animate_orb)
        self._orb_timer.start(100)

    def _set_state(self, state: AssistantState):
        self.state = state
        self.status_label.setText(f"Status: {state.value}")

    def _animate_orb(self):
        # Simple pulsate by changing stylesheet opacity-like effect
        self._orb_phase = (self._orb_phase + 1) % 100
        # create gradient based on phase
        # for simplicity set background color hue shift
        v = 0.3 + 0.7 * abs(50 - self._orb_phase) / 50
        color = f"rgba(0, 200, 255, {v})"
        self.orb.setStyleSheet(f"background-color: {color}; border-radius: 60px;")

    def _append_chat(self, who: str, text: str):
        self.chat_view.append(f"{who}: {text}")

    def _on_send(self):
        text = self.input.text().strip()
        if not text:
            return
        self._append_chat("You", text)
        self._set_state(AssistantState.THINKING)
        # run assistant in background
        thread = FunctionThread(default_assistant.handle_text, text)
        thread.result.connect(self._on_assistant_result)
        thread.start()
        self.current_worker = thread
        self.input.clear()

    def _on_assistant_result(self, payload):
        if not payload.get("success"):
            self._append_chat("ANIS", f"Error: {payload.get('error')}")
            self._set_state(AssistantState.ERROR)
            return
        resp = payload.get("result")
        # resp is a Response dataclass or similar
        if hasattr(resp, "action") and resp.action:
            self.activity_list.addItem(f"Action requested: {resp.action}")
            if resp.requires_confirmation:
                confirm = QMessageBox.question(self, "Confirm action", f"{resp.text}\n\nProceed?", QMessageBox.Yes | QMessageBox.No)
                if confirm != QMessageBox.Yes:
                    self._append_chat("ANIS", "Action cancelled by user.")
                    self._set_state(AssistantState.IDLE)
                    return
            # execute action in background
            self._set_state(AssistantState.EXECUTING)
            thread = FunctionThread(action_registry.execute_action, resp.action, resp.action_args or {})
            thread.result.connect(self._on_action_result)
            thread.start()
            self.current_worker = thread
        else:
            self._append_chat("ANIS", resp.text)
            # speak response using TTS in background
            self._speak_text(resp.text)
            self._set_state(AssistantState.IDLE)

    def _on_action_result(self, payload):
        if not payload.get("success"):
            self._append_chat("ANIS", f"Action failed: {payload.get('error')}")
            self._set_state(AssistantState.ERROR)
            return
        result = payload.get("result")
        # result is action execute return value
        if isinstance(result, dict):
            summary = result.get("summary") or str(result)
            self._append_chat("ANIS", f"Done, sir. {summary}")
            self.activity_list.addItem(f"Executed: {summary}")
        else:
            self._append_chat("ANIS", f"Done, sir.")
        self._set_state(AssistantState.IDLE)

    def _speak_text(self, text: str):
        # Use background thread to call TTS.speak
        self._set_state(AssistantState.SPEAKING)
        thread = FunctionThread(self.tts.speak, text, self.lang_combo.currentText())
        thread.result.connect(self._on_tts_result)
        thread.start()
        self.current_tts_thread = thread

    def _on_tts_result(self, payload):
        if payload.get("success"):
            self._append_chat("(TTS)", payload.get("result"))
        else:
            self._append_chat("ANIS", f"TTS failed: {payload.get('error')}")
        self._set_state(AssistantState.IDLE)

    def _on_action_result_old(self, payload):
        pass

    # Microphone controls
    def _on_toggle_mic(self, checked: bool):
        if checked:
            # start listening
            if not self.microphone.is_available():
                QMessageBox.warning(self, "Microphone", "No microphone available.")
                self.micro_btn.setChecked(False)
                return
            self._set_state(AssistantState.LISTENING)
            # In mock mode we can simulate a phrase
            self.microphone.start_listening(self._on_transcript, phrase=None)
        else:
            self.microphone.stop_listening()
            self._set_state(AssistantState.IDLE)

    def _on_ptt_pressed(self):
        if not self.microphone.is_available():
            return
        self._set_state(AssistantState.LISTENING)
        # For push-to-talk in mock mode simulate a short phrase
        # If MOCK_MIC is enabled, the mic will call back immediately; otherwise we just set state
        self.microphone.start_listening(self._on_transcript, phrase="(mock) user speech via PTT")

    def _on_ptt_released(self):
        # stop listening; PTT recorded phrase already sent via callback
        self.microphone.stop_listening()
        # do not change state here; assistant will change after processing

    def _on_transcript(self, transcript: str):
        # called when microphone has a transcript
        self._append_chat("You (voice)", transcript)
        # run assistant on transcript
        self._set_state(AssistantState.THINKING)
        thread = FunctionThread(default_assistant.handle_text, transcript)
        thread.result.connect(self._on_assistant_result)
        thread.start()
        self.current_worker = thread

    def _on_stop_speaking(self):
        # Attempt to cancel current TTS thread
        if self.current_tts_thread and self.current_tts_thread.isRunning():
            # no real cancellation in mock, but we can terminate thread
            try:
                self.current_tts_thread.terminate()
            except Exception:
                pass
        self._set_state(AssistantState.IDLE)

    def _on_cancel_task(self):
        # Attempt to cancel current worker
        if self.current_worker and self.current_worker.isRunning():
            try:
                self.current_worker.terminate()
            except Exception:
                pass
            self._append_chat("ANIS", "Task cancelled by user.")
            self._set_state(AssistantState.IDLE)

    def _on_language_changed(self, lang: str):
        database.set_preference("language", lang)
        self._append_chat("ANIS", f"Language set to {lang}")

    def _open_settings(self):
        dlg = QMessageBox(self)
        dlg.setWindowTitle("Settings")
        ai_provider = database.get_preference("ai_provider") or "mock"
        dlg.setText(f"AI provider: {ai_provider}\nSpeech provider: mock\nWake-word: disabled by default")
        dlg.exec()

    def _open_memory(self):
        # simple display of preferences
        conn = database.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT key, value FROM preferences")
        rows = cur.fetchall()
        text = "\n".join([f"{k} = {v}" for k, v in rows]) or "(no preferences)"
        dlg = QMessageBox(self)
        dlg.setWindowTitle("Memory Preferences")
        dlg.setText(text)
        dlg.exec()
