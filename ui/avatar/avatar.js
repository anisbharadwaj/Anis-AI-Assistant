const viewport = document.getElementById('viewport');
const transcriptEl = document.getElementById('transcript');
const liveStateEl = document.getElementById('live-state');
const connectionPill = document.getElementById('connection-pill');
const connectionText = document.getElementById('connection-text');
const statusDot = document.getElementById('status-dot');

let scene, camera, renderer, avatarGroup, mouthMesh, haloMesh, dotParticles;
let animationState = 'idle';
let socket = null;
let recognition = null;
let lastCommandAt = 0;
let socketRetryTimer = null;

function setConnection(connected) {
  if (connected) {
    connectionPill.style.background = '#34d399';
    connectionPill.style.boxShadow = '0 0 10px rgba(52,211,153,0.7)';
    connectionText.textContent = 'Connected';
    statusDot.style.background = '#34d399';
    statusDot.style.boxShadow = '0 0 12px rgba(52,211,153,0.9)';
  } else {
    connectionPill.style.background = '#f87171';
    connectionPill.style.boxShadow = '0 0 10px rgba(248,113,113,0.7)';
    connectionText.textContent = 'Offline';
    statusDot.style.background = '#34d399';
    statusDot.style.boxShadow = '0 0 10px rgba(52,211,153,0.9)';
  }
}

function updateTranscript(text) {
  transcriptEl.textContent = text;
}

function setLiveState(state) {
  animationState = state;
  liveStateEl.textContent = state.toUpperCase();
}

function initThree() {
  scene = new THREE.Scene();
  scene.background = new THREE.Color(0x020812);
  scene.fog = new THREE.Fog(0x020812, 6, 18);

  camera = new THREE.PerspectiveCamera(40, viewport.clientWidth / viewport.clientHeight, 0.1, 100);
  camera.position.set(0, 1.2, 5.6);

  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.setSize(viewport.clientWidth, viewport.clientHeight);
  viewport.appendChild(renderer.domElement);

  const ambientLight = new THREE.AmbientLight(0x7dd3fc, 1.1);
  scene.add(ambientLight);

  const keyLight = new THREE.PointLight(0x67e8f9, 2.2, 25, 2);
  keyLight.position.set(2.5, 3.2, 4.5);
  scene.add(keyLight);

  const rimLight = new THREE.PointLight(0x1d4ed8, 1.6, 25, 2);
  rimLight.position.set(-3.5, 1.5, -2.8);
  scene.add(rimLight);

  avatarGroup = new THREE.Group();
  scene.add(avatarGroup);

  const bodyMat = new THREE.MeshPhysicalMaterial({
    color: 0x5eead4,
    emissive: 0x0f766e,
    emissiveIntensity: 0.55,
    metalness: 0.65,
    roughness: 0.18,
    transparent: true,
    opacity: 0.95,
  });

  const headMat = new THREE.MeshPhysicalMaterial({
    color: 0x7dd3fc,
    emissive: 0x164e63,
    emissiveIntensity: 0.55,
    metalness: 0.4,
    roughness: 0.3,
    transparent: true,
    opacity: 0.96,
  });

  const faceMat = new THREE.MeshBasicMaterial({ color: 0xcaf6ff, transparent: true, opacity: 0.9 });

  const body = new THREE.Mesh(new THREE.SphereGeometry(1.0, 32, 32), bodyMat);
  body.scale.set(1.15, 1.35, 0.92);
  body.position.y = 0.1;
  avatarGroup.add(body);

  const head = new THREE.Mesh(new THREE.SphereGeometry(0.72, 32, 32), headMat);
  head.position.set(0, 1.75, 0.2);
  avatarGroup.add(head);

  const face = new THREE.Mesh(new THREE.SphereGeometry(0.52, 32, 32), faceMat);
  face.scale.set(0.82, 0.94, 0.78);
  face.position.set(0, 1.72, 0.75);
  avatarGroup.add(face);

  const eyeLeft = new THREE.Mesh(new THREE.SphereGeometry(0.06, 16, 16), new THREE.MeshBasicMaterial({ color: 0x082f49 }));
  eyeLeft.position.set(-0.17, 1.8, 1.15);
  avatarGroup.add(eyeLeft);

  const eyeRight = eyeLeft.clone();
  eyeRight.position.x = 0.17;
  avatarGroup.add(eyeRight);

  mouthMesh = new THREE.Mesh(
    new THREE.BoxGeometry(0.32, 0.08, 0.08),
    new THREE.MeshBasicMaterial({ color: 0xfef3c7 })
  );
  mouthMesh.position.set(0, 1.38, 1.12);
  avatarGroup.add(mouthMesh);

  const torsoGlow = new THREE.Mesh(
    new THREE.TorusGeometry(1.15, 0.06, 12, 64),
    new THREE.MeshBasicMaterial({ color: 0x67e8f9, transparent: true, opacity: 0.7 })
  );
  torsoGlow.rotation.x = Math.PI / 2;
  torsoGlow.position.y = -0.9;
  avatarGroup.add(torsoGlow);

  haloMesh = new THREE.Mesh(
    new THREE.TorusGeometry(2.15, 0.04, 12, 80),
    new THREE.MeshBasicMaterial({ color: 0x7dd3fc, transparent: true, opacity: 0.8 })
  );
  haloMesh.rotation.x = Math.PI / 2;
  haloMesh.position.y = 2.5;
  avatarGroup.add(haloMesh);

  const particleGeometry = new THREE.BufferGeometry();
  const count = 180;
  const positions = new Float32Array(count * 3);
  for (let i = 0; i < count * 3; i += 3) {
    positions[i] = (Math.random() - 0.5) * 8;
    positions[i + 1] = (Math.random() - 0.5) * 6;
    positions[i + 2] = (Math.random() - 0.5) * 8;
  }
  particleGeometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
  const particleMat = new THREE.PointsMaterial({ color: 0x67e8f9, size: 0.045, transparent: true, opacity: 0.8 });
  dotParticles = new THREE.Points(particleGeometry, particleMat);
  scene.add(dotParticles);

  animateFrame();
  window.addEventListener('resize', onResize);
}

function animateFrame() {
  requestAnimationFrame(animateFrame);
  const t = performance.now() * 0.001;

  if (avatarGroup) {
    avatarGroup.rotation.y = t * 0.28;
    avatarGroup.position.y = Math.sin(t * 1.4) * 0.18;

    if (animationState === 'speaking') {
      mouthMesh.scale.y = 1 + Math.abs(Math.sin(t * 18)) * 1.8;
      avatarGroup.scale.setScalar(1.05 + Math.sin(t * 12) * 0.04);
      haloMesh.material.opacity = 0.9;
    } else if (animationState === 'listening') {
      mouthMesh.scale.y = 0.8 + Math.abs(Math.sin(t * 8)) * 0.5;
      avatarGroup.scale.setScalar(1.02 + Math.sin(t * 6) * 0.02);
      haloMesh.material.opacity = 0.7;
    } else {
      mouthMesh.scale.y = 0.5;
      avatarGroup.scale.setScalar(1);
      haloMesh.material.opacity = 0.75;
    }

    if (dotParticles) {
      dotParticles.rotation.y += 0.0015;
      dotParticles.rotation.x = Math.sin(t * 0.7) * 0.2;
    }
  }

  if (renderer && scene && camera) renderer.render(scene, camera);
}

function onResize() {
  if (!renderer || !camera) return;
  camera.aspect = viewport.clientWidth / viewport.clientHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(viewport.clientWidth, viewport.clientHeight);
}

function connectSocket() {
  try {
    socket = new WebSocket('ws://localhost:8765');
  } catch (error) {
    setConnection(false);
    return;
  }

  socket.addEventListener('open', () => {
    setConnection(true);
  });

  socket.addEventListener('message', (event) => {
    try {
      const data = JSON.parse(event.data);
      if (data && data.text) updateTranscript(String(data.text));
      if (data && data.state) setLiveState(String(data.state));
    } catch (error) {
      console.warn('Malformed websocket payload', error);
    }
  });

  socket.addEventListener('close', () => {
    setConnection(false);
    if (!socketRetryTimer) {
      socketRetryTimer = setTimeout(() => {
        socketRetryTimer = null;
        connectSocket();
      }, 2500);
    }
  });

  socket.addEventListener('error', () => {
    setConnection(false);
  });
}

function sanitizeCommand(raw) {
  if (typeof raw !== 'string') return null;
  const cleaned = raw.trim();
  if (!cleaned) return null;
  if (cleaned.length > 2000) return null;
  return cleaned;
}

function handleLocalCommand(commandText) {
  const text = commandText.toLowerCase();

  if (text.includes('hello') || text.includes('hi')) {
    speak('Hello, I am Anis. I am here to help you.');
    return;
  }

  if (text.includes('open youtube') || text.includes('open yt')) {
    speak('Opening YouTube now.');
    window.open('https://www.youtube.com', '_blank');
    return;
  }

  if (text.includes('system status') || text.includes('performance')) {
    speak('Your system is running normally, and I am ready to help you.');
    return;
  }

  speak('I heard you. I can help with a few tasks locally, like opening YouTube or responding to simple questions.');
}

function dispatchCommand(rawText) {
  const command = sanitizeCommand(rawText);
  if (!command) return;

  const now = Date.now();
  if (now - lastCommandAt < 700) return;
  lastCommandAt = now;

  const lowered = command.toLowerCase();
  if (!lowered.includes('anis')) {
    updateTranscript('I heard you. Please say “Anis” before a command so I know you are speaking to me.');
    return;
  }

  updateTranscript(command);
  setLiveState('listening');

  if (socket && socket.readyState === WebSocket.OPEN) {
    socket.send(JSON.stringify({ type: 'command', text: command }));
  } else {
    handleLocalCommand(command);
  }
}

function speak(text) {
  const value = String(text || '').trim();
  if (!value) return;

  setLiveState('speaking');
  updateTranscript(value);

  if ('speechSynthesis' in window) {
    const utterance = new SpeechSynthesisUtterance(value);
    utterance.rate = 1.02;
    utterance.pitch = 1.2;
    utterance.lang = 'en-US';
    utterance.onend = () => setLiveState('idle');
    utterance.onerror = () => setLiveState('idle');
    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(utterance);
  } else {
    setLiveState('idle');
  }
}

function startListening() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    updateTranscript('This browser does not support voice recognition. Use a Chromium-based browser like Chrome or Edge.');
    return;
  }

  if (!recognition) {
    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-US';

    recognition.onstart = () => {
      setLiveState('listening');
      updateTranscript('Listening…');
    };

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      dispatchCommand(transcript);
    };

    recognition.onerror = (event) => {
      updateTranscript(`Voice capture failed: ${event.error || 'unknown error'}`);
      setLiveState('idle');
    };

    recognition.onend = () => {
      setLiveState('idle');
    };
  }

  try {
    recognition.start();
  } catch (error) {
    recognition.stop();
    setTimeout(() => recognition.start(), 150);
  }
}

document.getElementById('mic-btn').addEventListener('click', startListening);
document.getElementById('speak-btn').addEventListener('click', () => speak('Hello, I am Anis. I am ready to help you.'));
document.getElementById('stop-btn').addEventListener('click', () => {
  if (recognition) recognition.stop();
  window.speechSynthesis?.cancel();
  setLiveState('idle');
});

initThree();
setConnection(false);
connectSocket();
updateTranscript('Say: “Anis, open YouTube” or tap the mic.');
