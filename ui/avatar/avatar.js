const viewport = document.getElementById('viewport');
const transcriptEl = document.getElementById('transcript');
const liveStateEl = document.getElementById('live-state');
const connectionPill = document.getElementById('connection-pill');
const connectionText = document.getElementById('connection-text');
const statusDot = document.getElementById('status-dot');

let scene, camera, renderer, avatarGroup, mouthMesh, haloMesh, faceShadow, dotParticles;
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

function setLiveState(state) {
  animationState = state;
  liveStateEl.textContent = state.toUpperCase();
}

function updateTranscript(text) {
  transcriptEl.textContent = text;
}

function initThree() {
  scene = new THREE.Scene();
  scene.background = new THREE.Color(0x020812);
  scene.fog = new THREE.Fog(0x020812, 6, 18);

  camera = new THREE.PerspectiveCamera(40, viewport.clientWidth / viewport.clientHeight, 0.1, 100);
  camera.position.set(0, 1.2, 5.8);

  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.setSize(viewport.clientWidth, viewport.clientHeight);
  viewport.appendChild(renderer.domElement);

  const ambientLight = new THREE.AmbientLight(0x9cc9ff, 1.15);
  scene.add(ambientLight);

  const keyLight = new THREE.DirectionalLight(0xfff3e7, 1.8);
  keyLight.position.set(2.4, 4.5, 4.3);
  scene.add(keyLight);

  const rimLight = new THREE.PointLight(0x5fd8ff, 1.6, 30, 2);
  rimLight.position.set(-3.2, 2.2, -2.5);
  scene.add(rimLight);

  const fillLight = new THREE.PointLight(0x1d4ed8, 0.8, 30, 2);
  fillLight.position.set(0, 1.5, -4.0);
  scene.add(fillLight);

  avatarGroup = new THREE.Group();
  scene.add(avatarGroup);

  const skinMat = new THREE.MeshPhysicalMaterial({
    color: 0xd9b59a,
    emissive: 0x4a2e23,
    emissiveIntensity: 0.15,
    metalness: 0.08,
    roughness: 0.72,
    transparent: true,
    opacity: 0.98
  });

  const cheekMat = new THREE.MeshStandardMaterial({
    color: 0xe8c5a6,
    roughness: 0.8,
    metalness: 0.03
  });

  const eyeMat = new THREE.MeshPhysicalMaterial({
    color: 0x111827,
    roughness: 0.25,
    metalness: 0.45
  });

  const bodyMat = new THREE.MeshPhysicalMaterial({
    color: 0x6ec7ff,
    emissive: 0x0d5f77,
    emissiveIntensity: 0.35,
    metalness: 0.62,
    roughness: 0.22,
    transparent: true,
    opacity: 0.96
  });

  const body = new THREE.Mesh(new THREE.SphereGeometry(1.0, 48, 48), bodyMat);
  body.scale.set(1.16, 1.42, 0.9);
  body.position.y = 0.18;
  avatarGroup.add(body);

  const head = new THREE.Mesh(new THREE.SphereGeometry(0.72, 48, 48), skinMat);
  head.scale.set(1.02, 1.12, 0.96);
  head.position.set(0, 1.76, 0.1);
  avatarGroup.add(head);

  const jaw = new THREE.Mesh(new THREE.SphereGeometry(0.48, 48, 32), cheekMat);
  jaw.scale.set(1.0, 0.72, 0.82);
  jaw.position.set(0, 1.28, 0.3);
  avatarGroup.add(jaw);

  const cheekLeft = new THREE.Mesh(new THREE.SphereGeometry(0.12, 20, 20), cheekMat);
  cheekLeft.position.set(-0.28, 1.52, 0.72);
  avatarGroup.add(cheekLeft);

  const cheekRight = cheekLeft.clone();
  cheekRight.position.x = 0.28;
  avatarGroup.add(cheekRight);

  const eyeLeft = new THREE.Mesh(new THREE.SphereGeometry(0.065, 20, 20), eyeMat);
  eyeLeft.position.set(-0.17, 1.8, 0.95);
  avatarGroup.add(eyeLeft);

  const eyeRight = eyeLeft.clone();
  eyeRight.position.x = 0.17;
  avatarGroup.add(eyeRight);

  const eyeGlow = new THREE.Mesh(
    new THREE.SphereGeometry(0.028, 16, 16),
    new THREE.MeshBasicMaterial({ color: 0xf0f9ff })
  );
  eyeGlow.position.set(-0.17, 1.82, 1.02);
  avatarGroup.add(eyeGlow);

  const eyeGlow2 = eyeGlow.clone();
  eyeGlow2.position.x = 0.17;
  avatarGroup.add(eyeGlow2);

  const nose = new THREE.Mesh(
    new THREE.ConeGeometry(0.08, 0.28, 18),
    new THREE.MeshStandardMaterial({ color: 0xd7b08c, roughness: 0.8, metalness: 0.02 })
  );
  nose.rotation.x = Math.PI / 2;
  nose.position.set(0, 1.58, 1.08);
  avatarGroup.add(nose);

  mouthMesh = new THREE.Mesh(
    new THREE.SphereGeometry(0.15, 20, 14, 0, Math.PI * 2, 0, Math.PI / 2),
    new THREE.MeshStandardMaterial({
      color: 0xb45309,
      roughness: 0.85,
      metalness: 0.08
    })
  );
  mouthMesh.scale.set(1.35, 0.72, 0.8);
  mouthMesh.position.set(0, 1.34, 1.08);
  avatarGroup.add(mouthMesh);

  const torsoGlow = new THREE.Mesh(
    new THREE.TorusGeometry(1.15, 0.06, 12, 64),
    new THREE.MeshBasicMaterial({ color: 0x67e8f9, transparent: true, opacity: 0.7 })
  );
  torsoGlow.rotation.x = Math.PI / 2;
  torsoGlow.position.y = -0.82;
  avatarGroup.add(torsoGlow);

  haloMesh = new THREE.Mesh(
    new THREE.TorusGeometry(2.2, 0.04, 12, 90),
    new THREE.MeshBasicMaterial({ color: 0x7dd3fc, transparent: true, opacity: 0.8 })
  );
  haloMesh.rotation.x = Math.PI / 2;
  haloMesh.position.y = 2.4;
  avatarGroup.add(haloMesh);

  const shadowGeo = new THREE.CircleGeometry(1.55, 48);
  const shadowMat = new THREE.MeshBasicMaterial({ color: 0x000000, transparent: true, opacity: 0.3 });
  faceShadow = new THREE.Mesh(shadowGeo, shadowMat);
  faceShadow.rotation.x = -Math.PI / 2;
  faceShadow.position.y = -1.7;
  scene.add(faceShadow);

  const particleGeometry = new THREE.BufferGeometry();
  const count = 180;
  const positions = new Float32Array(count * 3);

  for (let i = 0; i < count * 3; i += 3) {
    positions[i] = (Math.random() - 0.5) * 8;
    positions[i + 1] = (Math.random() - 0.5) * 6;
    positions[i + 2] = (Math.random() - 0.5) * 8;
  }

  particleGeometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
  const particleMat = new THREE.PointsMaterial({
    color: 0x67e8f9,
    size: 0.045,
    transparent: true,
    opacity: 0.8
  });

  dotParticles = new THREE.Points(particleGeometry, particleMat);
  scene.add(dotParticles);

  animateFrame();
  window.addEventListener('resize', onResize);
}

function animateFrame() {
  requestAnimationFrame(animateFrame);

  const t = performance.now() * 0.001;

  if (avatarGroup) {
    avatarGroup.rotation.y = t * 0.24;
    avatarGroup.position.y = Math.sin(t * 1.25) * 0.18;

    if (animationState === 'speaking') {
      mouthMesh.scale.y = 0.9 + Math.abs(Math.sin(t * 18)) * 1.8;
      mouthMesh.scale.x = 1.1 + Math.abs(Math.sin(t * 12)) * 0.3;
      avatarGroup.scale.setScalar(1.05 + Math.sin(t * 12) * 0.04);
      haloMesh.material.opacity = 0.9;
    } else if (animationState === 'listening') {
      mouthMesh.scale.y = 0.8 + Math.abs(Math.sin(t * 9)) * 0.4;
      avatarGroup.scale.setScalar(1.02 + Math.sin(t * 7) * 0.02);
      haloMesh.material.opacity = 0.75;
    } else {
      mouthMesh.scale.y = 0.6;
      mouthMesh.scale.x = 1.1;
      avatarGroup.scale.setScalar(1.0);
      haloMesh.material.opacity = 0.7;
    }
  }

  if (dotParticles) {
    dotParticles.rotation.y += 0.0015;
    dotParticles.rotation.x = Math.sin(t * 0.7) * 0.2;
  }

  if (faceShadow) {
    faceShadow.material.opacity = 0.28 + Math.sin(t * 1.6) * 0.05;
  }

  renderer.render(scene, camera);
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
    utterance.pitch = 1.15;
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
    updateTranscript('This browser does not support voice recognition. Use Chrome or Edge.');
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
    if (recognition) {
      recognition.stop();
      setTimeout(() => recognition.start(), 150);
    }
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
