import os

ROOT = os.path.dirname(os.path.dirname(__file__))
AVATAR_DIR = os.path.join(ROOT, 'ui', 'avatar')
INDEX = os.path.join(AVATAR_DIR, 'index.html')
JS = os.path.join(AVATAR_DIR, 'avatar.js')


def test_avatar_files_exist():
    assert os.path.isdir(AVATAR_DIR), 'ui/avatar directory should exist'
    assert os.path.isfile(INDEX), 'ui/avatar/index.html should exist'
    assert os.path.isfile(JS), 'ui/avatar/avatar.js should exist'


def test_index_links_avatar_script_and_threejs():
    with open(INDEX, 'r', encoding='utf-8') as f:
        html = f.read()

    assert 'three.min.js' in html, 'Three.js script should be loaded'
    assert './avatar.js' in html or 'avatar.js' in html, 'avatar.js should be referenced'


def test_js_has_voice_and_socket_support():
    with open(JS, 'r', encoding='utf-8') as f:
        js = f.read()

    assert 'WebSocket' in js or 'ws://localhost:8765' in js, 'socket logic should be present'
    assert 'SpeechRecognition' in js or 'speechSynthesis' in js, 'voice interaction should be present'
    assert 'dispatchCommand' in js, 'command handling should be present'
