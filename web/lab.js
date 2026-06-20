const replay = window.IMU_REPLAY || [];
const canvas = document.getElementById("scene");
const ctx = canvas.getContext("2d");
const frameEl = document.getElementById("frame");
const timeEl = document.getElementById("time");
const calibrationEl = document.getElementById("calibration");
const packetEl = document.getElementById("packet");
const toggle = document.getElementById("toggle");
const stepButton = document.getElementById("step");
const resetButton = document.getElementById("reset");
const scrubber = document.getElementById("scrubber");

let frameIndex = 0;
let playing = true;
let lastTick = performance.now();

const vertices = [
  [-1.2, -0.4, -0.22],
  [1.2, -0.4, -0.22],
  [1.2, 0.4, -0.22],
  [-1.2, 0.4, -0.22],
  [-1.2, -0.4, 0.22],
  [1.2, -0.4, 0.22],
  [1.2, 0.4, 0.22],
  [-1.2, 0.4, 0.22],
  [1.2, 0, 0],
  [1.75, 0, 0],
  [0, 0, 0.22],
  [0, 0, 0.75],
];

const edges = [
  [0, 1],
  [1, 2],
  [2, 3],
  [3, 0],
  [4, 5],
  [5, 6],
  [6, 7],
  [7, 4],
  [0, 4],
  [1, 5],
  [2, 6],
  [3, 7],
  [8, 9, "#d94f3d"],
  [10, 11, "#22945e"],
];

function rotate(point, quaternion) {
  const [w, x, y, z] = quaternion;
  const [px, py, pz] = point;
  const xx = x * x;
  const yy = y * y;
  const zz = z * z;
  const xy = x * y;
  const xz = x * z;
  const yz = y * z;
  const wx = w * x;
  const wy = w * y;
  const wz = w * z;
  return [
    (1 - 2 * (yy + zz)) * px + 2 * (xy - wz) * py + 2 * (xz + wy) * pz,
    2 * (xy + wz) * px + (1 - 2 * (xx + zz)) * py + 2 * (yz - wx) * pz,
    2 * (xz - wy) * px + 2 * (yz + wx) * py + (1 - 2 * (xx + yy)) * pz,
  ];
}

function project(point) {
  const [x, y, z] = point;
  const distance = 4.2;
  const scale = Math.min(canvas.width, canvas.height) * 0.36;
  const perspective = distance / (distance + y);
  return [
    canvas.width * 0.5 + x * scale * perspective,
    canvas.height * 0.53 - z * scale * perspective,
  ];
}

function drawLine(a, b, color = "#17243d", width = 5) {
  ctx.strokeStyle = color;
  ctx.lineWidth = width;
  ctx.lineCap = "round";
  ctx.beginPath();
  ctx.moveTo(a[0], a[1]);
  ctx.lineTo(b[0], b[1]);
  ctx.stroke();
}

function drawGrid() {
  const horizon = canvas.height * 0.76;
  ctx.strokeStyle = "#d6cab5";
  ctx.lineWidth = 1;
  for (let x = 0; x <= canvas.width; x += 48) {
    drawLine([x, horizon], [canvas.width / 2, canvas.height * 0.55], "#d6cab5", 1);
  }
  for (let offset = 0; offset < 220; offset += 28) {
    drawLine([0, horizon + offset], [canvas.width, horizon + offset], "#d6cab5", 1);
  }
}

function render() {
  const sample = replay[frameIndex] || replay[0];
  ctx.fillStyle = "#f3efe4";
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  drawGrid();

  if (sample) {
    const points = vertices.map((point) => project(rotate(point, sample.quaternion)));
    for (const [a, b, color] of edges) {
      drawLine(points[a], points[b], color || "#17243d", color ? 6 : 5);
    }
    frameEl.textContent = `${sample.index + 1}/${replay.length}`;
    timeEl.textContent = `${sample.timestampMs} ms`;
    calibrationEl.textContent = sample.calibration.join(",");
    packetEl.textContent = sample.csv;
    scrubber.max = String(Math.max(0, replay.length - 1));
    scrubber.value = String(frameIndex);
  }
}

function tick(now) {
  if (playing && replay.length && now - lastTick > 33) {
    frameIndex = (frameIndex + 1) % replay.length;
    lastTick = now;
    render();
  }
  requestAnimationFrame(tick);
}

toggle.addEventListener("click", () => {
  playing = !playing;
  toggle.textContent = playing ? "Pause" : "Play";
});

stepButton.addEventListener("click", () => {
  playing = false;
  toggle.textContent = "Play";
  frameIndex = (frameIndex + 1) % replay.length;
  render();
});

resetButton.addEventListener("click", () => {
  frameIndex = 0;
  render();
});

scrubber.addEventListener("input", () => {
  playing = false;
  toggle.textContent = "Play";
  frameIndex = Number(scrubber.value);
  render();
});

render();
requestAnimationFrame(tick);

