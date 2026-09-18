"""
2D Sprite, Animation & VFX Studio Web Application
Includes:
- Full 52-Move Character Generator (Humanoid & Non-Humanoid)
- Customizable Individual Move Prompts + Add Custom Animations
- Single Animation Re-run & Custom Seeds
- 2D VFX / Projectiles / Orbs / Slashes / Particles Generator
- Complete Asset Library Tab (Preview, Filter, Re-run, Delete, Single Download & ZIP Download)
- Clean Single-Output Option (No duplicate retro outputs by default)
- AMD Radeon RX 9060 XT (ROCm) / ComfyUI Integration
"""

import sys
import os
import json
import time
import zipfile
import subprocess
import urllib.request
import urllib.error
from http.server import HTTPServer, BaseHTTPRequestHandler

# Windows console UTF-8 fix
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

COMFY_URL = "http://127.0.0.1:8188"
PORT = 8190
SHARED_DIR = r"C:\Users\USER\AppData\Local\Comfy-Desktop\ComfyUI-Shared"
OUTPUT_DIR = os.path.join(SHARED_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

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


def build_character_graph(char_desc, action_item, is_creature, style, output_style, seed, char_name, custom_action_prompt=None):
    """Builds the ComfyUI workflow JSON for a character animation."""
    if custom_action_prompt and custom_action_prompt.strip():
        action_desc = custom_action_prompt.strip()
    else:
        action_desc = action_item["creature"] if is_creature else action_item["human"]

    prefix = f"{char_name}_{action_item['id']}"
    fps = float(action_item.get("fps", 6.0))

    style_prompts = {
        "16-bit Retro Pixel Art": "clean 16-bit retro game sprite, bold outlines, flat solid pure white background, distinct separated frames, full body",
        "Chibi Brawler Sprite": "cute stylized chibi proportions, bold clean cel-shading outlines, vibrant colors, flat solid pure white background, separated frames",
        "8-bit Classic NES": "authentic 8-bit pixel art, restricted retro palette, crisp pixel grid, flat solid pure white background",
        "Hand-drawn 2D Cartoon": "hand-drawn 2D animation frames, expressive dynamic poses, flat solid pure white background",
        "Modern Flat Vector": "modern flat vector art, clean sharp geometry, high contrast, flat solid pure white background"
    }
    style_str = style_prompts.get(style, style_prompts["16-bit Retro Pixel Art"])

    pos_prompt = (
        f"pixel art 2d sprite sheet of {char_desc}, "
        f"4 animation frames in a horizontal sequence, "
        f"{action_desc}, {style_str}"
    )
    neg_prompt = "3d render, photorealistic, noise, gradients, complex background, blurry, overlapping frames, text, watermark"

    graph = {
        "1": {"class_type": "UNETLoader", "inputs": {"unet_name": "z_image_turbo_bf16.safetensors", "weight_dtype": "default"}},
        "2": {"class_type": "CLIPLoader", "inputs": {"clip_name": "qwen_3_4b.safetensors", "type": "qwen_image"}},
        "3": {"class_type": "VAELoader", "inputs": {"vae_name": "z-image-ae.safetensors"}},
        "4": {"class_type": "TextEncodeZImageOmni", "inputs": {"prompt": pos_prompt, "auto_resize_images": True, "clip": ["2", 0]}},
        "5": {"class_type": "TextEncodeZImageOmni", "inputs": {"prompt": neg_prompt, "auto_resize_images": True, "clip": ["2", 0]}},
        "6": {"class_type": "EmptyLatentImage", "inputs": {"width": 1024, "height": 256, "batch_size": 1}},
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
        "10": {"class_type": "SplitImageToTileList", "inputs": {"image": ["9", 0], "tile_width": 256, "tile_height": 256, "overlap": 0}},
        "11": {"class_type": "RebatchImages", "inputs": {"images": ["10", 0], "batch_size": 4}},
    }

    # Output selection (fixes the duplicate output issue)
    if output_style == "retro":
        # Downscale & Upscale using Nearest-Exact
        graph["14"] = {"class_type": "ImageScale", "inputs": {"image": ["11", 0], "upscale_method": "nearest-exact", "width": 48, "height": 48, "crop": "disabled"}}
        graph["15"] = {"class_type": "ImageScale", "inputs": {"image": ["14", 0], "upscale_method": "nearest-exact", "width": 192, "height": 192, "crop": "disabled"}}
        graph["16"] = {"class_type": "SaveAnimatedPNG", "inputs": {"images": ["15", 0], "filename_prefix": f"{prefix}_anim", "fps": fps, "compress_level": 4}}
        graph["17"] = {"class_type": "ImageGrid", "inputs": {"images": ["15", 0], "columns": 4, "cell_width": 192, "cell_height": 192, "padding": 0}}
        graph["18"] = {"class_type": "SaveImage", "inputs": {"images": ["17", 0], "filename_prefix": f"{prefix}_spritesheet"}}
    elif output_style == "both":
        # Save standard
        graph["12"] = {"class_type": "SaveAnimatedPNG", "inputs": {"images": ["11", 0], "filename_prefix": f"{prefix}_anim", "fps": fps, "compress_level": 4}}
        graph["13"] = {"class_type": "SaveAnimatedWEBP", "inputs": {"images": ["11", 0], "filename_prefix": f"{prefix}_webp", "fps": fps, "lossless": True, "quality": 90, "method": "default"}}
        graph["17"] = {"class_type": "ImageGrid", "inputs": {"images": ["11", 0], "columns": 4, "cell_width": 256, "cell_height": 256, "padding": 0}}
        graph["18"] = {"class_type": "SaveImage", "inputs": {"images": ["17", 0], "filename_prefix": f"{prefix}_spritesheet"}}
        # And save retro
        graph["14"] = {"class_type": "ImageScale", "inputs": {"image": ["11", 0], "upscale_method": "nearest-exact", "width": 48, "height": 48, "crop": "disabled"}}
        graph["15"] = {"class_type": "ImageScale", "inputs": {"image": ["14", 0], "upscale_method": "nearest-exact", "width": 192, "height": 192, "crop": "disabled"}}
        graph["16"] = {"class_type": "SaveAnimatedPNG", "inputs": {"images": ["15", 0], "filename_prefix": f"{prefix}_retro_anim", "fps": fps, "compress_level": 4}}
    else:
        # Standard clean output (Default: SINGLE ANIMATION)
        graph["12"] = {"class_type": "SaveAnimatedPNG", "inputs": {"images": ["11", 0], "filename_prefix": f"{prefix}_anim", "fps": fps, "compress_level": 4}}
        graph["13"] = {"class_type": "SaveAnimatedWEBP", "inputs": {"images": ["11", 0], "filename_prefix": f"{prefix}_webp", "fps": fps, "lossless": True, "quality": 90, "method": "default"}}
        graph["17"] = {"class_type": "ImageGrid", "inputs": {"images": ["11", 0], "columns": 4, "cell_width": 256, "cell_height": 256, "padding": 0}}
        graph["18"] = {"class_type": "SaveImage", "inputs": {"images": ["17", 0], "filename_prefix": f"{prefix}_spritesheet"}}

    return graph


def build_vfx_graph(vfx_desc, vfx_id, seed, name_prefix):
    """Builds the ComfyUI workflow JSON for a 2D VFX / Projectile / Particle animation."""
    prefix = f"{name_prefix}_{vfx_id}"
    pos_prompt = (
        f"pixel art 2d sprite sheet of {vfx_desc}, "
        f"4 sequential animation frames in a horizontal sequence, "
        f"high contrast vibrant video game special effect VFX, clean bold outlines, "
        f"flat solid pure white background, distinct separated frames"
    )
    neg_prompt = "human, character, face, body, photorealistic, noise, gradients, complex background, text, watermark, blurry, overlapping frames"

    return {
        "1": {"class_type": "UNETLoader", "inputs": {"unet_name": "z_image_turbo_bf16.safetensors", "weight_dtype": "default"}},
        "2": {"class_type": "CLIPLoader", "inputs": {"clip_name": "qwen_3_4b.safetensors", "type": "qwen_image"}},
        "3": {"class_type": "VAELoader", "inputs": {"vae_name": "z-image-ae.safetensors"}},
        "4": {"class_type": "TextEncodeZImageOmni", "inputs": {"prompt": pos_prompt, "auto_resize_images": True, "clip": ["2", 0]}},
        "5": {"class_type": "TextEncodeZImageOmni", "inputs": {"prompt": neg_prompt, "auto_resize_images": True, "clip": ["2", 0]}},
        "6": {"class_type": "EmptyLatentImage", "inputs": {"width": 1024, "height": 256, "batch_size": 1}},
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
        "10": {"class_type": "SplitImageToTileList", "inputs": {"image": ["9", 0], "tile_width": 256, "tile_height": 256, "overlap": 0}},
        "11": {"class_type": "RebatchImages", "inputs": {"images": ["10", 0], "batch_size": 4}},
        "12": {"class_type": "SaveAnimatedPNG", "inputs": {"images": ["11", 0], "filename_prefix": f"{prefix}_anim", "fps": 8.0, "compress_level": 4}},
        "13": {"class_type": "SaveAnimatedWEBP", "inputs": {"images": ["11", 0], "filename_prefix": f"{prefix}_webp", "fps": 8.0, "lossless": True, "quality": 90, "method": "default"}},
        "14": {"class_type": "ImageGrid", "inputs": {"images": ["11", 0], "columns": 4, "cell_width": 256, "cell_height": 256, "padding": 0}},
        "15": {"class_type": "SaveImage", "inputs": {"images": ["14", 0], "filename_prefix": f"{prefix}_spritesheet"}}
    }


def send_to_comfy(prompt_dict):
    req = urllib.request.Request(
        f"{COMFY_URL}/prompt",
        data=json.dumps({"prompt": prompt_dict}).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))["prompt_id"]


HTML_STUDIO = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>2D Sprite & VFX Studio</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
:root {
  --bg-main: #090d16;
  --bg-card: #131b2e;
  --bg-item: #1a253d;
  --border: #233354;
  --text-main: #f8fafc;
  --text-muted: #94a3b8;
  --accent: #38bdf8;
  --accent-glow: rgba(56, 189, 248, 0.25);
  --success: #10b981;
  --purple: #c084fc;
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

.container { max-width: 1360px; margin: 24px auto; padding: 0 20px; }
.grid-layout { display: grid; grid-template-columns: 440px 1fr; gap: 24px; }

.panel {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 20px;
}

h2 { font-size: 16px; font-weight: 700; color: #fff; margin-bottom: 16px; display: flex; justify-content: space-between; align-items: center; }

.form-group { margin-bottom: 16px; }
label { display: block; font-size: 11px; font-weight: 700; color: var(--text-muted); margin-bottom: 6px; text-transform: uppercase; letter-spacing: 0.5px; }
input[type="text"], textarea, select {
  width: 100%;
  background: var(--bg-item);
  border: 1px solid var(--border);
  border-radius: 8px;
  color: #fff;
  padding: 10px 12px;
  font-size: 13px;
  outline: none;
  transition: border-color 0.2s;
}
input[type="text"]:focus, textarea:focus, select:focus { border-color: var(--accent); }
textarea { resize: vertical; min-height: 80px; }

.radio-pill-group { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
.radio-pill {
  background: var(--bg-item);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 10px;
  text-align: center;
  cursor: pointer;
  font-size: 13px;
  font-weight: 600;
  transition: all 0.2s;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}
.radio-pill input { display: none; }
.radio-pill.active { background: #0369a1; border-color: var(--accent); color: #fff; box-shadow: 0 0 12px var(--accent-glow); }
.radio-pill small { font-size: 10px; font-weight: 400; opacity: 0.8; }

.btn-trigger {
  width: 100%;
  background: linear-gradient(135deg, #0284c7, #2563eb);
  color: #fff;
  border: none;
  border-radius: 10px;
  padding: 14px;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
  box-shadow: 0 4px 15px var(--accent-glow);
  transition: transform 0.1s, opacity 0.2s;
  margin-top: 10px;
}
.btn-trigger:hover { opacity: 0.95; transform: translateY(-1px); }
.btn-trigger:active { transform: translateY(1px); }

.btn-sm {
  background: var(--bg-item);
  border: 1px solid var(--border);
  color: var(--text-muted);
  border-radius: 6px;
  padding: 5px 10px;
  font-size: 11px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.15s;
}
.btn-sm:hover { color: #fff; border-color: var(--accent); }
.btn-sm.btn-danger:hover { color: #fff; border-color: var(--danger); background: #881337; }

.anim-selector-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  gap: 8px;
  flex-wrap: wrap;
}

.anim-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 10px;
  max-height: 650px;
  overflow-y: auto;
  padding-right: 6px;
}

.anim-card {
  background: var(--bg-item);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 10px 12px;
  transition: all 0.15s;
}
.anim-card.selected { border-color: var(--accent); background: #132742; }
.anim-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px; }
.anim-title { font-size: 13px; font-weight: 700; color: #fff; display: flex; align-items: center; gap: 8px; }
.anim-title input { width: 16px; height: 16px; accent-color: var(--accent); cursor: pointer; }
.anim-cat { font-size: 10px; color: var(--text-muted); }
.anim-prompt-box {
  width: 100%;
  background: #0d1526;
  border: 1px solid #1e293b;
  border-radius: 6px;
  padding: 6px 8px;
  font-size: 11px;
  color: #cbd5e1;
  outline: none;
  resize: none;
  height: 44px;
}
.anim-prompt-box:focus { border-color: var(--accent); }

.status-bar {
  margin-top: 16px;
  background: #0a1120;
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 12px;
  font-size: 12px;
}
.status-header { display: flex; justify-content: space-between; margin-bottom: 6px; font-weight: 600; }
.progress-track { height: 6px; background: #334155; border-radius: 3px; overflow: hidden; }
.progress-fill { height: 100%; width: 0%; background: var(--accent); transition: width 0.3s; }

/* Asset Library */
.library-filters {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  align-items: center;
  flex-wrap: wrap;
}
.library-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 16px;
}
.asset-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 12px;
  overflow: hidden;
  transition: transform 0.15s, border-color 0.15s;
}
.asset-card:hover { border-color: var(--accent); transform: translateY(-2px); }
.asset-preview {
  width: 100%;
  height: 180px;
  object-fit: contain;
  background: repeating-conic-gradient(#1a263d 0% 25%, #0e1626 0% 50%) 50% / 16px 16px;
  display: block;
}
.asset-body { padding: 12px; }
.asset-title { font-size: 13px; font-weight: 700; color: #fff; margin-bottom: 4px; word-break: break-all; }
.asset-meta { font-size: 11px; color: var(--text-muted); margin-bottom: 10px; display: flex; justify-content: space-between; }
.asset-actions { display: flex; gap: 6px; flex-wrap: wrap; }
</style>
</head>
<body>

<header>
  <div class="logo">
    👾 <span>SpriteStudio</span> AI
    <span class="badge">AMD ROCm RX 9060 XT</span>
  </div>

  <div class="nav-tabs">
    <button class="nav-tab active" onclick="switchTab('tabCharacter')">🎮 Character Studio (52 Moves)</button>
    <button class="nav-tab" onclick="switchTab('tabVFX')">✨ VFX & Projectiles</button>
    <button class="nav-tab" onclick="switchTab('tabLibrary')">📦 Asset Library</button>
  </div>

  <div style="display:flex; gap:10px;">
    <button class="btn-sm" onclick="openOutputFolder()">📂 Open Output Folder</button>
  </div>
</header>

<div class="container">
  <!-- TAB 1: CHARACTER STUDIO -->
  <div class="tab-content active" id="tabCharacter">
    <div class="grid-layout">
      <!-- Left Config -->
      <div class="panel">
        <h2>1. Character Configuration</h2>

        <div class="form-group">
          <label>Character Name / Prefix</label>
          <input type="text" id="charName" value="shadow_ninja" placeholder="e.g. cyber_wolf, flame_mage">
        </div>

        <div class="form-group">
          <label>Visual Description</label>
          <textarea id="charDesc" placeholder="Describe outfit, armor, weapons, colors, fur, silhouette...">a swift cyberpunk shadow ninja with glowing neon blue scarf, dark stealth suit, and dual energetic katanas</textarea>
        </div>

        <div class="form-group">
          <label>Anatomy & Movement Type</label>
          <div class="radio-pill-group">
            <label class="radio-pill active" id="pillHuman">
              <input type="radio" name="anatomy" value="human" checked onchange="toggleAnatomy(false)">
              <span>👤 Humanoid</span>
              <small>Punches, kicks, weapons</small>
            </label>
            <label class="radio-pill" id="pillCreature">
              <input type="radio" name="anatomy" value="creature" onchange="toggleAnatomy(true)">
              <span>🐾 Non-Humanoid</span>
              <small>Claws, bites, tail, pounces</small>
            </label>
          </div>
        </div>

        <div class="form-group">
          <label>Style Preset</label>
          <select id="artStyle">
            <option value="16-bit Retro Pixel Art">16-bit Retro Pixel Art (Default)</option>
            <option value="Chibi Brawler Sprite">Chibi Brawler Sprite (Cute, HD)</option>
            <option value="8-bit Classic NES">8-bit Classic NES</option>
            <option value="Hand-drawn 2D Cartoon">Hand-drawn 2D Cartoon</option>
            <option value="Modern Flat Vector">Modern Flat Vector</option>
          </select>
        </div>

        <div class="form-group">
          <label>Output Format (No Duplicates)</label>
          <select id="outputStyle">
            <option value="standard" selected>Clean Cel-Shaded Animation (Single output)</option>
            <option value="retro">PixelLab Chunky Pixel Art (Nearest-Neighbor)</option>
            <option value="both">Both (Standard + Retro duplicate)</option>
          </select>
        </div>

        <div class="form-group" style="display:grid; grid-template-columns: 1fr 1fr; gap:10px;">
          <div>
            <label>Seed</label>
            <input type="text" id="charSeed" value="424242">
          </div>
          <div>
            <label>&nbsp;</label>
            <button class="btn-sm" style="width:100%; height:38px;" onclick="randomizeSeed()">🎲 Randomize</button>
          </div>
        </div>

        <button class="btn-trigger" id="btnGenerate" onclick="startGeneration()">
          🚀 Generate Sprite Pack (<span id="selectedCount">52</span> Animations)
        </button>

        <div class="status-bar" id="statusBar" style="display:none;">
          <div class="status-header">
            <span id="statusText">Queuing animations...</span>
            <span id="statusPercent">0%</span>
          </div>
          <div class="progress-track">
            <div class="progress-fill" id="progressFill"></div>
          </div>
        </div>
      </div>

      <!-- Right Move Selector -->
      <div class="panel">
        <h2>
          <span>2. Moveset & Customization</span>
          <div style="display:flex; gap:8px;">
            <button class="btn-sm" style="background:#0284c7; color:#fff;" onclick="openAddCustomModal()">➕ Add Custom Move</button>
            <span style="font-size:12px; color:var(--accent);" id="countBadge">52 / 52 Selected</span>
          </div>
        </h2>

        <div class="anim-selector-bar">
          <div>
            <button class="btn-sm" onclick="selectAll(true)">Select All</button>
            <button class="btn-sm" onclick="selectAll(false)">Deselect All</button>
          </div>
          <div style="display:flex; gap:4px; flex-wrap:wrap;">
            <button class="btn-sm" onclick="filterCategory('All')">All</button>
            <button class="btn-sm" onclick="filterCategory('Locomotion')">Locomotion</button>
            <button class="btn-sm" onclick="filterCategory('Standing Strikes')">Strikes</button>
            <button class="btn-sm" onclick="filterCategory('Aerial Attacks')">Air</button>
            <button class="btn-sm" onclick="filterCategory('Crouch Moves')">Crouch</button>
            <button class="btn-sm" onclick="filterCategory('Reactions & Statuses')">Status</button>
            <button class="btn-sm" onclick="filterCategory('Specials')">Specials</button>
          </div>
        </div>

        <div class="anim-grid" id="animGrid"></div>
      </div>
    </div>
  </div>

  <!-- TAB 2: VFX & PROJECTILE GENERATOR -->
  <div class="tab-content" id="tabVFX">
    <div class="grid-layout">
      <!-- Left Config -->
      <div class="panel">
        <h2>1. VFX Generator Setup</h2>

        <div class="form-group">
          <label>VFX Set Name</label>
          <input type="text" id="vfxName" value="fire_magic" placeholder="e.g. plasma_fx, slash_effects">
        </div>

        <div class="form-group">
          <label>Custom VFX Prompt (or pick from right)</label>
          <textarea id="vfxDesc" placeholder="e.g. swirling blue electric orb with crackling lightning discharge...">fiery plasma energy fireball projectile flying forward, swirling orange flame particles, glowing bright combustion trail</textarea>
        </div>

        <div class="form-group" style="display:grid; grid-template-columns: 1fr 1fr; gap:10px;">
          <div>
            <label>Seed</label>
            <input type="text" id="vfxSeed" value="987654">
          </div>
          <div>
            <label>&nbsp;</label>
            <button class="btn-sm" style="width:100%; height:38px;" onclick="randomizeVFXSeed()">🎲 Randomize</button>
          </div>
        </div>

        <button class="btn-trigger" style="background: linear-gradient(135deg, #e11d48, #9333ea);" onclick="startVFXGeneration()">
          ✨ Generate VFX Animation (<span id="vfxSelectedCount">1</span> Selected)
        </button>

        <div class="status-bar" id="vfxStatusBar" style="display:none;">
          <div class="status-header">
            <span id="vfxStatusText">Queuing VFX...</span>
          </div>
        </div>
      </div>

      <!-- Right VFX Preset Selector -->
      <div class="panel">
        <h2>2. VFX Presets Library (Click to Load or Select Multiple)</h2>
        <div class="anim-grid" id="vfxGrid"></div>
      </div>
    </div>
  </div>

  <!-- TAB 3: ASSET LIBRARY -->
  <div class="tab-content" id="tabLibrary">
    <div class="panel">
      <h2>
        <span>Asset Library</span>
        <button class="btn-sm" onclick="loadAssetLibrary()">🔄 Refresh</button>
      </h2>

      <div class="library-filters">
        <input type="text" id="libSearch" placeholder="🔍 Search by character or action name..." style="width:280px;" oninput="filterLibrary()">
        <select id="libTypeFilter" style="width:180px;" onchange="filterLibrary()">
          <option value="all">All Types</option>
          <option value="character">Characters</option>
          <option value="vfx">VFX & Projectiles</option>
        </select>
        <button class="btn-sm" onclick="downloadSelectedCharZip()">📦 Download Character ZIP</button>
      </div>

      <div class="library-grid" id="libraryGrid">
        <div style="color:var(--text-muted); font-size:13px;">Loading assets...</div>
      </div>
    </div>
  </div>
</div>

<!-- Modal: Add Custom Move -->
<div id="modalAddCustom" style="display:none; position:fixed; inset:0; background:rgba(0,0,0,0.7); z-index:200; align-items:center; justify-content:center;">
  <div class="panel" style="width:480px; max-width:90%;">
    <h2>➕ Add Custom Animation Move</h2>
    <div class="form-group">
      <label>Move ID (e.g. wall_climb, tail_whip)</label>
      <input type="text" id="customMoveId" placeholder="e.g. wall_climb">
    </div>
    <div class="form-group">
      <label>Move Display Name</label>
      <input type="text" id="customMoveName" placeholder="e.g. Wall Climb">
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
        <option value="Specials">Specials</option>
      </select>
    </div>
    <div class="form-group">
      <label>Action Prompt Description</label>
      <textarea id="customMovePrompt" placeholder="Describe the character's exact movement, limbs, weapon, trail..."></textarea>
    </div>
    <div style="display:flex; justify-content:flex-end; gap:8px;">
      <button class="btn-sm" onclick="closeAddCustomModal()">Cancel</button>
      <button class="btn-sm" style="background:#0284c7; color:#fff;" onclick="submitCustomMove()">Add to Moveset</button>
    </div>
  </div>
</div>

<!-- Modal: Re-run Move -->
<div id="modalRerun" style="display:none; position:fixed; inset:0; background:rgba(0,0,0,0.7); z-index:200; align-items:center; justify-content:center;">
  <div class="panel" style="width:460px; max-width:90%;">
    <h2>🔁 Re-run Animation Move</h2>
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

async function init() {
  const res1 = await fetch('/api/presets');
  animations = await res1.json();

  const res2 = await fetch('/api/vfx_presets');
  vfxList = await res2.json();

  renderAnimations();
  renderVFX();
  loadAssetLibrary();
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

  animations.forEach((anim, idx) => {
    if (catFilter !== 'All' && anim.cat !== catFilter) return;

    const card = document.createElement('div');
    card.className = 'anim-card' + (anim.selected !== false ? ' selected' : '');

    const defaultDesc = isCreatureMode ? anim.creature : anim.human;
    const currentDesc = anim.custom_prompt !== undefined ? anim.custom_prompt : defaultDesc;

    card.innerHTML = `
      <div class="anim-header">
        <label class="anim-title">
          <input type="checkbox" ${anim.selected !== false ? 'checked' : ''} onchange="toggleSelect(${idx}, this.checked)">
          <span>${anim.name}</span>
        </label>
        <span class="anim-cat">${anim.cat}</span>
      </div>
      <textarea class="anim-prompt-box" placeholder="Customize action prompt..." onchange="updateCustomPrompt(${idx}, this.value)">${currentDesc}</textarea>
      <div style="display:flex; justify-content:flex-end; margin-top:6px;">
        <button class="btn-sm" onclick="openRerunModalSingle(${idx})" title="Generate only this move">🔁 Re-run</button>
      </div>
    `;
    grid.appendChild(card);
  });
  updateCounts();
}

function toggleSelect(idx, val) {
  animations[idx].selected = val;
  updateCounts();
}

function updateCustomPrompt(idx, val) {
  animations[idx].custom_prompt = val;
}

function selectAll(state) {
  animations.forEach(a => a.selected = state);
  renderAnimations();
}

function filterCategory(cat) {
  renderAnimations(cat);
}

function updateCounts() {
  const count = animations.filter(a => a.selected !== false).length;
  document.getElementById('selectedCount').innerText = count;
  document.getElementById('countBadge').innerText = `${count} / ${animations.length} Selected`;
}

function randomizeSeed() {
  document.getElementById('charSeed').value = Math.floor(Math.random() * 900000) + 100000;
}

function randomizeVFXSeed() {
  document.getElementById('vfxSeed').value = Math.floor(Math.random() * 900000) + 100000;
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
function openRerunModalSingle(idx) {
  const anim = animations[idx];
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
  const seed = parseInt(document.getElementById('rerunSeed').value) || 424242;
  const style = document.getElementById('artStyle').value;
  const outputStyle = document.getElementById('outputStyle').value;
  const customPrompt = document.getElementById('rerunPrompt').value.trim();

  closeRerunModal();

  const payload = {
    char_name: name,
    char_desc: desc,
    seed: seed,
    style: style,
    output_style: outputStyle,
    is_creature: isCreatureMode,
    action_item: currentRerunItem,
    custom_prompt: customPrompt
  };

  try {
    await fetch('/api/generate_single', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(payload)
    });
    alert(`Queued ${currentRerunItem.name} for regeneration!`);
    loadAssetLibrary();
  } catch (err) {
    alert("Error: " + err);
  }
}

/* Batch Generation */
async function startGeneration() {
  const name = document.getElementById('charName').value.trim() || 'hero';
  const desc = document.getElementById('charDesc').value.trim();
  const seed = parseInt(document.getElementById('charSeed').value) || 424242;
  const style = document.getElementById('artStyle').value;
  const outputStyle = document.getElementById('outputStyle').value;
  const selectedMoves = animations.filter(a => a.selected !== false);

  if (selectedMoves.length === 0) {
    alert("Please select at least one animation!");
    return;
  }

  const btn = document.getElementById('btnGenerate');
  btn.disabled = true;
  btn.innerText = "⏳ Queuing into ComfyUI...";

  document.getElementById('statusBar').style.display = 'block';
  document.getElementById('statusText').innerText = `Queuing ${selectedMoves.length} animations...`;

  const payload = {
    char_name: name,
    char_desc: desc,
    seed: seed,
    style: style,
    output_style: outputStyle,
    is_creature: isCreatureMode,
    selected_moves: selectedMoves
  };

  try {
    await fetch('/api/generate', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(payload)
    });
    btn.innerText = `Running Batch (${selectedMoves.length} items)`;
    startPolling();
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
      const pct = data.total_queued > 0 ? Math.min(100, Math.round((data.completed_count / data.total_queued) * 100)) : 0;

      document.getElementById('statusPercent').innerText = `${pct}%`;
      document.getElementById('progressFill').style.width = `${pct}%`;
      document.getElementById('statusText').innerText = data.is_running ? "Processing on AMD Radeon RX 9060 XT..." : "Batch Finished!";

      if (!data.is_running && pct >= 100) {
        clearInterval(pollingInterval);
        document.getElementById('btnGenerate').disabled = false;
        document.getElementById('btnGenerate').innerText = "🚀 Generate Sprite Pack";
        loadAssetLibrary();
      }
    } catch (e) {
      console.error(e);
    }
  }, 3000);
}

/* VFX Tab */
function renderVFX() {
  const grid = document.getElementById('vfxGrid');
  grid.innerHTML = '';

  vfxList.forEach((vfx, idx) => {
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
      <div style="font-size:11px; color:var(--text-muted);">${vfx.desc}</div>
    `;
    grid.appendChild(card);
  });
}

async function startVFXGeneration() {
  const name = document.getElementById('vfxName').value.trim() || 'vfx';
  const desc = document.getElementById('vfxDesc').value.trim();
  const seed = parseInt(document.getElementById('vfxSeed').value) || 987654;

  const payload = {
    vfx_name: name,
    vfx_desc: desc,
    seed: seed
  };

  try {
    await fetch('/api/generate_vfx', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(payload)
    });
    alert(`Queued VFX '${name}' to ComfyUI!`);
    loadAssetLibrary();
  } catch (err) {
    alert("Error: " + err);
  }
}

/* Asset Library */
async function loadAssetLibrary() {
  const res = await fetch('/api/library');
  libraryData = await res.json();
  filterLibrary();
}

function filterLibrary() {
  const search = document.getElementById('libSearch').value.toLowerCase();
  const typeFilter = document.getElementById('libTypeFilter').value;
  const grid = document.getElementById('libraryGrid');
  grid.innerHTML = '';

  const filtered = libraryData.filter(item => {
    const matchSearch = item.name.toLowerCase().includes(search) || item.char.toLowerCase().includes(search);
    const matchType = typeFilter === 'all' ? true : item.type === typeFilter;
    return matchSearch && matchType;
  });

  if (filtered.length === 0) {
    grid.innerHTML = '<div style="color:var(--text-muted); font-size:13px; grid-column:1/-1;">No assets matching filter found.</div>';
    return;
  }

  filtered.forEach(item => {
    const card = document.createElement('div');
    card.className = 'asset-card';
    card.innerHTML = `
      <img src="${item.preview_url}" class="asset-preview" alt="${item.name}">
      <div class="asset-body">
        <div class="asset-title">${item.char}: ${item.action}</div>
        <div class="asset-meta">
          <span>${item.type.toUpperCase()}</span>
          <span>${item.date}</span>
        </div>
        <div class="asset-actions">
          <a href="${item.apng_url}" download class="btn-sm" title="Download Looping APNG">⬇️ APNG</a>
          ${item.webp_url ? `<a href="${item.webp_url}" download class="btn-sm" title="Download WebP">⬇️ WebP</a>` : ''}
          ${item.sheet_url ? `<a href="${item.sheet_url}" download class="btn-sm" title="Download Sprite Sheet">⬇️ Sheet</a>` : ''}
          <button class="btn-sm btn-danger" onclick="deleteAsset('${item.base_prefix}')" title="Delete Asset">🗑️</button>
        </div>
      </div>
    `;
    grid.appendChild(card);
  });
}

async function deleteAsset(prefix) {
  if (!confirm(`Delete all files for '${prefix}'?`)) return;
  await fetch(`/api/delete_asset?prefix=${encodeURIComponent(prefix)}`, {method: 'POST'});
  loadAssetLibrary();
}

function downloadSelectedCharZip() {
  const search = document.getElementById('libSearch').value.trim() || document.getElementById('charName').value.trim();
  window.location.href = `/api/download_zip?name=${encodeURIComponent(search)}`;
}

async function openOutputFolder() {
  await fetch('/api/open_folder', {method: 'POST'});
}

window.onload = init;
</script>

</body>
</html>
"""


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

        elif self.path.startswith("/api/status"):
            is_running = False
            try:
                with urllib.request.urlopen(f"{COMFY_URL}/queue", timeout=2) as r:
                    q = json.loads(r.read().decode())
                    is_running = len(q.get("queue_running", [])) > 0 or len(q.get("queue_pending", [])) > 0
            except Exception:
                pass

            data = {
                "is_running": is_running,
                "completed_count": getattr(self.server, "completed_count", 0),
                "total_queued": getattr(self.server, "last_queued_count", 0)
            }

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(data).encode("utf-8"))
            return

        elif self.path.startswith("/api/library"):
            assets = []
            if os.path.exists(OUTPUT_DIR):
                files = sorted(os.listdir(OUTPUT_DIR), key=lambda x: os.path.getmtime(os.path.join(OUTPUT_DIR, x)), reverse=True)
                # Find all unique prefixes
                seen_prefixes = set()
                for f in files:
                    if f.endswith("_anim_00001_.png") or f.endswith("_spritesheet_00001_.png"):
                        prefix = f.replace("_anim_00001_.png", "").replace("_spritesheet_00001_.png", "").replace("_retro_anim_00001_.png", "")
                        if prefix in seen_prefixes:
                            continue
                        seen_prefixes.add(prefix)

                        # Parts
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
            import urllib.parse
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
            filename = self.path.replace("/output/", "")
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

        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        if self.path == "/api/generate":
            content_len = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(content_len).decode("utf-8"))

            char_name = data.get("char_name", "hero")
            char_desc = data.get("char_desc", "")
            seed = int(data.get("seed", 424242))
            style = data.get("style", "16-bit Retro Pixel Art")
            output_style = data.get("output_style", "standard")
            is_creature = bool(data.get("is_creature", False))
            selected_moves = data.get("selected_moves", [])

            queued = []
            for move in selected_moves:
                custom_p = move.get("custom_prompt")
                prompt_dict = build_character_graph(char_desc, move, is_creature, style, output_style, seed, char_name, custom_p)
                try:
                    pid = send_to_comfy(prompt_dict)
                    queued.append(pid)
                except Exception as e:
                    print(f"Error queueing {move.get('id')}: {e}")

            self.server.last_queued_count = len(queued)
            self.server.completed_count = 0

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok", "queued": len(queued)}).encode("utf-8"))
            return

        elif self.path == "/api/generate_single":
            content_len = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(content_len).decode("utf-8"))

            char_name = data.get("char_name", "hero")
            char_desc = data.get("char_desc", "")
            seed = int(data.get("seed", 424242))
            style = data.get("style", "16-bit Retro Pixel Art")
            output_style = data.get("output_style", "standard")
            is_creature = bool(data.get("is_creature", False))
            action_item = data.get("action_item", {})
            custom_p = data.get("custom_prompt")

            prompt_dict = build_character_graph(char_desc, action_item, is_creature, style, output_style, seed, char_name, custom_p)
            pid = send_to_comfy(prompt_dict)

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok", "pid": pid}).encode("utf-8"))
            return

        elif self.path == "/api/generate_vfx":
            content_len = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(content_len).decode("utf-8"))

            vfx_name = data.get("vfx_name", "vfx")
            vfx_desc = data.get("vfx_desc", "energy fireball projectile")
            seed = int(data.get("seed", 987654))

            prompt_dict = build_vfx_graph(vfx_desc, vfx_name, seed, "vfx")
            pid = send_to_comfy(prompt_dict)

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok", "pid": pid}).encode("utf-8"))
            return

        elif self.path.startswith("/api/delete_asset"):
            import urllib.parse
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
    server.last_queued_count = 0
    server.completed_count = 0
    print(f"============================================================")
    print(f"🎮 2D Sprite, Animation & VFX Studio Running on http://127.0.0.1:{PORT}")
    print(f"Connected to ComfyUI on {COMFY_URL}")
    print(f"============================================================")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.server_close()


if __name__ == "__main__":
    run_server()
