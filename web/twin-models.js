import * as THREE from "three";
import { RoundedBoxGeometry } from "three/examples/jsm/geometries/RoundedBoxGeometry.js";

export function makeSourceRig() {
  const group = new THREE.Group();
  const atom = mesh(
    new RoundedBoxGeometry(1.0, 1.0, 0.4, 5, 0.08),
    { color: 0xd8dce0, roughness: 0.42, metalness: 0.08 }
  );
  atom.castShadow = true;
  group.add(atom);

  const face = mesh(
    new RoundedBoxGeometry(0.76, 0.76, 0.08, 4, 0.05),
    { color: 0x30384a, roughness: 0.54 }
  );
  face.position.z = 0.24;
  face.castShadow = true;
  group.add(face);

  const led = mesh(
    new RoundedBoxGeometry(0.16, 0.16, 0.04, 3, 0.025),
    { color: 0xff3d2d, emissive: 0xff3d2d, emissiveIntensity: 1.2, roughness: 0.35 }
  );
  led.position.set(-0.22, 0.2, 0.31);
  group.add(led);

  const button = mesh(new THREE.CylinderGeometry(0.12, 0.12, 0.045, 32), {
    color: 0x111827,
    roughness: 0.34,
  });
  button.rotation.x = Math.PI / 2;
  button.position.set(0.21, -0.2, 0.31);
  group.add(button);

  const usb = mesh(
    new RoundedBoxGeometry(0.28, 0.09, 0.12, 3, 0.02),
    { color: 0x161b22, roughness: 0.3, metalness: 0.25 }
  );
  usb.position.set(0, -0.56, 0.03);
  group.add(usb);

  const grove = mesh(
    new RoundedBoxGeometry(0.34, 0.13, 0.13, 3, 0.02),
    { color: 0xf4f1df, roughness: 0.62 }
  );
  grove.position.set(0.56, 0, 0.02);
  group.add(grove);

  const board = mesh(
    new RoundedBoxGeometry(0.78, 0.58, 0.08, 3, 0.025),
    { color: 0x245f52, roughness: 0.48, metalness: 0.04 }
  );
  board.position.set(0, 0.74, -0.03);
  board.castShadow = true;
  group.add(board);

  const sensor = mesh(
    new RoundedBoxGeometry(0.2, 0.2, 0.07, 3, 0.018),
    { color: 0x1a202c, roughness: 0.4, metalness: 0.15 }
  );
  sensor.position.set(0.16, 0.74, 0.07);
  group.add(sensor);

  for (let index = 0; index < 5; index += 1) {
    const pin = mesh(new THREE.BoxGeometry(0.035, 0.12, 0.035), {
      color: 0xd4a84e,
      roughness: 0.26,
      metalness: 0.5,
    });
    pin.position.set(-0.31 + index * 0.08, 1.04, 0.08);
    group.add(pin);
  }

  addRotationRings(group, 0.83);
  const sprite = makeLabel("ATOM + BNO055");
  sprite.position.set(0, 1.28, 0);
  group.add(sprite);
  return { group };
}

export function makeResponseRig() {
  const group = new THREE.Group();
  const chassis = mesh(
    new RoundedBoxGeometry(1.28, 0.48, 0.38, 5, 0.08),
    { color: 0x16815a, roughness: 0.44, metalness: 0.08 }
  );
  chassis.castShadow = true;
  group.add(chassis);

  const ghost = new THREE.Mesh(
    new RoundedBoxGeometry(1.42, 0.62, 0.5, 5, 0.08),
    new THREE.MeshStandardMaterial({
      color: 0x7bd7af,
      transparent: true,
      opacity: 0.18,
      roughness: 0.3,
      metalness: 0.02,
    })
  );
  group.add(ghost);

  const nose = mesh(
    new RoundedBoxGeometry(0.34, 0.2, 0.22, 3, 0.035),
    { color: 0x172033, roughness: 0.46 }
  );
  nose.position.x = 0.78;
  group.add(nose);

  const antenna = mesh(new THREE.CylinderGeometry(0.025, 0.025, 0.54, 16), {
    color: 0x172033,
    roughness: 0.36,
  });
  antenna.rotation.z = -0.7;
  antenna.position.set(-0.54, 0.32, 0.02);
  group.add(antenna);

  const sprite = makeLabel("Response body");
  sprite.position.set(0, 0.72, 0);
  group.add(sprite);
  return { group };
}

function mesh(geometry, materialOptions) {
  return new THREE.Mesh(geometry, new THREE.MeshStandardMaterial(materialOptions));
}

function addRotationRings(group, radius) {
  const specs = [
    [0xd94f3d, [0, Math.PI / 2, 0]],
    [0x1f8f62, [Math.PI / 2, 0, 0]],
    [0x2d6cdf, [0, 0, 0]],
  ];
  for (const [color, rotation] of specs) {
    const ring = new THREE.Mesh(
      new THREE.TorusGeometry(radius, 0.01, 8, 96),
      new THREE.MeshBasicMaterial({ color, transparent: true, opacity: 0.42 })
    );
    ring.rotation.set(...rotation);
    group.add(ring);
  }
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
