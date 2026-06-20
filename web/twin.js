import * as THREE from "three";

const replay = window.IMU_REPLAY || [];
const canvas = document.getElementById("twin-scene");
const frameEl = document.getElementById("twin-frame");
const lagEl = document.getElementById("twin-lag");
const springEl = document.getElementById("twin-spring");
const modeEl = document.getElementById("twin-mode");
const packetEl = document.getElementById("twin-packet");
const toggle = document.getElementById("twin-toggle");
const reset = document.getElementById("twin-reset");
const sourceMode = document.getElementById("source-mode");
const rollInput = document.getElementById("source-roll");
const pitchInput = document.getElementById("source-pitch");
const yawInput = document.getElementById("source-yaw");
const rollValue = document.getElementById("source-roll-value");
const pitchValue = document.getElementById("source-pitch-value");
const yawValue = document.getElementById("source-yaw-value");

const renderer = new THREE.WebGLRenderer({
  canvas,
  antialias: true,
  alpha: false,
  preserveDrawingBuffer: true,
});
renderer.setClearColor(0xf5efe2);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

const scene = new THREE.Scene();
scene.background = new THREE.Color(0xf5efe2);
scene.fog = new THREE.Fog(0xf5efe2, 8, 18);

const camera = new THREE.PerspectiveCamera(42, 1, 0.1, 100);
camera.position.set(0, 3.2, 7.6);
camera.lookAt(0, 0, 0);

const hemi = new THREE.HemisphereLight(0xffffff, 0xd7c8ae, 2.2);
scene.add(hemi);

const key = new THREE.DirectionalLight(0xffffff, 2.8);
key.position.set(-3, 5, 4);
scene.add(key);

const floor = new THREE.Mesh(
  new THREE.PlaneGeometry(12, 7, 1, 1),
  new THREE.MeshStandardMaterial({ color: 0xeadfca, roughness: 0.82 })
);
floor.rotation.x = -Math.PI / 2;
floor.position.y = -1.15;
scene.add(floor);

const grid = new THREE.GridHelper(12, 24, 0xb9ad98, 0xd7cbb7);
grid.position.y = -1.14;
scene.add(grid);

const source = makeBox(0xd94f3d, "Source IMU");
source.group.position.set(-2.7, 0, 0);
scene.add(source.group);

const reply = makeBox(0x1f8f62, "Response Body");
reply.group.position.set(0.85, 0, 0);
scene.add(reply.group);

const cableMaterial = new THREE.LineBasicMaterial({ color: 0x13203a, linewidth: 3 });
const cable = new THREE.Line(new THREE.BufferGeometry(), cableMaterial);
scene.add(cable);

const pulseMaterial = new THREE.MeshStandardMaterial({
  color: 0xd94f3d,
  emissive: 0xd94f3d,
  emissiveIntensity: 0.85,
});
const pulse = new THREE.Mesh(new THREE.SphereGeometry(0.07, 24, 12), pulseMaterial);
scene.add(pulse);

const replyPulseMaterial = new THREE.MeshStandardMaterial({
  color: 0x1f8f62,
  emissive: 0x1f8f62,
  emissiveIntensity: 0.75,
});
const replyPulse = new THREE.Mesh(new THREE.SphereGeometry(0.055, 24, 12), replyPulseMaterial);
scene.add(replyPulse);

let frameIndex = 0;
let playing = true;
let manualSource = false;
let previousTime = performance.now();
const replyQuaternion = new THREE.Quaternion();
const replyVelocity = new THREE.Vector3();
const replyBase = new THREE.Vector3(0.85, 0, 0);
const targetPosition = new THREE.Vector3();
const manual = { roll: 0, pitch: 0, yaw: 0 };

window.__TWIN_READY = false;
window.__TWIN_METRICS = {
  frame: 0,
  lagDegrees: 0,
  springEnergy: 0,
  leftX: source.group.position.x,
  rightX: reply.group.position.x,
  mode: "replay",
  manualRoll: 0,
  manualPitch: 0,
  manualYaw: 0,
};

function makeBox(color, label) {
  const group = new THREE.Group();
  const material = new THREE.MeshStandardMaterial({
    color,
    roughness: 0.52,
    metalness: 0.05,
  });
  const body = new THREE.Mesh(new THREE.BoxGeometry(1.18, 0.5, 0.34), material);
  body.castShadow = false;
  group.add(body);

  const edge = new THREE.LineSegments(
    new THREE.EdgesGeometry(body.geometry),
    new THREE.LineBasicMaterial({ color: 0x13203a })
  );
  group.add(edge);

  const nose = new THREE.Mesh(
    new THREE.BoxGeometry(0.32, 0.16, 0.18),
    new THREE.MeshStandardMaterial({ color: 0x13203a, roughness: 0.6 })
  );
  nose.position.x = 0.75;
  group.add(nose);

  const sprite = makeLabel(label);
  sprite.position.set(0, 0.62, 0);
  group.add(sprite);
  return { group, body };
}

function makeLabel(text) {
  const labelCanvas = document.createElement("canvas");
  labelCanvas.width = 256;
  labelCanvas.height = 64;
  const context = labelCanvas.getContext("2d");
  context.fillStyle = "rgba(255, 250, 240, 0.86)";
  context.fillRect(0, 0, labelCanvas.width, labelCanvas.height);
  context.fillStyle = "#13203a";
  context.font = "700 28px Avenir Next, sans-serif";
  context.textAlign = "center";
  context.textBaseline = "middle";
  context.fillText(text, labelCanvas.width / 2, labelCanvas.height / 2);
  const texture = new THREE.CanvasTexture(labelCanvas);
  const material = new THREE.SpriteMaterial({ map: texture, transparent: true });
  const sprite = new THREE.Sprite(material);
  sprite.scale.set(1.5, 0.38, 1);
  return sprite;
}

function quaternionFromSample(sample) {
  const [w, x, y, z] = sample.quaternion;
  return new THREE.Quaternion(x, y, z, w).normalize();
}

function resize() {
  const width = window.innerWidth;
  const height = window.innerHeight;
  renderer.setSize(width, height, false);
  camera.aspect = width / height;
  camera.updateProjectionMatrix();
}

function sourcePosition(sample) {
  const seconds = sample.timestampMs / 1000;
  return new THREE.Vector3(
    -2.7,
    Math.sin(seconds * 1.7) * 0.18,
    Math.cos(seconds * 1.1) * 0.24
  );
}

function manualQuaternion() {
  return new THREE.Quaternion().setFromEuler(
    new THREE.Euler(
      THREE.MathUtils.degToRad(manual.roll),
      THREE.MathUtils.degToRad(manual.pitch),
      THREE.MathUtils.degToRad(manual.yaw),
      "XYZ"
    )
  );
}

function manualSourcePosition() {
  return new THREE.Vector3(
    -2.7,
    THREE.MathUtils.clamp(manual.pitch / 75, -1, 1) * 0.22,
    THREE.MathUtils.clamp(manual.yaw / 180, -1, 1) * 0.3
  );
}

function manualPacket(quaternion) {
  return [
    quaternion.w,
    quaternion.x,
    quaternion.y,
    quaternion.z,
    3,
    3,
    3,
    3,
    Math.round(performance.now()),
  ]
    .map((value) => (Number.isInteger(value) ? value : value.toFixed(6)))
    .join(",");
}

function updateCable(progress) {
  const left = source.group.position.clone().add(new THREE.Vector3(0.7, 0, 0));
  const right = reply.group.position.clone().add(new THREE.Vector3(-0.7, 0, 0));
  const mid = left.clone().lerp(right, 0.5);
  mid.y -= 0.36;
  const curve = new THREE.CatmullRomCurve3([left, mid, right]);
  const points = curve.getPoints(32);
  cable.geometry.dispose();
  cable.geometry = new THREE.BufferGeometry().setFromPoints(points);
  pulse.position.copy(curve.getPoint(progress));
  replyPulse.position.copy(curve.getPoint(1 - ((progress * 0.62 + 0.18) % 1)));
}

function updateHud({ frameText, lagDegrees, springEnergy, packetText, mode }) {
  frameEl.textContent = frameText;
  lagEl.textContent = `${lagDegrees.toFixed(1)} deg`;
  springEl.textContent = springEnergy.toFixed(2);
  modeEl.textContent = mode;
  packetEl.textContent = packetText;
}

function updateControlLabels() {
  rollValue.textContent = `${manual.roll} deg`;
  pitchValue.textContent = `${manual.pitch} deg`;
  yawValue.textContent = `${manual.yaw} deg`;
  sourceMode.textContent = manualSource ? "Auto replay" : "Manual source";
  toggle.textContent = manualSource ? "Play replay" : playing ? "Pause" : "Play";
}

function setManualSource(enabled) {
  manualSource = enabled;
  playing = !enabled;
  updateControlLabels();
}

function step(now) {
  const dt = Math.min((now - previousTime) / 1000, 0.05);
  previousTime = now;

  if (playing && replay.length) {
    frameIndex = (frameIndex + 1) % replay.length;
  }

  const sample = replay[frameIndex] || replay[0];
  if (sample) {
    const sourceQuaternion = manualSource ? manualQuaternion() : quaternionFromSample(sample);
    const sourceTargetPosition = manualSource ? manualSourcePosition() : sourcePosition(sample);
    source.group.quaternion.copy(sourceQuaternion);
    source.group.position.copy(sourceTargetPosition);

    const followStrength = 1 - Math.exp(-dt * 5.5);
    replyQuaternion.slerp(sourceQuaternion, followStrength);
    reply.group.quaternion.copy(replyQuaternion);

    targetPosition.copy(replyBase);
    targetPosition.y = source.group.position.y * 0.72;
    targetPosition.z = source.group.position.z * 0.72;
    const displacement = targetPosition.clone().sub(reply.group.position);
    replyVelocity.addScaledVector(displacement, 18 * dt);
    replyVelocity.multiplyScalar(Math.max(0, 1 - 4.2 * dt));
    reply.group.position.addScaledVector(replyVelocity, dt);

    const lagDegrees = THREE.MathUtils.radToDeg(replyQuaternion.angleTo(sourceQuaternion));
    const springEnergy = displacement.length() * 10 + replyVelocity.length();
    const progress = manualSource ? (now / 1000) % 1 : ((sample.timestampMs / 1000) * 1.8) % 1;
    updateCable(progress);
    const mode = manualSource ? "manual" : "replay";
    updateHud({
      frameText: manualSource ? "manual" : `${sample.index + 1}/${replay.length}`,
      lagDegrees,
      springEnergy,
      packetText: manualSource ? manualPacket(sourceQuaternion) : sample.csv,
      mode,
    });

    window.__TWIN_READY = true;
    window.__TWIN_METRICS = {
      frame: sample.index + 1,
      lagDegrees,
      springEnergy,
      leftX: source.group.position.x,
      rightX: reply.group.position.x,
      leftY: source.group.position.y,
      leftZ: source.group.position.z,
      rightY: reply.group.position.y,
      rightZ: reply.group.position.z,
      mode,
      manualRoll: manual.roll,
      manualPitch: manual.pitch,
      manualYaw: manual.yaw,
    };
  }

  renderer.render(scene, camera);
  requestAnimationFrame(step);
}

toggle.addEventListener("click", () => {
  if (manualSource) {
    setManualSource(false);
    return;
  }
  playing = !playing;
  updateControlLabels();
});

reset.addEventListener("click", () => {
  frameIndex = 0;
  reply.group.position.copy(replyBase);
  replyVelocity.set(0, 0, 0);
  replyQuaternion.identity();
  manual.roll = 0;
  manual.pitch = 0;
  manual.yaw = 0;
  rollInput.value = "0";
  pitchInput.value = "0";
  yawInput.value = "0";
  updateControlLabels();
});

sourceMode.addEventListener("click", () => {
  setManualSource(!manualSource);
});

function bindControl(input, key) {
  input.addEventListener("input", () => {
    manual[key] = Number(input.value);
    setManualSource(true);
  });
}

bindControl(rollInput, "roll");
bindControl(pitchInput, "pitch");
bindControl(yawInput, "yaw");

window.addEventListener("resize", resize);
updateControlLabels();
resize();
requestAnimationFrame(step);
