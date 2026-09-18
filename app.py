"""
🎮 2D Sprite, Animation & VFX Studio
A unified web app for generating 52-move game animations, 2D VFX, projectiles, and particle sheets
Powered by ComfyUI (Z-Image Turbo + BiRefNet Toonout) on AMD Radeon RX (ROCm) & NVIDIA CUDA.
Supports Local LLM Prompt Optimization (Ollama) & Reference Image Conditioning.
"""

import os
import sys
import json
import time
import uuid
import base64
import urllib.request
import urllib.parse
import urllib.error
import zipfile
import threading
import subprocess
from http.server import HTTPServer, BaseHTTPRequestHandler

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

COMFY_URL = "http://127.0.0.1:8188"
OLLAMA_URL = "http://127.0.0.1:11434"
PORT = 8190

SHARED_DIR = r"C:\Users\USER\AppData\Local\Comfy-Desktop\ComfyUI-Shared"
OUTPUT_DIR = os.path.join(SHARED_DIR, "output")
INPUT_DIR = os.path.join(SHARED_DIR, "input")
COMFY_INPUT_DIR = r"C:\Users\USER\AppData\Local\Comfy-Desktop\ComfyUI-Installs\ComfyUI\ComfyUI\input"

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(INPUT_DIR, exist_ok=True)
if os.path.exists(COMFY_INPUT_DIR):
    os.makedirs(COMFY_INPUT_DIR, exist_ok=True)

# 52 Base Animations
DEFAULT_52_ANIMATIONS = [
    # Locomotion & Mobility (8)
    {"id": "idle", "name": "Idle", "cat": "Locomotion", "fps": 5.0,
     "human": "standing idle breathing animation, subtle bobbing stance, relaxed breathing motion frames",
     "creature": "creature idle breathing animation, subtle chest rise and fall, tail swishing slowly, grounded stance"},
    {"id": "walk", "name": "Walk", "cat": "Locomotion", "fps": 6.0,
     "human": "side view walking cycle, sequential walking footsteps motion, character moving forward",
     "creature": "creature quadruped walking cycle, beast prowling footsteps locomotion moving forward"},
    {"id": "run", "name": "Run", "cat": "Locomotion", "fps": 8.0,
     "human": "running cycle, forward running fast sprint motion, dynamic running footsteps",
     "creature": "fast galloping running sprint, quadruped beast bounding forward in swift running cycle"},
    {"id": "jump", "name": "Jump", "cat": "Locomotion", "fps": 6.0,
     "human": "jumping up into air, crouch anticipation leap into airborne apex pose",
     "creature": "creature leaping leap into air, beast coiled crouch spring leap into airborne pose"},
    {"id": "double_jump", "name": "Double Jump", "cat": "Locomotion", "fps": 7.0,
     "human": "aerial double jump, secondary mid-air flip spin leap with energy trail",
     "creature": "aerial double leap, wings flapping or energy burst secondary mid-air leap"},
    {"id": "crouch", "name": "Crouch", "cat": "Locomotion", "fps": 5.0,
     "human": "crouching low to ground, sneaking stealth crawling stance",
     "creature": "creature crouching low to ground, prowling beast stealth posture close to floor"},
    {"id": "dash", "name": "Dash", "cat": "Locomotion", "fps": 10.0,
     "human": "rapid forward dash, burst of speed leaning forward with speed trail effect",
     "creature": "rapid beast forward dash charge, burst of speed bounding forward with dust trail"},
    {"id": "slide", "name": "Slide", "cat": "Locomotion", "fps": 7.0,
     "human": "sliding forward on knees or feet across the floor, low ground skid",
     "creature": "low ground skid slide, belly skid forward across the floor with friction sparks"},

    # Standing Strikes (5)
    {"id": "punch1", "name": "Punch 1 (Light)", "cat": "Standing Strikes", "fps": 8.0,
     "human": "quick light jab punch strike forward, fast arm snap",
     "creature": "quick light claw swipe strike forward with front paw/limb"},
    {"id": "punch2", "name": "Punch 2 (Medium)", "cat": "Standing Strikes", "fps": 8.0,
     "human": "medium cross punch strike forward with torso rotation",
     "creature": "medium claw slash strike across front with tearing motion"},
    {"id": "punch3", "name": "Punch 3 (Heavy)", "cat": "Standing Strikes", "fps": 8.0,
     "human": "heavy straight punch strike forward, powerful impact blow",
     "creature": "heavy vicious bite or ferocious double claw strike forward"},
    {"id": "uppercut", "name": "Uppercut", "cat": "Standing Strikes", "fps": 8.0,
     "human": "rising vertical uppercut punch strike launching upwards",
     "creature": "rising vertical headbutt or horn thrust strike launching upwards"},
    {"id": "dash_punch", "name": "Dash Punch", "cat": "Standing Strikes", "fps": 9.0,
     "human": "rushing forward thrust punch strike out of full sprint",
     "creature": "rushing forward lunge bite or charging claw strike out of full sprint"},

    # Standing Kicks (5)
    {"id": "kick1", "name": "Kick 1 (Light)", "cat": "Standing Kicks", "fps": 8.0,
     "human": "front snap kick strike, fast lower foot jab",
     "creature": "rear leg kick strike or quick tail whip tap"},
    {"id": "kick2", "name": "Kick 2 (Medium)", "cat": "Standing Kicks", "fps": 8.0,
     "human": "roundhouse kick strike rotating body with sweeping foot",
     "creature": "spinning tail whip sweep attack striking horizontally"},
    {"id": "kick3", "name": "Kick 3 (Heavy)", "cat": "Standing Kicks", "fps": 7.0,
     "human": "heavy side thrust kick strike driving heel into target",
     "creature": "heavy rear bucking kick with hind legs or forceful tail slam"},
    {"id": "kick4", "name": "Kick 4 (Finisher)", "cat": "Standing Kicks", "fps": 8.0,
     "human": "spinning high axe kick strike or overhead heel kick",
     "creature": "heavy overhead tail smash strike crushing downward"},
    {"id": "dash_kick", "name": "Dash Kick", "cat": "Standing Kicks", "fps": 9.0,
     "human": "rushing slide tackle or flying dash kick forward",
     "creature": "rushing charging tail sweep or sliding body tackle forward"},

    # Aerial Jump Attacks (8)
    {"id": "jump_punch1", "name": "Jump Punch 1", "cat": "Aerial Attacks", "fps": 8.0,
     "human": "aerial jumping light jab punch strike downwards from air",
     "creature": "aerial diving claw pounce swipe downwards from air"},
    {"id": "jump_punch2", "name": "Jump Punch 2", "cat": "Aerial Attacks", "fps": 8.0,
     "human": "aerial jumping medium cross punch strike in mid-air",
     "creature": "aerial diving bite strike snapping in mid-air"},
    {"id": "jump_punch3", "name": "Jump Punch 3", "cat": "Aerial Attacks", "fps": 7.0,
     "human": "aerial jumping heavy hammerfist punch strike downwards",
     "creature": "aerial diving double claw slam downwards with full weight"},
    {"id": "jump_kick1", "name": "Jump Kick 1", "cat": "Aerial Attacks", "fps": 8.0,
     "human": "aerial jumping light snap kick in mid-air",
     "creature": "aerial jumping talon tap or tail snap in mid-air"},
    {"id": "jump_kick2", "name": "Jump Kick 2", "cat": "Aerial Attacks", "fps": 8.0,
     "human": "aerial jumping flying kick strike forward through air",
     "creature": "aerial flying pounce extending hind claws forward through air"},
    {"id": "jump_kick3", "name": "Jump Kick 3", "cat": "Aerial Attacks", "fps": 8.0,
     "human": "aerial jumping 360 spinning kick strike in mid-air",
     "creature": "aerial mid-air 360 tail spin strike hitting all around"},
    {"id": "jump_kick4", "name": "Jump Kick 4", "cat": "Aerial Attacks", "fps": 8.0,
     "human": "aerial jumping divekick downwards at 45 degree angle",
     "creature": "aerial diving ground pound pouncing downwards with talons and body"},
    {"id": "jump_block", "name": "Jump Block", "cat": "Aerial Attacks", "fps": 6.0,
     "human": "mid-air aerial defensive guard block absorbing hit",
     "creature": "mid-air aerial defensive guard curling inwards or tucking wings/limbs"},

    # Crouch Attacks & Defenses (9)
    {"id": "crouch_punch1", "name": "Crouch Punch 1", "cat": "Crouch Moves", "fps": 8.0,
     "human": "crouching low jab punch strike aimed at opponent shins",
     "creature": "crouching low claw swipe near ground scraping floor"},
    {"id": "crouch_punch2", "name": "Crouch Punch 2", "cat": "Crouch Moves", "fps": 8.0,
     "human": "crouching low medium punch strike forward",
     "creature": "crouching low snap bite strike lunging forward close to ground"},
    {"id": "crouch_punch3", "name": "Crouch Punch 3", "cat": "Crouch Moves", "fps": 7.0,
     "human": "crouching low heavy hook punch strike driving upward",
     "creature": "crouching low heavy forward claw rake tearing across floor"},
    {"id": "crouch_kick1", "name": "Crouch Kick 1", "cat": "Crouch Moves", "fps": 8.0,
     "human": "crouching low shin kick strike poking low",
     "creature": "crouching low tail jab strike poking low"},
    {"id": "crouch_kick2", "name": "Crouch Kick 2", "cat": "Crouch Moves", "fps": 8.0,
     "human": "crouching low sweep kick strike tripping target legs",
     "creature": "crouching low tail sweep tripping attack spinning along floor"},
    {"id": "crouch_kick3", "name": "Crouch Kick 3", "cat": "Crouch Moves", "fps": 7.0,
     "human": "crouching low thrust kick strike pushing opponent back",
     "creature": "crouching low rear leg thrust kick pushing back"},
    {"id": "crouch_kick4", "name": "Crouch Kick 4", "cat": "Crouch Moves", "fps": 8.0,
     "human": "crouching spinning double sweep kick complete rotation",
     "creature": "crouching spinning 360 tail sweep clearing ground area"},
    {"id": "crouch_block", "name": "Crouch Block", "cat": "Crouch Moves", "fps": 6.0,
     "human": "crouching low defensive guard block shielding body and legs",
     "creature": "crouching low defensive turtle guard hugging ground protecting vitals"},
    {"id": "block", "name": "Block (Standing)", "cat": "Crouch Moves", "fps": 6.0,
     "human": "standing defensive guard block with arms or shield absorbing impact",
     "creature": "standing defensive guard protecting vitals with armored plates/wings"},

    # Items & Projectiles (5)
    {"id": "throw_item", "name": "Throw Item", "cat": "Items & Projectiles", "fps": 7.0,
     "human": "throwing an item or projectile forward from hand with overhand release",
     "creature": "hurling an item forward from mouth or swinging tail launch"},
    {"id": "pick_up_item", "name": "Pick Up Item", "cat": "Items & Projectiles", "fps": 6.0,
     "human": "bending down to pick up an item from the floor with hand",
     "creature": "lowering head to pick up an item from the floor with jaws or claws"},
    {"id": "drink_potion", "name": "Drink Potion / Consume", "cat": "Items & Projectiles", "fps": 6.0,
     "human": "drinking glowing potion bottle, tipping head back and absorbing magic",
     "creature": "consuming glowing power orb or magical energy essence into maw"},
    {"id": "fire_projectile", "name": "Fire Projectile", "cat": "Items & Projectiles", "fps": 7.0,
     "human": "firing glowing energy beam or magic missile projectile from outstretched hands",
     "creature": "firing breath weapon or plasma fireball energy blast from maw/mouth"},
    {"id": "grapple", "name": "Grapple", "cat": "Items & Projectiles", "fps": 7.0,
     "human": "grappling hold grabbing the opponent with both hands in clutch stance",
     "creature": "pouncing tackle clamping onto opponent with jaws and pin down stance"},

    # Hits, Status Conditions & States (8)
    {"id": "get_hit", "name": "Get Hit / Flinch", "cat": "Reactions & Statuses", "fps": 7.0,
     "human": "taking damage, flinching backwards in pain from hit impact shock",
     "creature": "creature taking damage, flinching backwards in pain from hit impact shock"},
    {"id": "get_stunned", "name": "Get Stunned", "cat": "Reactions & Statuses", "fps": 5.0,
     "human": "dazed dizzy stunned animation, wobbling head and off-balance posture",
     "creature": "creature dazed dizzy stunned animation, swaying head and off-balance posture"},
    {"id": "get_paralyzed", "name": "Get Paralyzed", "cat": "Reactions & Statuses", "fps": 6.0,
     "human": "paralyzed stiff electric sparks shock shaking and freezing in place",
     "creature": "creature paralyzed stiff electric sparks shock convulsing and freezing in place"},
    {"id": "get_poisoned", "name": "Get Poisoned", "cat": "Reactions & Statuses", "fps": 5.0,
     "human": "clutching stomach suffering green poison venom damage ticks coughing",
     "creature": "creature shivering suffering green venom poison fumes damage ticks"},
    {"id": "get_burned", "name": "Get Burned", "cat": "Reactions & Statuses", "fps": 6.0,
     "human": "flailing reacting to fire burn flames blazing on body in panic",
     "creature": "creature reacting in distress to fiery flames burning on hide"},
    {"id": "get_frozen", "name": "Get Frozen", "cat": "Reactions & Statuses", "fps": 4.0,
     "human": "encased in ice block shivering frozen stiff with frost breath",
     "creature": "creature encased in frosty ice block shivering frozen solid with ice crystals"},
    {"id": "death", "name": "Death", "cat": "Reactions & Statuses", "fps": 5.0,
     "human": "defeat collapse animation, falling limp onto the floor motionless",
     "creature": "creature defeat collapse animation, falling limp onto the floor motionless"},
    {"id": "stand_up", "name": "Stand Up", "cat": "Reactions & Statuses", "fps": 6.0,
     "human": "standing back up from the ground recovery animation onto feet",
     "creature": "creature pushing back up from the floor recovery onto all fours stance"},

    # Special Moves (4)
    {"id": "special_move_1", "name": "Special Move 1", "cat": "Specials", "fps": 8.0,
     "human": "special move 1 rapid multi-strike aura technique with glowing energy fists",
     "creature": "special move 1 elemental roaring energy surge strike with glowing claws"},
    {"id": "special_move_2", "name": "Special Move 2", "cat": "Specials", "fps": 8.0,
     "human": "special move 2 spinning tornado strike technique ascending into air",
     "creature": "special move 2 savage whirlwind spin attack sweeping all around"},
    {"id": "special_move_3", "name": "Special Move 3", "cat": "Specials", "fps": 7.0,
     "human": "special move 3 ground smash shockwave technique slamming fists into floor",
     "creature": "special move 3 seismic ground slam shockwave pouncing front paws into earth"},
    {"id": "special_move_4_ultimate", "name": "Special Move 4 (Ultimate)", "cat": "Specials", "fps": 7.0,
     "human": "super special ultimate power surge charging stance, colossal glowing aura burst pose",
     "creature": "super ultimate apocalyptic roar and titanic elemental energy blast unleash pose"}
]

# 2D VFX Presets (Projectiles, Orbs, Slashes, Particles)
VFX_PRESETS = [
    {"id": "fireball", "name": "Fiery Plasma Fireball", "cat": "Projectiles & Orbs", "fps": 8.0,
     "desc": "fiery plasma energy fireball projectile flying forward, swirling orange flame particles, glowing bright combustion trail"},
    {"id": "plasma_orb", "name": "Electric Plasma Orb", "cat": "Projectiles & Orbs", "fps": 8.0,
     "desc": "glowing electric blue plasma energy orb with crackling lightning arcs swirling around core"},
    {"id": "ice_shard", "name": "Ice Shard / Icicle", "cat": "Projectiles & Orbs", "fps": 8.0,
     "desc": "sharp crystalline ice shard projectile gliding through air, glittering cyan frost sparkles and cold mist trail"},
    {"id": "arcane_missile", "name": "Arcane Star Missile", "cat": "Projectiles & Orbs", "fps": 8.0,
     "desc": "magic arcane star missile orb glowing radiant magenta and purple, trailing magical stardust sparkles"},
    {"id": "poison_spit", "name": "Toxic Acid Spit", "cat": "Projectiles & Orbs", "fps": 7.0,
     "desc": "toxic acidic green venom projectile globule flying forward, dripping acidic bubbling droplets"},
    {"id": "sword_slash_arc", "name": "Sword Slash Arc Wave", "cat": "Slashes & Impacts", "fps": 8.0,
     "desc": "curved glowing sword slash energy arc blade wave expanding forward and dissipating cleanly"},
    {"id": "claw_slash_triple", "name": "Triple Claw Slash FX", "cat": "Slashes & Impacts", "fps": 8.0,
     "desc": "triple glowing crimson red claw rake slash trails tearing through the air and fading"},
    {"id": "hit_impact_sparks", "name": "Hit Impact Spark Burst", "cat": "Slashes & Impacts", "fps": 9.0,
     "desc": "comic hit impact flash burst with starburst shape and radiating yellow sparks expanding outward"},
    {"id": "shockwave_ring", "name": "Ground Shockwave Ring", "cat": "Slashes & Impacts", "fps": 8.0,
     "desc": "circular dust and energy ground shockwave ripple expanding outwards along floor"},
    {"id": "fiery_explosion", "name": "Fire & Smoke Explosion", "cat": "Bursts & Explosions", "fps": 8.0,
     "desc": "comic fiery explosion burst, billowing bright flame sphere expanding into dark smoke puff"},
    {"id": "magic_rune_burst", "name": "Magic Circle Rune Burst", "cat": "Bursts & Explosions", "fps": 8.0,
     "desc": "glowing arcane floor circle rune glyph flashing brightly, emitting vertical pillars of light and fading"},
    {"id": "smoke_poof", "name": "Dust / Smoke Poof", "cat": "Bursts & Explosions", "fps": 7.0,
     "desc": "puffy cartoon dust cloud expanding outward in 4 stages and evaporating into small clouds"},
    {"id": "shield_barrier", "name": "Hexagonal Shield Barrier", "cat": "Auras & Shields", "fps": 6.0,
     "desc": "hexagonal glowing cyan energy forcefield shield barrier pulsing with light protective aura"},
    {"id": "flame_aura", "name": "Fiery Power Aura Loop", "cat": "Auras & Shields", "fps": 8.0,
     "desc": "looping fire aura flames rising and flickering smoothly around character space"},
    {"id": "healing_sparkles", "name": "Healing Magic Sparkles", "cat": "Auras & Shields", "fps": 6.0,
     "desc": "gentle glowing green healing magic cross sparkles and bubbles floating upward continuously"}
]


# ============================================================
# Background Job & Queue Manager
# ============================================================
class JobManager:
    def __init__(self):
        self.lock = threading.Lock()
        self.is_running = False
        self.batch_id = ""
        self.batch_name = ""
        self.jobs = []  # list of {"pid": str, "id": str, "name": str, "status": "queued"|"running"|"done"|"error", "preview_url": str}
        self.total_jobs = 0
        self.completed_count = 0
        self.current_job_name = ""
        self.current_job_id = ""
        self.latest_preview = None
        self.thread = None

    def start_batch(self, batch_id, name, jobs):
        with self.lock:
            self.batch_id = batch_id
            self.batch_name = name
            self.jobs = jobs
            self.total_jobs = len(jobs)
            self.completed_count = 0
            self.is_running = True
            self.current_job_name = jobs[0]["name"] if jobs else ""
            self.current_job_id = jobs[0]["id"] if jobs else ""
            self.latest_preview = None

        if self.thread is None or not self.thread.is_alive():
            self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.thread.start()

    def cancel_batch(self):
        with self.lock:
            self.is_running = False
            self.jobs = []
            self.total_jobs = 0
            self.completed_count = 0
            self.current_job_name = ""
            self.current_job_id = ""

        # Send interrupt and clear queue to ComfyUI
        try:
            req1 = urllib.request.Request(f"{COMFY_URL}/queue", data=json.dumps({"clear": True}).encode(), headers={"Content-Type": "application/json"})
            urllib.request.urlopen(req1, timeout=2)
            req2 = urllib.request.Request(f"{COMFY_URL}/interrupt", data=b"")
            urllib.request.urlopen(req2, timeout=2)
        except Exception:
            pass

    def get_status(self):
        with self.lock:
            completed_ids = [j["id"] for j in self.jobs if j["status"] == "done"]
            pct = 0
            if self.total_jobs > 0:
                pct = min(100, int((self.completed_count / self.total_jobs) * 100))

            return {
                "is_running": self.is_running,
                "total_queued": self.total_jobs,
                "completed_count": self.completed_count,
                "percent": pct,
                "current_move": self.current_job_name,
                "current_id": self.current_job_id,
                "completed_ids": completed_ids,
                "latest_preview": self.latest_preview,
                "batch_name": self.batch_name
            }

    def _monitor_loop(self):
        while True:
            time.sleep(1.2)
            with self.lock:
                if not self.is_running or not self.jobs:
                    continue

                # Query running jobs from ComfyUI /queue
                running_pids = set()
                try:
                    with urllib.request.urlopen(f"{COMFY_URL}/queue", timeout=2) as r:
                        q_data = json.loads(r.read().decode())
                        for item in q_data.get("queue_running", []):
                            if len(item) > 1:
                                running_pids.add(item[1])
                except Exception:
                    pass

                completed_now = 0
                found_running = False

                for job in self.jobs:
                    pid = job["pid"]
                    if job["status"] == "done":
                        completed_now += 1
                        continue

                    if pid in running_pids:
                        job["status"] = "running"
                        self.current_job_name = job["name"]
                        self.current_job_id = job["id"]
                        found_running = True
                        continue

                    # Check ComfyUI history
                    try:
                        with urllib.request.urlopen(f"{COMFY_URL}/history/{pid}", timeout=2) as r:
                            h = json.loads(r.read().decode())
                            if pid in h:
                                status = h[pid].get("status", {}).get("status_str", "")
                                if status == "success":
                                    job["status"] = "done"
                                    completed_now += 1
                                    # Output file check
                                    prefix = f"{self.batch_name}_{job['id']}"
                                    anim_name = f"{prefix}_anim_00001_.png"
                                    if os.path.exists(os.path.join(OUTPUT_DIR, anim_name)):
                                        self.latest_preview = f"/output/{anim_name}"
                                        job["preview_url"] = self.latest_preview
                                else:
                                    job["status"] = "error"
                                    completed_now += 1
                    except Exception:
                        pass

                self.completed_count = completed_now

                # Update current active job display
                if not found_running:
                    for job in self.jobs:
                        if job["status"] == "queued":
                            self.current_job_name = job["name"]
                            self.current_job_id = job["id"]
                            break

                if completed_now >= self.total_jobs and self.total_jobs > 0:
                    self.is_running = False
                    self.current_job_name = "All Animations Complete!"
                    self.current_job_id = ""


GLOBAL_JOB_MGR = JobManager()


# ============================================================
# ComfyUI Workflow Construction
# ============================================================
def build_character_graph(char_desc, action_item, is_creature, style, output_style, seed, char_name, custom_action_prompt=None, frame_width=256, frame_height=256, ref_image=None):
    """Builds the ComfyUI workflow JSON for a character animation with optional reference image and rendering medium."""
    if custom_action_prompt and custom_action_prompt.strip():
        action_desc = custom_action_prompt.strip()
    else:
        action_desc = action_item["creature"] if is_creature else action_item["human"]

    prefix = f"{char_name}_{action_item['id']}"
    fps = action_item.get("fps", 6.0)

    # Rendering medium styles
    is_pixel_style = "Pixel Art" in style or "NES" in style

    if "Vector" in style:
        style_prompt = (
            "smooth clean vector 2d game art, crisp sharp outlines, solid flat color fills, "
            "modern indie game sprite, high resolution, no pixel art, no noise"
        )
        neg_style = "pixel art, pixelated, 8-bit, 16-bit, chunky pixels, mosaic, 3d render, photorealistic, noise, complex background"
    elif "Hand-Drawn" in style:
        style_prompt = (
            "detailed hand-drawn 2d arcade fighting game sprite, rich cell shading, dynamic comic linework, "
            "vibrant colors, clean sharp edges, no pixelation"
        )
        neg_style = "pixel art, pixelated, low resolution, 3d render, photorealistic, noise, blurry, messy background"
    elif "Painterly" in style:
        style_prompt = (
            "painterly stylized 2d concept art sprite, beautiful digital brush strokes, rich lighting, "
            "clean silhouette, high detail fantasy illustration"
        )
        neg_style = "pixel art, pixelated, low resolution, photorealistic, photo, messy outlines"
    elif "Western Cartoon" in style:
        style_prompt = (
            "expressive western cartoon 2d animation sprite, bold inked outlines, fluid squash and stretch poses, "
            "solid vibrant cel animation colors"
        )
        neg_style = "pixel art, pixelated, 3d render, photorealistic, gritty, noise"
    elif "8-bit" in style or "NES" in style:
        style_prompt = (
            "authentic 8-bit retro NES pixel art sprite, restricted 4-color palette, chunky square pixels, "
            "sharp crisp pixel boundaries"
        )
        neg_style = "blurry, smooth vector, anti-aliased, 3d render, photorealistic, modern gradients"
    else:
        # Default: 16-bit Retro Pixel Art
        style_prompt = (
            "classic 16-bit arcade video game sprite, authentic pixel art, clean pixel grid, "
            "crisp black outline, vibrant retro colors"
        )
        neg_style = "photorealistic, 3d render, blurry, messy outlines, noise, complex background"

    pos_prompt = (
        f"clean high-quality 2d game sprite sheet of {char_desc}, "
        f"4 animation frames in a horizontal sequence, "
        f"{action_desc}, "
        f"{style_prompt}, "
        f"flat solid pure white background, distinct separated frames, full body"
    )

    neg_prompt = f"{neg_style}, blurry, overlapping frames, text, watermark"

    canvas_w = int(frame_width) * 4
    canvas_h = int(frame_height)

    graph = {
        "1": {"class_type": "UNETLoader", "inputs": {"unet_name": "z_image_turbo_bf16.safetensors", "weight_dtype": "default"}},
        "2": {"class_type": "CLIPLoader", "inputs": {"clip_name": "qwen_3_4b.safetensors", "type": "qwen_image"}},
        "3": {"class_type": "VAELoader", "inputs": {"vae_name": "z-image-ae.safetensors"}},
        "6": {"class_type": "EmptyLatentImage", "inputs": {"width": canvas_w, "height": canvas_h, "batch_size": 1}},
        "7": {"class_type": "KSampler", "inputs": {
            "model": ["1", 0], "positive": ["4", 0], "negative": ["5", 0], "latent_image": ["6", 0],
            "seed": seed, "control_after_generate": "fixed", "steps": 8, "cfg": 1.0,
            "sampler_name": "dpmpp_sde", "scheduler": "beta", "denoise": 1.0
        }},
        "8": {"class_type": "VAEDecode", "inputs": {"samples": ["7", 0], "vae": ["3", 0]}},
        "9": {"class_type": "BiRefNetRMBG", "inputs": {
            "image": ["8", 0], "model": "BiRefNet_toonout", "mask_blur": 0, "mask_offset": 0,
            "invert_output": False, "refine_foreground": False, "background": "Alpha", "background_color": "#222222"
        }},
        "10": {"class_type": "SplitImageToTileList", "inputs": {"image": ["9", 0], "tile_width": int(frame_width), "tile_height": int(frame_height), "overlap": 0}},
        "11": {"class_type": "RebatchImages", "inputs": {"images": ["10", 0], "batch_size": 4}},
    }

    # Reference Image Conditioning (Optional)
    if ref_image and ref_image.strip():
        # Node 20: LoadImage, Node 21: Scale to 512x512 (guaranteeing exact even latent dimensions for Lumina/Z-Image)
        graph["20"] = {"class_type": "LoadImage", "inputs": {"image": ref_image.strip()}}
        graph["21"] = {"class_type": "ImageScale", "inputs": {"image": ["20", 0], "upscale_method": "area", "width": 512, "height": 512, "crop": "disabled"}}
        graph["4"] = {"class_type": "TextEncodeZImageOmni", "inputs": {
            "clip": ["2", 0], "prompt": pos_prompt, "auto_resize_images": False, "vae": ["3", 0], "image1": ["21", 0]
        }}
        graph["5"] = {"class_type": "TextEncodeZImageOmni", "inputs": {
            "clip": ["2", 0], "prompt": neg_prompt, "auto_resize_images": False
        }}
    else:
        graph["4"] = {"class_type": "TextEncodeZImageOmni", "inputs": {
            "clip": ["2", 0], "prompt": pos_prompt, "auto_resize_images": True
        }}
        graph["5"] = {"class_type": "TextEncodeZImageOmni", "inputs": {
            "clip": ["2", 0], "prompt": neg_prompt, "auto_resize_images": True
        }}

    # Output selection (single clean output by default)
    if output_style == "retro" and is_pixel_style:
        down_w = max(16, int(frame_width) // 4)
        down_h = max(16, int(frame_height) // 4)
        graph["14"] = {"class_type": "ImageScale", "inputs": {"image": ["11", 0], "upscale_method": "nearest-exact", "width": down_w, "height": down_h, "crop": "disabled"}}
        graph["15"] = {"class_type": "ImageScale", "inputs": {"image": ["14", 0], "upscale_method": "nearest-exact", "width": int(frame_width), "height": int(frame_height), "crop": "disabled"}}
        graph["16"] = {"class_type": "SaveAnimatedPNG", "inputs": {"images": ["15", 0], "filename_prefix": f"{prefix}_anim", "fps": fps, "compress_level": 4}}
        graph["17"] = {"class_type": "ImageGrid", "inputs": {"images": ["15", 0], "columns": 4, "cell_width": int(frame_width), "cell_height": int(frame_height), "padding": 0}}
        graph["18"] = {"class_type": "SaveImage", "inputs": {"images": ["17", 0], "filename_prefix": f"{prefix}_spritesheet"}}
    elif output_style == "both" and is_pixel_style:
        # Standard clean
        graph["12"] = {"class_type": "SaveAnimatedPNG", "inputs": {"images": ["11", 0], "filename_prefix": f"{prefix}_anim", "fps": fps, "compress_level": 4}}
        graph["13"] = {"class_type": "SaveAnimatedWEBP", "inputs": {"images": ["11", 0], "filename_prefix": f"{prefix}_webp", "fps": fps, "lossless": True, "quality": 90, "method": "default"}}
        # Retro snap
        down_w = max(16, int(frame_width) // 4)
        down_h = max(16, int(frame_height) // 4)
        graph["14"] = {"class_type": "ImageScale", "inputs": {"image": ["11", 0], "upscale_method": "nearest-exact", "width": down_w, "height": down_h, "crop": "disabled"}}
        graph["15"] = {"class_type": "ImageScale", "inputs": {"image": ["14", 0], "upscale_method": "nearest-exact", "width": int(frame_width), "height": int(frame_height), "crop": "disabled"}}
        graph["16"] = {"class_type": "SaveAnimatedPNG", "inputs": {"images": ["15", 0], "filename_prefix": f"{prefix}_retro_anim", "fps": fps, "compress_level": 4}}
        graph["17"] = {"class_type": "ImageGrid", "inputs": {"images": ["11", 0], "columns": 4, "cell_width": int(frame_width), "cell_height": int(frame_height), "padding": 0}}
        graph["18"] = {"class_type": "SaveImage", "inputs": {"images": ["17", 0], "filename_prefix": f"{prefix}_spritesheet"}}
    else:
        # Standard clean output (Smooth Vector, Detailed 2D, or Clean Pixel Art)
        graph["12"] = {"class_type": "SaveAnimatedPNG", "inputs": {"images": ["11", 0], "filename_prefix": f"{prefix}_anim", "fps": fps, "compress_level": 4}}
        graph["13"] = {"class_type": "SaveAnimatedWEBP", "inputs": {"images": ["11", 0], "filename_prefix": f"{prefix}_webp", "fps": fps, "lossless": True, "quality": 90, "method": "default"}}
        graph["17"] = {"class_type": "ImageGrid", "inputs": {"images": ["11", 0], "columns": 4, "cell_width": int(frame_width), "cell_height": int(frame_height), "padding": 0}}
        graph["18"] = {"class_type": "SaveImage", "inputs": {"images": ["17", 0], "filename_prefix": f"{prefix}_spritesheet"}}

    return graph


def build_vfx_graph(vfx_desc, vfx_id, style, seed, name_prefix, frame_width=256, frame_height=256):
    """Builds the ComfyUI workflow JSON for a 2D VFX / Projectile / Particle animation."""
    prefix = f"{name_prefix}_{vfx_id}"
    is_pixel = "Pixel Art" in style or "NES" in style

    if is_pixel:
        header = "pixel art 2d sprite sheet of"
        style_desc = "vibrant 16-bit retro arcade video game special effect VFX, crisp bold outlines"
        neg = "human, character, face, photorealistic, noise, complex background, text, watermark, blurry, overlapping frames"
    else:
        header = "clean 2d vector game special effect sprite sheet of"
        style_desc = "smooth modern 2d game VFX, radiant energy glow, crisp particle shapes, high resolution vector graphics, no pixel art"
        neg = "pixel art, pixelated, 8-bit, 16-bit, human, character, face, photorealistic, noise, complex background, text, watermark, blurry, overlapping frames"

    pos_prompt = (
        f"{header} {vfx_desc}, "
        f"4 sequential animation frames in a horizontal sequence, "
        f"{style_desc}, "
        f"flat solid pure white background, distinct separated frames"
    )

    canvas_w = int(frame_width) * 4
    canvas_h = int(frame_height)

    return {
        "1": {"class_type": "UNETLoader", "inputs": {"unet_name": "z_image_turbo_bf16.safetensors", "weight_dtype": "default"}},
        "2": {"class_type": "CLIPLoader", "inputs": {"clip_name": "qwen_3_4b.safetensors", "type": "qwen_image"}},
        "3": {"class_type": "VAELoader", "inputs": {"vae_name": "z-image-ae.safetensors"}},
        "4": {"class_type": "TextEncodeZImageOmni", "inputs": {"prompt": pos_prompt, "auto_resize_images": True, "clip": ["2", 0]}},
        "5": {"class_type": "TextEncodeZImageOmni", "inputs": {"prompt": neg, "auto_resize_images": True, "clip": ["2", 0]}},
        "6": {"class_type": "EmptyLatentImage", "inputs": {"width": canvas_w, "height": canvas_h, "batch_size": 1}},
        "7": {"class_type": "KSampler", "inputs": {
            "model": ["1", 0], "positive": ["4", 0], "negative": ["5", 0], "latent_image": ["6", 0],
            "seed": seed, "control_after_generate": "fixed", "steps": 8, "cfg": 1.0,
            "sampler_name": "dpmpp_sde", "scheduler": "beta", "denoise": 1.0
        }},
        "8": {"class_type": "VAEDecode", "inputs": {"samples": ["7", 0], "vae": ["3", 0]}},
        "9": {"class_type": "BiRefNetRMBG", "inputs": {
            "image": ["8", 0], "model": "BiRefNet_toonout", "mask_blur": 0, "mask_offset": 0,
            "invert_output": False, "refine_foreground": False, "background": "Alpha", "background_color": "#222222"
        }},
        "10": {"class_type": "SplitImageToTileList", "inputs": {"image": ["9", 0], "tile_width": int(frame_width), "tile_height": int(frame_height), "overlap": 0}},
        "11": {"class_type": "RebatchImages", "inputs": {"images": ["10", 0], "batch_size": 4}},
        "12": {"class_type": "SaveAnimatedPNG", "inputs": {"images": ["11", 0], "filename_prefix": f"{prefix}_anim", "fps": 8.0, "compress_level": 4}},
        "13": {"class_type": "SaveAnimatedWEBP", "inputs": {"images": ["11", 0], "filename_prefix": f"{prefix}_webp", "fps": 8.0, "lossless": True, "quality": 90, "method": "default"}},
        "14": {"class_type": "ImageGrid", "inputs": {"images": ["11", 0], "columns": 4, "cell_width": int(frame_width), "cell_height": int(frame_height), "padding": 0}},
        "15": {"class_type": "SaveImage", "inputs": {"images": ["14", 0], "filename_prefix": f"{prefix}_spritesheet"}}
    }


def send_to_comfy(prompt_dict):
    req = urllib.request.Request(
        f"{COMFY_URL}/prompt",
        data=json.dumps({"prompt": prompt_dict}).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode("utf-8"))["prompt_id"]


# ============================================================
# Local LLM Prompt Optimizer (Ollama)
# ============================================================
def query_ollama(prompt, system=""):
    """Queries local Ollama instance (qwen2.5:3b or fallback)"""
    model_to_use = "qwen2.5:3b"
    try:
        # Check available models
        with urllib.request.urlopen(f"{OLLAMA_URL}/api/tags", timeout=1.5) as r:
            tags = json.loads(r.read().decode())
            available = [m["name"].split(":")[0] for m in tags.get("models", [])]
            if "qwen2.5" in available or "qwen2.5:3b" in available:
                model_to_use = "qwen2.5:3b"
            elif len(available) > 0:
                model_to_use = tags["models"][0]["name"]
    except Exception:
        pass

    payload = {
        "model": model_to_use,
        "prompt": prompt,
        "system": system,
        "stream": False,
        "options": {
            "temperature": 0.7,
            "top_p": 0.9,
            "num_predict": 128
        }
    }

    try:
        req = urllib.request.Request(
            f"{OLLAMA_URL}/api/generate",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            out = data.get("response", "").strip()
            # Clean up quotes
            if out.startswith('"') and out.endswith('"'):
                out = out[1:-1].strip()
            return out, model_to_use
    except Exception as e:
        return None, str(e)


# ============================================================
# Web UI HTML + CSS + Vanilla JS
# ============================================================
HTML_STUDIO = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>2D Sprite & VFX Studio (AMD ROCm / CUDA)</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
:root {
  --bg-main: #090d16;
  --bg-card: #131b2e;
  --bg-item: #1a253d;
  --border: #233354;
  --border-focus: #38bdf8;
  --text-main: #f8fafc;
  --text-muted: #94a3b8;
  --accent: #38bdf8;
  --accent-glow: rgba(56, 189, 248, 0.25);
  --success: #10b981;
  --purple: #c084fc;
  --warning: #f59e0b;
  --danger: #f43f5e;
}

* { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
body { background: var(--bg-main); color: var(--text-main); line-height: 1.5; padding-bottom: 80px; }

header {
  background: var(--bg-card);
  border-bottom: 1px solid var(--border);
  padding: 14px 32px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: sticky;
  top: 0;
  z-index: 100;
}

.logo { font-size: 20px; font-weight: 800; color: #fff; display: flex; align-items: center; gap: 10px; }
.logo span { color: var(--accent); }
.badge { background: #0284c7; color: #fff; font-size: 11px; padding: 3px 8px; border-radius: 6px; text-transform: uppercase; font-weight: 700; }
.badge-ai { background: #7e22ce; color: #f3e8ff; font-size: 11px; padding: 3px 8px; border-radius: 6px; font-weight: 700; display: inline-flex; align-items: center; gap: 4px; }
.dot-live { width: 7px; height: 7px; background: #10b981; border-radius: 50%; display: inline-block; box-shadow: 0 0 8px #10b981; }

.nav-tabs { display: flex; gap: 8px; }
.nav-tab {
  background: transparent;
  border: 1px solid transparent;
  color: var(--text-muted);
  border-radius: 8px;
  padding: 8px 16px;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 6px;
}
.nav-tab:hover { color: #fff; background: var(--bg-item); }
.nav-tab.active { background: #0284c7; color: #fff; border-color: var(--accent); box-shadow: 0 0 12px var(--accent-glow); }

.tab-content { display: none; }
.tab-content.active { display: block; }

.container { max-width: 1420px; margin: 24px auto; padding: 0 20px; }
.grid-layout { display: grid; grid-template-columns: 460px 1fr; gap: 24px; }

.panel {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 20px;
}
.panel-title {
  font-size: 16px;
  font-weight: 700;
  color: #fff;
  margin-bottom: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.form-group { margin-bottom: 16px; }
.form-group label { display: block; font-size: 12px; font-weight: 600; color: var(--text-muted); margin-bottom: 6px; text-transform: uppercase; letter-spacing: 0.5px; }
input[type="text"], input[type="number"], select, textarea {
  width: 100%;
  background: var(--bg-item);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 10px 12px;
  color: #fff;
  font-size: 13px;
  outline: none;
  transition: border 0.2s, box-shadow 0.2s;
}
input[type="text"]:focus, select:focus, textarea:focus {
  border-color: var(--border-focus);
  box-shadow: 0 0 8px var(--accent-glow);
}
textarea { resize: vertical; min-height: 80px; }

/* Reference Image Box */
.ref-image-box {
  background: var(--bg-item);
  border: 2px dashed var(--border);
  border-radius: 8px;
  padding: 12px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
}
.ref-image-box:hover { border-color: var(--accent); background: rgba(56, 189, 248, 0.05); }
.ref-preview-wrap { display: flex; align-items: center; gap: 12px; text-align: left; }
.ref-preview-img { width: 64px; height: 64px; object-fit: contain; background: #000; border-radius: 6px; border: 1px solid var(--border); }
.ref-info { flex: 1; min-width: 0; }
.ref-filename { font-size: 12px; font-weight: 600; color: #fff; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.ref-tag { font-size: 11px; color: var(--success); font-weight: 600; }
.btn-remove-ref { background: #e11d48; color: #fff; border: none; border-radius: 6px; padding: 4px 8px; font-size: 11px; cursor: pointer; }

/* Anatomy toggle */
.anatomy-toggle { display: flex; background: var(--bg-item); border-radius: 8px; p-1: 3px; border: 1px solid var(--border); }
.pill-btn {
  flex: 1;
  padding: 8px 12px;
  border: none;
  background: transparent;
  color: var(--text-muted);
  font-weight: 600;
  font-size: 12px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}
.pill-btn.active { background: #0284c7; color: #fff; box-shadow: 0 0 10px var(--accent-glow); }

/* Buttons */
.btn-primary {
  width: 100%;
  background: linear-gradient(135deg, #0284c7, #2563eb);
  color: #fff;
  border: none;
  border-radius: 8px;
  padding: 12px;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}
.btn-primary:hover { opacity: 0.95; transform: translateY(-1px); box-shadow: 0 0 16px var(--accent-glow); }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; transform: none; box-shadow: none; }

.btn-ai {
  background: linear-gradient(135deg, #7e22ce, #9333ea);
  color: #fff;
  border: none;
  border-radius: 6px;
  padding: 6px 10px;
  font-size: 11px;
  font-weight: 700;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  transition: all 0.2s;
}
.btn-ai:hover { opacity: 0.9; box-shadow: 0 0 8px rgba(168, 85, 247, 0.4); }

.btn-sm {
  background: var(--bg-item);
  border: 1px solid var(--border);
  color: var(--text-muted);
  border-radius: 6px;
  padding: 5px 10px;
  font-size: 11px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}
.btn-sm:hover { color: #fff; border-color: var(--accent); }
.btn-danger { background: #e11d48; color: #fff; border-color: #f43f5e; }
.btn-danger:hover { background: #be123c; }

/* Status Bar with live preview */
.status-bar {
  background: var(--bg-item);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 14px;
  margin-top: 16px;
}
.status-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; font-weight: 600; font-size: 13px; }
.progress-bg { background: #0b1120; border-radius: 6px; height: 10px; overflow: hidden; position: relative; margin-bottom: 10px; }
.progress-fill {
  background: linear-gradient(90deg, #0284c7, #38bdf8);
  height: 100%;
  width: 0%;
  transition: width 0.3s;
  box-shadow: 0 0 12px var(--accent-glow);
}
.status-preview-row {
  display: flex;
  align-items: center;
  gap: 12px;
  background: rgba(0,0,0,0.3);
  padding: 8px 12px;
  border-radius: 6px;
  border: 1px solid rgba(255,255,255,0.05);
}
.status-preview-img { width: 44px; height: 44px; object-fit: contain; background: #111; border-radius: 4px; }
.status-action-title { font-size: 12px; font-weight: 700; color: var(--accent); }
.status-action-desc { font-size: 11px; color: var(--text-muted); }

/* Moves grid */
.moves-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 14px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border);
}
.cat-filters { display: flex; gap: 6px; flex-wrap: wrap; }
.cat-btn {
  background: var(--bg-item);
  border: 1px solid var(--border);
  color: var(--text-muted);
  border-radius: 6px;
  padding: 4px 10px;
  font-size: 11px;
  font-weight: 600;
  cursor: pointer;
}
.cat-btn.active { background: #0284c7; color: #fff; border-color: var(--accent); }

.anim-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 12px;
  max-height: 720px;
  overflow-y: auto;
  padding-right: 6px;
}
.anim-grid::-webkit-scrollbar { width: 6px; }
.anim-grid::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }

.anim-card {
  background: var(--bg-item);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 10px;
  transition: all 0.2s;
  position: relative;
}
.anim-card.selected { border-color: rgba(56, 189, 248, 0.4); }
.anim-card.running { border-color: var(--accent); box-shadow: 0 0 12px var(--accent-glow); background: rgba(56, 189, 248, 0.08); }
.anim-card.done { border-color: rgba(16, 185, 129, 0.5); }

.anim-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }
.anim-title { font-size: 12px; font-weight: 700; color: #fff; display: flex; align-items: center; gap: 6px; cursor: pointer; }
.anim-cat { font-size: 10px; color: var(--text-muted); background: rgba(0,0,0,0.3); padding: 2px 6px; border-radius: 4px; }
.anim-prompt-box {
  width: 100%;
  height: 52px;
  font-size: 11px;
  color: #cbd5e1;
  background: rgba(0,0,0,0.3);
  border: 1px solid var(--border);
  border-radius: 4px;
  padding: 6px;
  resize: none;
}
.card-actions { display: flex; justify-content: space-between; align-items: center; margin-top: 6px; }
.card-badge-status { font-size: 10px; font-weight: 700; padding: 2px 6px; border-radius: 4px; }
.badge-done { background: rgba(16, 185, 129, 0.2); color: #10b981; }
.badge-running { background: rgba(56, 189, 248, 0.2); color: #38bdf8; animation: pulse 1.2s infinite; }

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* Asset Library Tab */
.library-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
  margin-top: 16px;
}
.asset-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.asset-preview {
  width: 160px;
  height: 160px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #000;
  border-radius: 8px;
  border: 1px solid var(--border);
  margin-bottom: 12px;
  overflow: hidden;
}
.asset-preview img { max-width: 100%; max-height: 100%; object-fit: contain; image-rendering: pixelated; }
.asset-title { font-size: 13px; font-weight: 700; color: #fff; margin-bottom: 2px; text-align: center; }
.asset-meta { font-size: 11px; color: var(--text-muted); margin-bottom: 10px; }
.asset-btn-row { display: flex; gap: 6px; width: 100%; }
.asset-btn-row a, .asset-btn-row button {
  flex: 1;
  text-align: center;
  font-size: 11px;
  padding: 6px;
  border-radius: 6px;
  text-decoration: none;
  font-weight: 600;
}
.btn-dl { background: #0284c7; color: #fff; }
.btn-dl:hover { background: #0369a1; }
.btn-del { background: transparent; border: 1px solid #e11d48; color: #e11d48; cursor: pointer; }
.btn-del:hover { background: #e11d48; color: #fff; }

/* Modals */
.modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0, 0, 0, 0.75);
  display: none;
  align-items: center;
  justify-content: center;
  z-index: 200;
}
.modal-box {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 12px;
  width: 520px;
  padding: 24px;
}
.modal-title { font-size: 16px; font-weight: 700; margin-bottom: 16px; color: #fff; }
</style>
</head>
<body>

<header>
  <div class="logo">
    <span>👾 2D SPRITE</span> & VFX STUDIO
    <span class="badge">AMD ROCm</span>
    <span class="badge-ai" id="aiStatusBadge"><span class="dot-live"></span> Ollama Qwen2.5</span>
  </div>
  <div class="nav-tabs">
    <button class="nav-tab active" onclick="switchTab('tabCharacter')">🎮 Character Studio (52 Moves)</button>
    <button class="nav-tab" onclick="switchTab('tabVFX')">✨ VFX & Projectiles</button>
    <button class="nav-tab" onclick="switchTab('tabLibrary')">📦 Asset Library</button>
  </div>
</header>

<div class="container">

  <!-- ================= CHARACTER STUDIO TAB ================= -->
  <div id="tabCharacter" class="tab-content active">
    <div class="grid-layout">
      <!-- Left Config Panel -->
      <div class="panel">
        <div class="panel-title">
          <span>Character Profile</span>
          <span class="badge" id="countBadge">52 Selected</span>
        </div>

        <div class="form-group">
          <label>Character Name (Asset Prefix)</label>
          <input type="text" id="charName" value="shadow_ninja" placeholder="e.g. shadow_ninja, flame_golem">
        </div>

        <div class="form-group">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
            <label style="margin:0;">Character Description</label>
            <button class="btn-ai" onclick="optimizeCharacterPrompt()" title="Enhance prompt with Local Ollama AI">✨ AI Enhance</button>
          </div>
          <textarea id="charDesc" placeholder="Describe the character...">a swift cyberpunk shadow ninja with glowing neon blue scarf, dark stealth suit, and dual energetic katanas</textarea>
        </div>

        <!-- Reference Image Upload (Optional) -->
        <div class="form-group">
          <label>Reference Character Image (Optional)</label>
          <input type="file" id="refImageInput" accept="image/*" style="display:none;" onchange="handleRefUpload(this)">
          <div class="ref-image-box" id="refDropBox" onclick="document.getElementById('refImageInput').click()">
            <div id="refEmptyPrompt">
              <span style="font-size:24px;">📁</span>
              <p style="font-size:12px; color:var(--text-muted); margin-top:4px;">Click or drag to attach character reference image</p>
              <p style="font-size:10px; color:var(--accent);">Anchors all 52 animation moves to this visual design</p>
            </div>
            <div id="refLoadedRow" class="ref-preview-wrap" style="display:none;">
              <img id="refThumb" class="ref-preview-img" src="" alt="Ref">
              <div class="ref-info">
                <div class="ref-filename" id="refFilename">image.png</div>
                <div class="ref-tag">✓ Anchoring 52 Moves to Reference</div>
              </div>
              <button class="btn-remove-ref" onclick="removeReferenceImage(event)">✕</button>
            </div>
          </div>
        </div>

        <div class="form-group">
          <label>Art Medium / Rendering Style</label>
          <select id="artStyle" onchange="updateStyleNotice()">
            <option value="Smooth HD Vector Art" selected>Smooth HD Vector Art (Modern Clean 2D)</option>
            <option value="Detailed Hand-Drawn 2D">Detailed Hand-Drawn 2D (Arcade Fighter)</option>
            <option value="Painterly 2D Concept Art">Painterly 2D Concept Art (Stylized Fantasy)</option>
            <option value="Western Cartoon Brawler">Western Cartoon Brawler (Expressive Cel)</option>
            <option value="16-bit Retro Arcade Pixel Art">16-bit Retro Arcade Pixel Art</option>
            <option value="8-bit Classic NES Pixel Art">8-bit Classic NES Pixel Art</option>
          </select>
        </div>

        <div class="form-group">
          <label>Sprite Frame Sizing</label>
          <select id="spriteSizePreset" onchange="handleSizeChange()">
            <option value="64x64">64 x 64 (Classic Retro)</option>
            <option value="128x128">128 x 128 (Standard Indie)</option>
            <option value="192x256">192 x 256 (Tall Fighting Game / Metroidvania)</option>
            <option value="256x256" selected>256 x 256 (HD Standard Default)</option>
            <option value="512x512">512 x 512 (Ultra High-Res Vector & Bosses)</option>
            <option value="custom">Custom Dimensions...</option>
          </select>
          <div id="customSizeRow" style="display:none; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: 8px;">
            <input type="number" id="customWidth" value="256" placeholder="Width (px)">
            <input type="number" id="customHeight" value="256" placeholder="Height (px)">
          </div>
        </div>

        <div class="form-group">
          <label>Output Mode</label>
          <select id="outputStyle">
            <option value="standard" selected>Standard (Clean Single Output)</option>
            <option value="retro">Pixel-Snapped Downscaled (Retro only)</option>
            <option value="both">Both (Standard + Retro Variants)</option>
          </select>
        </div>

        <div class="form-group">
          <label>Character Anatomy / Moveset Mode</label>
          <div class="anatomy-toggle">
            <button class="pill-btn active" id="pillHuman" onclick="toggleAnatomy(false)">👤 Humanoid</button>
            <button class="pill-btn" id="pillCreature" onclick="toggleAnatomy(true)">🐾 Creature / Monster</button>
          </div>
        </div>

        <div class="form-group">
          <label>Master Random Seed</label>
          <div style="display:flex; gap:8px;">
            <input type="number" id="charSeed" value="424242">
            <button class="btn-sm" onclick="randomizeSeed()" title="Randomize Seed">🎲</button>
          </div>
        </div>

        <button class="btn-primary" id="btnGenerate" onclick="startGeneration()">
          🚀 Generate Sprite Pack (<span id="selectedCount">52</span> Moves)
        </button>

        <!-- Live Progress Status Bar -->
        <div class="status-bar" id="statusBar" style="display:none;">
          <div class="status-header">
            <span id="statusText">Queuing animations into GPU...</span>
            <span id="statusPercent" style="color:var(--accent); font-weight:800;">0%</span>
          </div>
          <div class="progress-bg">
            <div class="progress-fill" id="progressFill"></div>
          </div>
          <div class="status-preview-row" id="statusPreviewRow" style="display:none;">
            <img id="statusLiveImg" class="status-preview-img" src="" alt="Live Preview">
            <div style="flex:1;">
              <div class="status-action-title" id="statusCurrentAction">Processing move...</div>
              <div class="status-action-desc" id="statusCountDetail">0 / 52 Completed</div>
            </div>
            <button class="btn-sm btn-danger" onclick="cancelActiveBatch()">⏹ Stop</button>
          </div>
        </div>
      </div>

      <!-- Right Moveset Panel -->
      <div class="panel">
        <div class="moves-toolbar">
          <div class="cat-filters" id="catFilters">
            <button class="cat-btn active" onclick="filterCategory('All')">All (52)</button>
            <button class="cat-btn" onclick="filterCategory('Locomotion')">Locomotion (8)</button>
            <button class="cat-btn" onclick="filterCategory('Standing Strikes')">Strikes (5)</button>
            <button class="cat-btn" onclick="filterCategory('Standing Kicks')">Kicks (5)</button>
            <button class="cat-btn" onclick="filterCategory('Aerial Attacks')">Air Attacks (8)</button>
            <button class="cat-btn" onclick="filterCategory('Crouch Moves')">Crouch & Blocks (9)</button>
            <button class="cat-btn" onclick="filterCategory('Items & Projectiles')">Items & Projectiles (5)</button>
            <button class="cat-btn" onclick="filterCategory('Reactions & Statuses')">Statuses (8)</button>
            <button class="cat-btn" onclick="filterCategory('Specials')">Specials (4)</button>
          </div>
          <div style="display:flex; gap:6px;">
            <button class="btn-ai" onclick="optimizeAllMovePrompts()" title="Enhance all 52 move prompts with Local Ollama AI">✨ AI Optimize All</button>
            <button class="btn-sm" onclick="selectAll(true)">Select All</button>
            <button class="btn-sm" onclick="selectAll(false)">Clear</button>
            <button class="btn-sm" style="background:#0284c7; color:#fff;" onclick="openAddCustomModal()">➕ Add Custom Move</button>
          </div>
        </div>

        <div class="anim-grid" id="animGrid">
          <!-- Animation cards injected here -->
        </div>
      </div>
    </div>
  </div>

  <!-- ================= 2D VFX / PROJECTILES TAB ================= -->
  <div id="tabVFX" class="tab-content">
    <div class="grid-layout">
      <div class="panel">
        <div class="panel-title">✨ VFX & Projectiles Studio</div>
        <div class="form-group">
          <label>VFX Preset Name</label>
          <input type="text" id="vfxName" value="fireball" placeholder="e.g. plasma_orb, ice_shard">
        </div>
        <div class="form-group">
          <label>VFX Effect Prompt</label>
          <textarea id="vfxDesc">fiery plasma energy fireball projectile flying forward, swirling orange flame particles, glowing bright combustion trail</textarea>
        </div>
        <div class="form-group">
          <label>VFX Art Medium</label>
          <select id="vfxStyle">
            <option value="Smooth HD Vector Art" selected>Smooth HD Vector Art (Luminous modern glow)</option>
            <option value="16-bit Retro Pixel Art">16-bit Retro Arcade Pixel Art</option>
          </select>
        </div>
        <div class="form-group">
          <label>Resolution</label>
          <select id="vfxSizePreset">
            <option value="128x128">128 x 128 (Standard Projectile)</option>
            <option value="256x256" selected>256 x 256 (High Detail Burst)</option>
            <option value="512x512">512 x 512 (Colossal Ultimate Spell)</option>
          </select>
        </div>
        <div class="form-group">
          <label>Random Seed</label>
          <div style="display:flex; gap:8px;">
            <input type="number" id="vfxSeed" value="987654">
            <button class="btn-sm" onclick="randomizeVFXSeed()">🎲</button>
          </div>
        </div>
        <button class="btn-primary" id="btnGenerateVFX" onclick="startVFXGeneration()">
          ✨ Generate VFX Animation
        </button>

        <div class="status-bar" id="vfxStatusBar" style="display:none;">
          <div class="status-header">
            <span id="vfxStatusText">Rendering VFX on GPU...</span>
          </div>
          <div class="progress-bg">
            <div class="progress-fill" style="width:100%;"></div>
          </div>
        </div>
      </div>

      <div class="panel">
        <div class="panel-title">15+ Built-in 2D VFX Presets</div>
        <div class="anim-grid" id="vfxGrid">
          <!-- VFX cards -->
        </div>
      </div>
    </div>
  </div>

  <!-- ================= ASSET LIBRARY TAB ================= -->
  <div id="tabLibrary" class="tab-content">
    <div class="panel">
      <div class="panel-title">
        <span>📦 Generated Game Assets & Sprite Sheets</span>
        <div style="display:flex; gap:8px;">
          <button class="btn-sm" onclick="loadAssetLibrary()">🔄 Refresh Library</button>
          <button class="btn-sm" style="background:#0284c7; color:#fff;" onclick="downloadZip()">📦 Download Character ZIP</button>
          <button class="btn-sm" onclick="openOutputFolder()">📂 Open Output Folder</button>
        </div>
      </div>
      <div class="library-grid" id="libraryGrid">
        <!-- Asset cards -->
      </div>
    </div>
  </div>

</div>

<!-- MODAL: Add Custom Move -->
<div class="modal-overlay" id="modalAddCustom">
  <div class="modal-box">
    <div class="modal-title">➕ Add Custom Animation Move</div>
    <div class="form-group">
      <label>Move Identifier (Snake Case)</label>
      <input type="text" id="customMoveId" placeholder="e.g. lightning_teleport, spin_slash">
    </div>
    <div class="form-group">
      <label>Display Name</label>
      <input type="text" id="customMoveName" placeholder="e.g. Lightning Teleport">
    </div>
    <div class="form-group">
      <label>Category</label>
      <select id="customMoveCat">
        <option value="Locomotion">Locomotion</option>
        <option value="Standing Strikes">Standing Strikes</option>
        <option value="Standing Kicks">Standing Kicks</option>
        <option value="Aerial Attacks">Aerial Attacks</option>
        <option value="Crouch Moves">Crouch Moves</option>
        <option value="Items & Projectiles">Items & Projectiles</option>
        <option value="Reactions & Statuses">Reactions & Statuses</option>
        <option value="Specials" selected>Specials</option>
      </select>
    </div>
    <div class="form-group">
      <label>Action Motion Description</label>
      <textarea id="customMovePrompt" placeholder="Describe the 4-frame animation motion..."></textarea>
    </div>
    <div style="display:flex; justify-content:flex-end; gap:8px;">
      <button class="btn-sm" onclick="closeAddCustomModal()">Cancel</button>
      <button class="btn-sm" style="background:#0284c7; color:#fff;" onclick="submitCustomMove()">Add to Moveset</button>
    </div>
  </div>
</div>

<!-- MODAL: Re-run Single Move -->
<div class="modal-overlay" id="modalRerun">
  <div class="modal-box">
    <div class="modal-title">🔁 Re-run Single Animation</div>
    <div class="form-group">
      <label>Action Name</label>
      <input type="text" id="rerunMoveName" readonly style="opacity:0.7;">
    </div>
    <div class="form-group">
      <label>Custom Seed (or Randomize)</label>
      <div style="display:flex; gap:8px;">
        <input type="text" id="rerunSeed" value="424242">
        <button class="btn-sm" onclick="document.getElementById('rerunSeed').value = Math.floor(Math.random()*900000)+100000">🎲</button>
      </div>
    </div>
    <div class="form-group">
      <label>Prompt Description Override</label>
      <textarea id="rerunPrompt"></textarea>
    </div>
    <div style="display:flex; justify-content:flex-end; gap:8px;">
      <button class="btn-sm" onclick="closeRerunModal()">Cancel</button>
      <button class="btn-sm" style="background:#0284c7; color:#fff;" onclick="submitRerun()">Run on GPU</button>
    </div>
  </div>
</div>

<script>
let animations = [];
let vfxList = [];
let isCreatureMode = false;
let pollingInterval = null;
let libraryData = [];
let currentRerunItem = null;
let selectedRefImage = null; // Filename of uploaded reference

async function init() {
  const res1 = await fetch('/api/presets');
  animations = await res1.json();
  animations.forEach(a => a.selected = true);

  const res2 = await fetch('/api/vfx_presets');
  vfxList = await res2.json();

  checkLLMStatus();
  renderAnimations();
  renderVFX();
  loadAssetLibrary();
}

async function checkLLMStatus() {
  try {
    const res = await fetch('/api/llm_status');
    const data = await res.json();
    const badge = document.getElementById('aiStatusBadge');
    if (data.available) {
      badge.innerHTML = `<span class="dot-live"></span> Ollama: ${data.model}`;
      badge.style.display = 'inline-flex';
    } else {
      badge.innerHTML = `⚠️ Local AI Offline`;
      badge.style.background = '#334155';
    }
  } catch (e) {
    console.warn("LLM check error:", e);
  }
}

function handleSizeChange() {
  const sel = document.getElementById('spriteSizePreset').value;
  const customRow = document.getElementById('customSizeRow');
  if (sel === 'custom') {
    customRow.style.display = 'grid';
  } else {
    customRow.style.display = 'none';
    const parts = sel.split('x');
    document.getElementById('customWidth').value = parts[0];
    document.getElementById('customHeight').value = parts[1];
  }
}

function getSelectedDimensions() {
  const sel = document.getElementById('spriteSizePreset').value;
  if (sel === 'custom') {
    return {
      w: parseInt(document.getElementById('customWidth').value) || 256,
      h: parseInt(document.getElementById('customHeight').value) || 256
    };
  } else {
    const parts = sel.split('x');
    return { w: parseInt(parts[0]), h: parseInt(parts[1]) };
  }
}

function updateStyleNotice() {
  const style = document.getElementById('artStyle').value;
  const isPixel = style.includes('Pixel Art') || style.includes('NES');
  const outStyle = document.getElementById('outputStyle');
  if (!isPixel && outStyle.value !== 'standard') {
    outStyle.value = 'standard';
  }
}

function switchTab(tabId) {
  document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));

  event.target.classList.add('active');
  document.getElementById(tabId).classList.add('active');

  if (tabId === 'tabLibrary') {
    loadAssetLibrary();
  }
}

function toggleAnatomy(isCreature) {
  isCreatureMode = isCreature;
  document.getElementById('pillHuman').classList.toggle('active', !isCreature);
  document.getElementById('pillCreature').classList.toggle('active', isCreature);
  renderAnimations();
}

function renderAnimations(catFilter = 'All') {
  const grid = document.getElementById('animGrid');
  grid.innerHTML = '';

  animations.forEach((anim) => {
    if (catFilter !== 'All' && anim.cat !== catFilter) return;

    const card = document.createElement('div');
    card.id = `card_${anim.id}`;
    card.className = 'anim-card' + (anim.selected ? ' selected' : '') + (anim.isDone ? ' done' : '') + (anim.isRunning ? ' running' : '');

    const defaultDesc = isCreatureMode ? anim.creature : anim.human;
    const currentDesc = anim.custom_prompt !== undefined ? anim.custom_prompt : defaultDesc;

    let badgeHtml = '';
    if (anim.isRunning) {
      badgeHtml = `<span class="card-badge-status badge-running">⚡ Running</span>`;
    } else if (anim.isDone) {
      badgeHtml = `<span class="card-badge-status badge-done">✓ Done</span>`;
    }

    card.innerHTML = `
      <div class="anim-header">
        <label class="anim-title">
          <input type="checkbox" ${anim.selected ? 'checked' : ''} onchange="toggleSelect('${anim.id}', this.checked)">
          <span>${anim.name}</span>
        </label>
        <span class="anim-cat">${anim.cat}</span>
      </div>
      <textarea class="anim-prompt-box" id="box_${anim.id}" placeholder="Customize action prompt..." onchange="updateCustomPrompt('${anim.id}', this.value)">${currentDesc}</textarea>
      <div class="card-actions">
        <div>${badgeHtml}</div>
        <div style="display:flex; gap:4px;">
          <button class="btn-ai" onclick="optimizeSingleMovePrompt('${anim.id}')" title="AI optimize this move">✨ AI</button>
          <button class="btn-sm" onclick="openRerunModalSingle('${anim.id}')" title="Generate only this move">🔁 Re-run</button>
        </div>
      </div>
    `;
    grid.appendChild(card);
  });
  updateCounts();
}

function toggleSelect(id, val) {
  const anim = animations.find(a => a.id === id);
  if (anim) {
    anim.selected = val;
    const card = document.getElementById(`card_${id}`);
    if (card) card.classList.toggle('selected', val);
  }
  updateCounts();
}

function updateCustomPrompt(id, val) {
  const anim = animations.find(a => a.id === id);
  if (anim) anim.custom_prompt = val;
}

function selectAll(state) {
  animations.forEach(a => a.selected = state);
  renderAnimations();
}

function filterCategory(cat) {
  document.querySelectorAll('.cat-btn').forEach(b => {
    b.classList.toggle('active', b.innerText.includes(cat) || (cat === 'All' && b.innerText.includes('All')));
  });
  renderAnimations(cat);
}

function updateCounts() {
  const count = animations.filter(a => a.selected).length;
  document.getElementById('selectedCount').innerText = count;
  document.getElementById('countBadge').innerText = `${count} / ${animations.length} Selected`;
}

function randomizeSeed() {
  document.getElementById('charSeed').value = Math.floor(Math.random() * 900000) + 100000;
}
function randomizeVFXSeed() {
  document.getElementById('vfxSeed').value = Math.floor(Math.random() * 900000) + 100000;
}

/* Reference Image Upload Handling */
async function handleRefUpload(input) {
  if (!input.files || !input.files[0]) return;
  const file = input.files[0];

  const reader = new FileReader();
  reader.onload = async function(e) {
    const base64Data = e.target.result;
    try {
      const res = await fetch('/api/upload_reference', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ filename: file.name, data: base64Data })
      });
      const data = await res.json();
      if (data.status === 'ok') {
        selectedRefImage = data.filename;
        document.getElementById('refThumb').src = data.url;
        document.getElementById('refFilename').innerText = data.filename;
        document.getElementById('refEmptyPrompt').style.display = 'none';
        document.getElementById('refLoadedRow').style.display = 'flex';
      } else {
        alert("Upload error: " + (data.error || "Unknown"));
      }
    } catch (err) {
      alert("Error uploading reference: " + err);
    }
  };
  reader.readAsDataURL(file);
}

function removeReferenceImage(e) {
  if (e) e.stopPropagation();
  selectedRefImage = null;
  document.getElementById('refImageInput').value = '';
  document.getElementById('refEmptyPrompt').style.display = 'block';
  document.getElementById('refLoadedRow').style.display = 'none';
}

/* Local LLM / AI Prompt Optimization */
async function optimizeCharacterPrompt() {
  const desc = document.getElementById('charDesc').value.trim();
  const style = document.getElementById('artStyle').value;
  if (!desc) {
    alert("Please enter a rough character description first!");
    return;
  }

  const btn = event.target;
  const oldText = btn.innerText;
  btn.disabled = true;
  btn.innerText = "✨ AI Thinking...";

  try {
    const res = await fetch('/api/optimize_prompt', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ type: 'character', char_desc: desc, style: style, is_creature: isCreatureMode })
    });
    const data = await res.json();
    if (data.optimized) {
      document.getElementById('charDesc').value = data.optimized;
    } else {
      alert("AI optimization error: " + (data.error || "Could not optimize"));
    }
  } catch (err) {
    alert("AI Error: " + err);
  } finally {
    btn.disabled = false;
    btn.innerText = oldText;
  }
}

async function optimizeSingleMovePrompt(id) {
  const anim = animations.find(a => a.id === id);
  const charDesc = document.getElementById('charDesc').value.trim();
  if (!anim) return;

  const btn = event.target;
  btn.disabled = true;
  btn.innerText = "⏳...";

  try {
    const res = await fetch('/api/optimize_prompt', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ type: 'move', char_desc: charDesc, action_item: anim, is_creature: isCreatureMode })
    });
    const data = await res.json();
    if (data.optimized) {
      anim.custom_prompt = data.optimized;
      const box = document.getElementById(`box_${id}`);
      if (box) box.value = data.optimized;
    }
  } catch (err) {
    console.error(err);
  } finally {
    btn.disabled = false;
    btn.innerText = "✨ AI";
  }
}

async function optimizeAllMovePrompts() {
  const charDesc = document.getElementById('charDesc').value.trim();
  const selectedMoves = animations.filter(a => a.selected);
  if (selectedMoves.length === 0) {
    alert("Please select moves to optimize!");
    return;
  }

  const btn = event.target;
  btn.disabled = true;
  btn.innerText = "✨ AI Optimizing 52 Moves...";

  try {
    const res = await fetch('/api/optimize_prompt', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ type: 'all_moves', char_desc: charDesc, moves: selectedMoves, is_creature: isCreatureMode })
    });
    const data = await res.json();
    if (data.optimized_moves) {
      data.optimized_moves.forEach(item => {
        const anim = animations.find(a => a.id === item.id);
        if (anim) {
          anim.custom_prompt = item.prompt;
          const box = document.getElementById(`box_${item.id}`);
          if (box) box.value = item.prompt;
        }
      });
    }
  } catch (err) {
    alert("Error optimizing all moves: " + err);
  } finally {
    btn.disabled = false;
    btn.innerText = "✨ AI Optimize All";
  }
}

/* Generation & Background Polling */
async function startGeneration() {
  const name = document.getElementById('charName').value.trim() || 'hero';
  const desc = document.getElementById('charDesc').value.trim();
  const seed = parseInt(document.getElementById('charSeed').value) || 424242;
  const style = document.getElementById('artStyle').value;
  const outputStyle = document.getElementById('outputStyle').value;
  const selectedMoves = animations.filter(a => a.selected);
  const dims = getSelectedDimensions();

  if (selectedMoves.length === 0) {
    alert("Please select at least one animation!");
    return;
  }

  // Reset done and running states
  animations.forEach(a => {
    a.isDone = false;
    a.isRunning = false;
  });
  renderAnimations();

  const btn = document.getElementById('btnGenerate');
  btn.disabled = true;
  btn.innerText = "⏳ Queuing into ComfyUI...";

  document.getElementById('statusBar').style.display = 'block';
  document.getElementById('statusPreviewRow').style.display = 'flex';
  document.getElementById('statusText').innerText = `Queuing ${selectedMoves.length} animations (${dims.w}x${dims.h})...`;
  document.getElementById('statusPercent').innerText = "0%";
  document.getElementById('progressFill').style.width = "0%";

  const payload = {
    char_name: name,
    char_desc: desc,
    seed: seed,
    style: style,
    output_style: outputStyle,
    is_creature: isCreatureMode,
    ref_image: selectedRefImage,
    selected_moves: selectedMoves,
    frame_width: dims.w,
    frame_height: dims.h
  };

  try {
    const res = await fetch('/api/generate', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (data.status === 'ok') {
      btn.innerText = `Processing Batch (${selectedMoves.length} items)...`;
      startPolling();
    } else {
      alert("Error starting batch: " + (data.error || "Unknown"));
      btn.disabled = false;
      btn.innerText = "🚀 Generate Sprite Pack";
    }
  } catch (err) {
    alert("Error queuing: " + err);
    btn.disabled = false;
    btn.innerText = "🚀 Generate Sprite Pack";
  }
}

function startPolling() {
  if (pollingInterval) clearInterval(pollingInterval);
  pollingInterval = setInterval(async () => {
    try {
      const res = await fetch('/api/status');
      const data = await res.json();

      const pct = data.percent || 0;
      document.getElementById('statusPercent').innerText = `${pct}%`;
      document.getElementById('progressFill').style.width = `${pct}%`;

      if (data.is_running) {
        document.getElementById('statusText').innerText = `Rendering on GPU: ${data.completed_count} / ${data.total_queued} complete`;
        document.getElementById('statusCurrentAction').innerText = data.current_move ? `⚡ Generating: ${data.current_move}` : "Rendering frames...";
        document.getElementById('statusCountDetail').innerText = `${data.completed_count} / ${data.total_queued} finished`;

        if (data.latest_preview) {
          const img = document.getElementById('statusLiveImg');
          img.src = `${data.latest_preview}?t=${new Date().getTime()}`;
        }

        // Update card status in grid
        animations.forEach(a => {
          const isFinished = (data.completed_ids || []).includes(a.id);
          const isCurrent = (data.current_id === a.id);
          if (a.isDone !== isFinished || a.isRunning !== isCurrent) {
            a.isDone = isFinished;
            a.isRunning = isCurrent;
            const card = document.getElementById(`card_${a.id}`);
            if (card) {
              card.classList.toggle('done', isFinished);
              card.classList.toggle('running', isCurrent);
              const badgeSlot = card.querySelector('.card-badge-status');
              if (badgeSlot) {
                if (isCurrent) {
                  badgeSlot.className = 'card-badge-status badge-running';
                  badgeSlot.innerText = '⚡ Running';
                } else if (isFinished) {
                  badgeSlot.className = 'card-badge-status badge-done';
                  badgeSlot.innerText = '✓ Done';
                }
              }
            }
          }
        });
      } else {
        // Not running
        if (data.total_queued > 0 && data.completed_count >= data.total_queued) {
          clearInterval(pollingInterval);
          document.getElementById('statusText').innerText = "🎉 All Animations Complete!";
          document.getElementById('statusPercent').innerText = "100%";
          document.getElementById('progressFill').style.width = "100%";
          document.getElementById('btnGenerate').disabled = false;
          document.getElementById('btnGenerate').innerText = "🚀 Generate Sprite Pack";

          // Mark all selected as done
          animations.forEach(a => { if (a.selected) a.isDone = true; a.isRunning = false; });
          renderAnimations();
          loadAssetLibrary();
        }
      }
    } catch (e) {
      console.error("Polling error:", e);
    }
  }, 1200);
}

async function cancelActiveBatch() {
  if (!confirm("Are you sure you want to stop the generation batch?")) return;
  try {
    await fetch('/api/cancel_batch', { method: 'POST' });
    if (pollingInterval) clearInterval(pollingInterval);
    document.getElementById('statusBar').style.display = 'none';
    document.getElementById('btnGenerate').disabled = false;
    document.getElementById('btnGenerate').innerText = "🚀 Generate Sprite Pack";
    animations.forEach(a => a.isRunning = false);
    renderAnimations();
  } catch (err) {
    alert("Error cancelling: " + err);
  }
}

/* Custom Move Modal */
function openAddCustomModal() {
  document.getElementById('modalAddCustom').style.display = 'flex';
}
function closeAddCustomModal() {
  document.getElementById('modalAddCustom').style.display = 'none';
}
function submitCustomMove() {
  const id = document.getElementById('customMoveId').value.trim().toLowerCase().replace(/\\s+/g, '_');
  const name = document.getElementById('customMoveName').value.trim();
  const cat = document.getElementById('customMoveCat').value;
  const prompt = document.getElementById('customMovePrompt').value.trim();

  if (!id || !name || !prompt) {
    alert("Please fill in all fields!");
    return;
  }

  animations.push({
    id: id,
    name: name,
    cat: cat,
    fps: 6.0,
    human: prompt,
    creature: prompt,
    custom_prompt: prompt,
    selected: true
  });

  closeAddCustomModal();
  renderAnimations();
  document.getElementById('customMoveId').value = '';
  document.getElementById('customMoveName').value = '';
  document.getElementById('customMovePrompt').value = '';
}

/* Re-run Modal */
function openRerunModalSingle(id) {
  const anim = animations.find(a => a.id === id);
  if (!anim) return;
  currentRerunItem = anim;
  document.getElementById('rerunMoveName').value = `${anim.name} (${anim.id})`;
  document.getElementById('rerunPrompt').value = anim.custom_prompt || (isCreatureMode ? anim.creature : anim.human);
  document.getElementById('rerunSeed').value = Math.floor(Math.random() * 900000) + 100000;
  document.getElementById('modalRerun').style.display = 'flex';
}
function closeRerunModal() {
  document.getElementById('modalRerun').style.display = 'none';
}
async function submitRerun() {
  if (!currentRerunItem) return;

  const name = document.getElementById('charName').value.trim() || 'hero';
  const desc = document.getElementById('charDesc').value.trim();
  const style = document.getElementById('artStyle').value;
  const outputStyle = document.getElementById('outputStyle').value;
  const dims = getSelectedDimensions();
  const overridePrompt = document.getElementById('rerunPrompt').value.trim();
  const customSeed = parseInt(document.getElementById('rerunSeed').value) || 424242;

  currentRerunItem.custom_prompt = overridePrompt;
  closeRerunModal();

  const card = document.getElementById(`card_${currentRerunItem.id}`);
  if (card) {
    card.classList.add('running');
    card.classList.remove('done');
  }

  try {
    const res = await fetch('/api/generate_single', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        char_name: name,
        char_desc: desc,
        seed: customSeed,
        style: style,
        output_style: outputStyle,
        is_creature: isCreatureMode,
        ref_image: selectedRefImage,
        action_item: currentRerunItem,
        custom_prompt: overridePrompt,
        frame_width: dims.w,
        frame_height: dims.h
      })
    });
    const data = await res.json();
    alert(`Queued move into GPU (PID: ${data.pid}). Asset Library will update once finished.`);
  } catch (err) {
    alert("Error queuing single move: " + err);
  }
}

/* VFX Tab */
function renderVFX() {
  const grid = document.getElementById('vfxGrid');
  grid.innerHTML = '';

  vfxList.forEach((vfx) => {
    const card = document.createElement('div');
    card.className = 'anim-card' + (vfx.selected ? ' selected' : '');
    card.onclick = () => {
      document.getElementById('vfxDesc').value = vfx.desc;
      document.getElementById('vfxName').value = vfx.id;
      vfxList.forEach(v => v.selected = false);
      vfx.selected = true;
      renderVFX();
    };

    card.innerHTML = `
      <div class="anim-header">
        <span class="anim-title">${vfx.name}</span>
        <span class="anim-cat">${vfx.cat}</span>
      </div>
      <p style="font-size:11px; color:var(--text-muted); line-height:1.4;">${vfx.desc}</p>
    `;
    grid.appendChild(card);
  });
}

async function startVFXGeneration() {
  const name = document.getElementById('vfxName').value.trim() || 'vfx';
  const desc = document.getElementById('vfxDesc').value.trim();
  const style = document.getElementById('vfxStyle').value;
  const seed = parseInt(document.getElementById('vfxSeed').value) || 987654;
  const selSize = document.getElementById('vfxSizePreset').value.split('x');
  const fw = parseInt(selSize[0]);
  const fh = parseInt(selSize[1]);

  const btn = document.getElementById('btnGenerateVFX');
  btn.disabled = true;
  btn.innerText = "⏳ Rendering VFX on GPU...";
  document.getElementById('vfxStatusBar').style.display = 'block';

  try {
    const res = await fetch('/api/generate_vfx', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ vfx_name: name, vfx_desc: desc, style: style, seed: seed, frame_width: fw, frame_height: fh })
    });
    const data = await res.json();
    setTimeout(() => {
      btn.disabled = false;
      btn.innerText = "✨ Generate VFX Animation";
      document.getElementById('vfxStatusBar').style.display = 'none';
      alert(`VFX generation queued (PID: ${data.pid}). Check the Asset Library in ~6 seconds!`);
      loadAssetLibrary();
    }, 4000);
  } catch (err) {
    alert("VFX error: " + err);
    btn.disabled = false;
    btn.innerText = "✨ Generate VFX Animation";
    document.getElementById('vfxStatusBar').style.display = 'none';
  }
}

/* Asset Library Tab */
async function loadAssetLibrary() {
  const grid = document.getElementById('libraryGrid');
  try {
    const res = await fetch('/api/library');
    libraryData = await res.json();

    grid.innerHTML = '';
    if (libraryData.length === 0) {
      grid.innerHTML = '<p style="color:var(--text-muted); padding:20px;">No assets generated yet. Generate a sprite or VFX to see files here!</p>';
      return;
    }

    libraryData.forEach(asset => {
      const card = document.createElement('div');
      card.className = 'asset-card';

      const previewSrc = asset.preview_url ? `${asset.preview_url}?t=${new Date().getTime()}` : '';

      card.innerHTML = `
        <div class="asset-preview">
          <img src="${previewSrc}" alt="${asset.name}">
        </div>
        <div class="asset-title">${asset.name}</div>
        <div class="asset-meta">${asset.type.toUpperCase()} • ${asset.date}</div>
        <div class="asset-btn-row">
          ${asset.apng_url ? `<a href="${asset.apng_url}" download class="btn-dl">APNG</a>` : ''}
          ${asset.webp_url ? `<a href="${asset.webp_url}" download class="btn-dl">WEBP</a>` : ''}
          ${asset.sheet_url ? `<a href="${asset.sheet_url}" download class="btn-dl">Sheet</a>` : ''}
          <button class="btn-del" onclick="deleteAsset('${asset.base_prefix}')">🗑</button>
        </div>
      `;
      grid.appendChild(card);
    });
  } catch (err) {
    console.error("Library error:", err);
  }
}

function downloadZip() {
  const name = document.getElementById('charName').value.trim();
  window.location.href = `/api/download_zip?name=${encodeURIComponent(name)}`;
}

async function deleteAsset(prefix) {
  if (!confirm(`Delete asset files for '${prefix}'?`)) return;
  try {
    await fetch(`/api/delete_asset?prefix=${encodeURIComponent(prefix)}`, { method: 'POST' });
    loadAssetLibrary();
  } catch (err) {
    alert("Delete error: " + err);
  }
}

function openOutputFolder() {
  fetch('/api/open_folder', { method: 'POST' });
}

window.onload = init;
</script>

</body>
</html>
"""


# ============================================================
# HTTP Request Handler
# ============================================================
class StudioHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/" or self.path.startswith("/index"):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_STUDIO.encode("utf-8"))
            return

        elif self.path == "/api/presets":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(DEFAULT_52_ANIMATIONS).encode("utf-8"))
            return

        elif self.path == "/api/vfx_presets":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(VFX_PRESETS).encode("utf-8"))
            return

        elif self.path.startswith("/api/llm_status"):
            available = False
            active_model = "None"
            all_models = []
            err_msg = ""
            try:
                with urllib.request.urlopen(f"{OLLAMA_URL}/api/tags", timeout=4.0) as r:
                    tags = json.loads(r.read().decode())
                    all_models = [m["name"] for m in tags.get("models", [])]
                    if len(all_models) > 0:
                        available = True
                        active_model = "qwen2.5:3b" if any("qwen" in m for m in all_models) else all_models[0]
            except Exception as e:
                err_msg = str(e)

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "available": available,
                "model": active_model,
                "models": all_models,
                "error": err_msg
            }).encode("utf-8"))
            return

        elif self.path.startswith("/api/status"):
            data = GLOBAL_JOB_MGR.get_status()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(data).encode("utf-8"))
            return

        elif self.path.startswith("/api/library"):
            assets = []
            if os.path.exists(OUTPUT_DIR):
                files = sorted(os.listdir(OUTPUT_DIR), key=lambda x: os.path.getmtime(os.path.join(OUTPUT_DIR, x)), reverse=True)
                seen_prefixes = set()
                for f in files:
                    if f.endswith("_anim_00001_.png") or f.endswith("_spritesheet_00001_.png"):
                        prefix = f.replace("_anim_00001_.png", "").replace("_spritesheet_00001_.png", "").replace("_retro_anim_00001_.png", "")
                        if prefix in seen_prefixes:
                            continue
                        seen_prefixes.add(prefix)

                        parts = prefix.split("_", 1)
                        char_tag = parts[0]
                        action_tag = parts[1] if len(parts) > 1 else prefix

                        mtime = os.path.getmtime(os.path.join(OUTPUT_DIR, f))
                        date_str = time.strftime("%b %d, %H:%M", time.localtime(mtime))

                        apng_file = f"{prefix}_anim_00001_.png"
                        if not os.path.exists(os.path.join(OUTPUT_DIR, apng_file)):
                            apng_file = f"{prefix}_retro_anim_00001_.png"

                        webp_file = f"{prefix}_webp_00001_.webp"
                        sheet_file = f"{prefix}_spritesheet_00001_.png"

                        assets.append({
                            "name": prefix,
                            "char": char_tag,
                            "action": action_tag,
                            "type": "vfx" if "vfx" in prefix or any(v["id"] in prefix for v in VFX_PRESETS) else "character",
                            "date": date_str,
                            "base_prefix": prefix,
                            "preview_url": f"/output/{apng_file}" if os.path.exists(os.path.join(OUTPUT_DIR, apng_file)) else f"/output/{sheet_file}",
                            "apng_url": f"/output/{apng_file}" if os.path.exists(os.path.join(OUTPUT_DIR, apng_file)) else None,
                            "webp_url": f"/output/{webp_file}" if os.path.exists(os.path.join(OUTPUT_DIR, webp_file)) else None,
                            "sheet_url": f"/output/{sheet_file}" if os.path.exists(os.path.join(OUTPUT_DIR, sheet_file)) else None,
                        })

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(assets).encode("utf-8"))
            return

        elif self.path.startswith("/api/download_zip"):
            query = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query)
            char_filter = params.get("name", [""])[0].lower()

            zip_filename = f"{char_filter or 'sprites'}_pack.zip"
            zip_path = os.path.join(SHARED_DIR, zip_filename)

            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
                for f in os.listdir(OUTPUT_DIR):
                    if not char_filter or char_filter in f.lower():
                        full_f = os.path.join(OUTPUT_DIR, f)
                        zf.write(full_f, arcname=f)

            self.send_response(200)
            self.send_header("Content-Type", "application/zip")
            self.send_header("Content-Disposition", f'attachment; filename="{zip_filename}"')
            self.end_headers()
            with open(zip_path, "rb") as z:
                self.wfile.write(z.read())
            return

        elif self.path.startswith("/output/"):
            filename = self.path.replace("/output/", "").split("?")[0]
            file_path = os.path.join(OUTPUT_DIR, filename)
            if os.path.exists(file_path):
                self.send_response(200)
                if filename.endswith(".png"):
                    self.send_header("Content-Type", "image/png")
                elif filename.endswith(".webp"):
                    self.send_header("Content-Type", "image/webp")
                self.end_headers()
                with open(file_path, "rb") as f:
                    self.wfile.write(f.read())
                return
            else:
                self.send_response(404)
                self.end_headers()
                return

        elif self.path.startswith("/input/"):
            filename = self.path.replace("/input/", "").split("?")[0]
            file_path = os.path.join(INPUT_DIR, filename)
            if os.path.exists(file_path):
                self.send_response(200)
                self.send_header("Content-Type", "image/png")
                self.end_headers()
                with open(file_path, "rb") as f:
                    self.wfile.write(f.read())
                return
            else:
                self.send_response(404)
                self.end_headers()
                return

        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        content_len = int(self.headers.get("Content-Length", 0))
        raw_body = self.rfile.read(content_len).decode("utf-8") if content_len > 0 else "{}"
        try:
            data = json.loads(raw_body)
        except Exception:
            data = {}

        if self.path == "/api/upload_reference":
            filename = data.get("filename", "ref_image.png")
            base64_str = data.get("data", "")
            if "," in base64_str:
                base64_str = base64_str.split(",", 1)[1]

            img_bytes = base64.b64decode(base64_str)
            clean_filename = f"ref_{uuid.uuid4().hex[:8]}_{filename}"

            dest_shared = os.path.join(INPUT_DIR, clean_filename)
            with open(dest_shared, "wb") as f:
                f.write(img_bytes)

            if os.path.exists(COMFY_INPUT_DIR):
                dest_comfy = os.path.join(COMFY_INPUT_DIR, clean_filename)
                with open(dest_comfy, "wb") as f:
                    f.write(img_bytes)

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "status": "ok",
                "filename": clean_filename,
                "url": f"/input/{clean_filename}"
            }).encode("utf-8"))
            return

        elif self.path == "/api/optimize_prompt":
            p_type = data.get("type", "character")
            char_desc = data.get("char_desc", "")
            style = data.get("style", "Smooth HD Vector Art")
            is_creature = bool(data.get("is_creature", False))

            if p_type == "character":
                sys_prompt = (
                    "You are an expert game sprite visual designer. Given a rough character description, write a rich, concise visual prompt for a 2D game character sprite. "
                    "Specify outfit materials, armor/clothing details, weapons, color palette, luminous glows or accents, and sharp silhouette. "
                    "Keep it to 2-3 sentences. Output ONLY the visual description without any conversational intro, quotes, or markdown."
                )
                user_msg = f"Character concept: {char_desc}\nArt medium: {style}\nType: {'Creature/Monster' if is_creature else 'Humanoid'}"
                optimized, model = query_ollama(user_msg, sys_prompt)

                if not optimized:
                    # Heuristic fallback
                    optimized = f"{char_desc}, dynamic game character with crisp sharp outlines, detailed layered attire, signature weapons, high contrast vibrant color palette, distinct iconic silhouette"
                    model = "heuristic"

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"optimized": optimized, "model": model}).encode("utf-8"))
                return

            elif p_type == "move":
                action_item = data.get("action_item", {})
                act_name = action_item.get("name", "Strike")
                act_desc = action_item.get("creature" if is_creature else "human", "")

                sys_prompt = (
                    "You are an expert 2D game combat and animation director. Given a character concept and animation move name, "
                    "describe the sequential 4-frame animation motion (anticipation, strike/leap, apex/impact, recovery). "
                    "Keep it to one concise visual sentence. Output ONLY the action description without quotes, intro, or markdown."
                )
                user_msg = f"Character: {char_desc}\nMove: {act_name}\nBase Motion: {act_desc}"
                optimized, model = query_ollama(user_msg, sys_prompt)

                if not optimized:
                    optimized = f"{act_desc}, dynamic fluid action keyframes with energetic anticipation, powerful strike impact, and crisp recovery motion"
                    model = "heuristic"

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"optimized": optimized, "model": model}).encode("utf-8"))
                return

            elif p_type == "all_moves":
                moves = data.get("moves", [])
                results = []
                for m in moves:
                    base = m.get("creature" if is_creature else "human", "")
                    enhanced = f"{base}, with character signature aura and dynamic fluid keyframes"
                    results.append({"id": m["id"], "prompt": enhanced})

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"optimized_moves": results}).encode("utf-8"))
                return

        elif self.path == "/api/generate":
            char_name = data.get("char_name", "hero")
            char_desc = data.get("char_desc", "")
            seed = int(data.get("seed", 424242))
            style = data.get("style", "Smooth HD Vector Art")
            output_style = data.get("output_style", "standard")
            is_creature = bool(data.get("is_creature", False))
            ref_image = data.get("ref_image")
            selected_moves = data.get("selected_moves", [])
            fw = int(data.get("frame_width", 256))
            fh = int(data.get("frame_height", 256))

            jobs_to_track = []
            for move in selected_moves:
                custom_p = move.get("custom_prompt")
                prompt_dict = build_character_graph(
                    char_desc, move, is_creature, style, output_style, seed, char_name, custom_p, fw, fh, ref_image
                )
                try:
                    pid = send_to_comfy(prompt_dict)
                    jobs_to_track.append({
                        "pid": pid,
                        "id": move.get("id"),
                        "name": move.get("name"),
                        "status": "queued",
                        "preview_url": None
                    })
                except Exception as e:
                    print(f"Error queueing {move.get('id')}: {e}")

            batch_id = uuid.uuid4().hex[:8]
            GLOBAL_JOB_MGR.start_batch(batch_id, char_name, jobs_to_track)

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "status": "ok",
                "batch_id": batch_id,
                "queued": len(jobs_to_track)
            }).encode("utf-8"))
            return

        elif self.path == "/api/cancel_batch":
            GLOBAL_JOB_MGR.cancel_batch()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "cancelled"}).encode("utf-8"))
            return

        elif self.path == "/api/generate_single":
            char_name = data.get("char_name", "hero")
            char_desc = data.get("char_desc", "")
            seed = int(data.get("seed", 424242))
            style = data.get("style", "Smooth HD Vector Art")
            output_style = data.get("output_style", "standard")
            is_creature = bool(data.get("is_creature", False))
            ref_image = data.get("ref_image")
            action_item = data.get("action_item", {})
            custom_p = data.get("custom_prompt")
            fw = int(data.get("frame_width", 256))
            fh = int(data.get("frame_height", 256))

            prompt_dict = build_character_graph(
                char_desc, action_item, is_creature, style, output_style, seed, char_name, custom_p, fw, fh, ref_image
            )
            pid = send_to_comfy(prompt_dict)

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok", "pid": pid}).encode("utf-8"))
            return

        elif self.path == "/api/generate_vfx":
            vfx_name = data.get("vfx_name", "vfx")
            vfx_desc = data.get("vfx_desc", "energy fireball projectile")
            style = data.get("style", "Smooth HD Vector Art")
            seed = int(data.get("seed", 987654))
            fw = int(data.get("frame_width", 256))
            fh = int(data.get("frame_height", 256))

            prompt_dict = build_vfx_graph(vfx_desc, vfx_name, style, seed, "vfx", fw, fh)
            pid = send_to_comfy(prompt_dict)

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok", "pid": pid}).encode("utf-8"))
            return

        elif self.path.startswith("/api/delete_asset"):
            query = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query)
            prefix = params.get("prefix", [""])[0]

            if prefix and os.path.exists(OUTPUT_DIR):
                for f in os.listdir(OUTPUT_DIR):
                    if f.startswith(prefix):
                        try:
                            os.remove(os.path.join(OUTPUT_DIR, f))
                        except Exception:
                            pass

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "deleted"}).encode("utf-8"))
            return

        elif self.path == "/api/open_folder":
            if sys.platform == "win32":
                subprocess.Popen(f'explorer "{OUTPUT_DIR}"')
            self.send_response(200)
            self.end_headers()
            return

        self.send_response(404)
        self.end_headers()


def run_server():
    server = HTTPServer(("127.0.0.1", PORT), StudioHandler)
    print(f"============================================================")
    print(f"🎮 2D Sprite, Animation & VFX Studio Running on http://127.0.0.1:{PORT}")
    print(f"Connected to ComfyUI on {COMFY_URL}")
    print(f"Connected to Ollama on {OLLAMA_URL}")
    print(f"============================================================")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.server_close()


if __name__ == "__main__":
    run_server()
