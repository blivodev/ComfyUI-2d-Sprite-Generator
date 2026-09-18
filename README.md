# 👾 ComfyUI 2D Sprite, Animation & VFX Studio

> Complete end-to-end 2D Game Asset generation pipeline: 52 Fighting Game / Action Movesets, Non-Humanoid & Creature Adaptations, 2D VFX / Projectiles, Transparent Looping APNG/WebP Previews, Sprite Sheet Assembly, and an interactive Web UI.
> **Optimized for AMD Radeon RX (ROCm) and NVIDIA CUDA GPUs with ComfyUI.**

---

## 🌟 Key Features

* **52 Full Game Movesets**: Walk, Run, Jump, Double Jump, Crouch, Dash, Slide, Punches 1–3, Kicks 1–4, Air Attacks, Crouch Moves, Defenses, Status Conditions (Burn, Freeze, Poison, Paralyze, Stun), Item Interactions, and 4 Ultimate Specials.
* **🎨 Non-Pixel & Vector Art Mediums**: Generate true non-pixel art alongside pixel styles:
  * **Smooth HD Vector Art**: Crisp SVG/vector aesthetic with bold silhouettes and clean cell outlines.
  * **Detailed Hand-Drawn 2D**: High-definition hand-drawn arcade fighting game style with rich shading.
  * **Painterly 2D Concept Art**: Stylized textured fantasy illustration.
  * **Western Cartoon Brawler**: Expressive animated television show style.
  * **16-bit & 8-bit Retro Pixel Art**: Authentic chunky pixel art with optional nearest-neighbor snapping.
* **📐 Custom Sprite Frame Sizing**: Choose from preset defaults or specify exact custom dimensions:
  * `64x64` (Classic Retro)
  * `128x128` (Standard Indie Platformer)
  * `192x256` (Tall Arcade Fighter / Metroidvania)
  * `256x256` (HD 2D Character)
  * `512x512` (Ultra High-Res 2D Vector & Boss Sprites)
  * `Custom (W x H)`: Enter any custom resolution.
* **🐾 Non-Humanoid & Creature Support**: Instantly adapts the 52 moves for quadrupeds, beasts, monsters, mechs, slimes, and dragons (e.g. punches become claw strikes and bites; kicks become tail whips and rear bucking strikes; jump attacks become aerial pounces).
* **✨ 2D VFX, Projectiles & Particle Studio**: Generate animated fireballs, plasma orbs, ice shards, magic star missiles, sword slash arcs, impact bursts, explosions, shield barriers, and flame auras.
* **🚫 Clean Single Output (No Unwanted Duplicates)**: Single clean animation output by default (`standard`), with optional retro downscaled variants (`both`).
* **📦 Interactive Web Studio UI**:
  * **Character Studio Tab**: Configure character, art medium, frame dimensions, customize individual move prompts, and add unlimited custom animations.
  * **VFX & Projectiles Tab**: 15+ built-in particle & projectile presets or prompt any custom spell.
  * **Asset Library Tab**: Live transparent looping previews, download individual APNG/WebP/Sprite Sheets, or download the full character asset pack as a `.zip`.
  * **🔁 Single Move Re-run**: Re-roll any individual animation with custom seeds and modified prompts without regenerating the entire set.
* **✂️ Native Alpha Cutout**: Uses `BiRefNet_toonout` to extract 100% transparent backgrounds with clean anti-aliased or pixel-snapped edges.
* **⚡ AMD Radeon ROCm & NVIDIA CUDA Support**: Generates 4-frame animation strips in ~6–8 seconds on AMD Radeon RX 9060 XT (16GB) and compatible cards.

---

## 🎮 The 52 Animation Moveset

| Category | Count | Moves Included |
| :--- | :---: | :--- |
| **Locomotion & Mobility** | 8 | `idle`, `walk`, `run`, `jump`, `double jump`, `crouch`, `dash`, `slide` |
| **Standing Strikes** | 5 | `punch1`, `punch2`, `punch3`, `uppercut`, `dash punch` |
| **Standing Kicks** | 5 | `kick1`, `kick2`, `kick3`, `kick4`, `dash kick` |
| **Aerial Jump Attacks** | 8 | `jump punch1`, `jump punch2`, `jump punch3`, `jump kick1`, `jump kick2`, `jump kick3`, `jump kick4`, `jump block` |
| **Crouch Moves & Guards** | 9 | `crouch punch1`, `crouch punch2`, `crouch punch3`, `crouch kick1`, `crouch kick2`, `crouch kick3`, `crouch kick4`, `crouch block`, `block` |
| **Items & Projectiles** | 5 | `throw item`, `pick up item`, `drink potion`, `fire projectile`, `grapple` |
| **Hits, Statuses & States** | 8 | `get hit`, `get stunned`, `get paralyzed`, `get poisoned`, `get burned`, `get frozen`, `death`, `stand up` |
| **Special Moves** | 4 | `special move 1`, `special move 2`, `special move 3`, `special move 4 (ultimate)` |

---

## 🚀 Quick Start

### 1. Requirements & Prerequisites
* [ComfyUI](https://github.com/comfyanonymous/ComfyUI) running locally on `http://127.0.0.1:8188`
* Recommended Diffusion Model: `z_image_turbo_bf16.safetensors` (or SDXL / SD1.5 checkpoints)
* Text Encoder: `qwen_3_4b.safetensors` (or standard CLIP)
* Background Cutout: `BiRefNet_toonout.safetensors` (installed via `comfyui-rmbg`)

### 2. Installation
1. Clone this repository into your ComfyUI setup:
   ```bash
   git clone https://github.com/YOUR_USERNAME/ComfyUI-2d-Sprite-Generator.git
   cd ComfyUI-2d-Sprite-Generator
   ```
2. Copy `custom_nodes/comfyui-sprite-animator` into your ComfyUI `custom_nodes/` directory:
   ```bash
   cp -r custom_nodes/comfyui-sprite-animator /path/to/ComfyUI/custom_nodes/
   ```
3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### 3. Launching the Studio Web UI
* **On Windows**: Double-click `Launch_Sprite_Studio_UI.bat`
* **From Terminal**:
  ```bash
  python app.py
  ```
Open your browser to: **`http://127.0.0.1:8190`**

---

## 🛠️ Included Workflows

All ready-to-use workflows are located in [`workflows/`](workflows/):

1. **`2D_Sprite_and_Animation_Studio.json`**:
   The full automated character sprite sheet and animation generator with background removal and APNG loop export.
2. **`2D_VFX_Projectile_and_Particle_Studio.json`**:
   Optimized pipeline for 2D glowing projectiles, plasma orbs, explosions, and combat slash arcs.
3. **`Animate_Existing_2D_Sprite.json`**:
   Upload an existing character sprite or concept art, cut out the background, and slice/generate animated loops.

---

## 📦 What Gets Exported

For each animation or VFX generated, the studio automatically saves:

1. **`<prefix>_anim.png`**: High-quality Animated PNG (APNG) with 100% alpha transparency. Plays seamlessly in game engines (Unity, Godot, Unreal, GameMaker), web browsers, and Discord.
2. **`<prefix>_webp.webp`**: Lightweight animated WebP loop preview.
3. **`<prefix>_spritesheet.png`**: Master transparent Sprite Sheet PNG with zero cell padding, ready for game engines.
4. **`<prefix>_retro_anim.png`** *(Optional)*: Snapped 16-bit retro pixel art with nearest-neighbor scaling.

---

## 💻 CLI Batch Generation

You can also run batch generations directly from the command line:

```bash
python generate_character_pack.py \
  --name "cyber_ninja" \
  --character "a swift cyberpunk shadow ninja in dark armor with glowing blue katanas" \
  --seed 424242 \
  --count 52
```

---

## 📜 License

MIT License. Free for commercial and non-commercial game development.
