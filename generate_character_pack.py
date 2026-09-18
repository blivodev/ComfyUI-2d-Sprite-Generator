"""
ComfyUI Automated 2D Sprite Pack Generator (20 Defaults + 4 Directions/Specials)
Optimized for AMD Radeon RX 9060 XT 16GB with Z-Image-Turbo and BiRefNet Toonout.
"""

import sys
import os
import json
import time
import argparse
import urllib.request
import urllib.error

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


COMFY_URL = "http://127.0.0.1:8188"

# 20 Core Game Animations + 4 Directional / Special Animations
ANIMATION_PRESETS = [
    # --- LOCOMOTION & MOVEMENT (6) ---
    {
        "id": "01_idle",
        "name": "Idle Stance",
        "action": "standing idle breathing animation, subtle bobbing stance, relaxed breathing motion frames",
        "fps": 5.0,
        "frames": 4
    },
    {
        "id": "02_walk",
        "name": "Walk (Side View)",
        "action": "side view walking cycle, sequential walking footsteps motion, character moving forward",
        "fps": 6.0,
        "frames": 4
    },
    {
        "id": "03_run",
        "name": "Run Cycle",
        "action": "running cycle, forward running fast sprint motion, dynamic running footsteps",
        "fps": 8.0,
        "frames": 4
    },
    {
        "id": "04_sprint",
        "name": "Sprint / Dash",
        "action": "full speed dash sprint motion, leaning forward with motion blur trail effect",
        "fps": 10.0,
        "frames": 4
    },
    {
        "id": "05_jump",
        "name": "Jump Leap",
        "action": "jumping up into air, crouch anticipation leap into apex pose",
        "fps": 6.0,
        "frames": 4
    },
    {
        "id": "06_fall_land",
        "name": "Fall & Land",
        "action": "falling downwards through air and crouch impact landing on ground",
        "fps": 6.0,
        "frames": 4
    },

    # --- COMBAT & ABILITIES (8) ---
    {
        "id": "07_attack_light",
        "name": "Attack Light",
        "action": "quick light jab strike attack animation, fast weapon swing forward",
        "fps": 8.0,
        "frames": 4
    },
    {
        "id": "08_attack_heavy",
        "name": "Attack Heavy",
        "action": "heavy two-handed overhead strike slash attack, powerful downward swing",
        "fps": 7.0,
        "frames": 4
    },
    {
        "id": "09_attack_combo",
        "name": "Attack Combo / Spin",
        "action": "spinning roundhouse slash combo attack animation, sweeping strike",
        "fps": 8.0,
        "frames": 4
    },
    {
        "id": "10_ranged_shoot",
        "name": "Ranged Shoot / Throw",
        "action": "ranged projectile throw or shooting weapon animation, release motion",
        "fps": 7.0,
        "frames": 4
    },
    {
        "id": "11_cast_spell",
        "name": "Cast Magic Spell",
        "action": "magic spell cast animation, raising weapon or hands channeling glowing energy",
        "fps": 6.0,
        "frames": 4
    },
    {
        "id": "12_block_guard",
        "name": "Block / Shield Guard",
        "action": "defensive block guard stance, raising shield or arms absorbing impact",
        "fps": 6.0,
        "frames": 4
    },
    {
        "id": "13_dodge_roll",
        "name": "Dodge Roll",
        "action": "evasive dodge roll forward on the ground, tumbling recovery motion",
        "fps": 8.0,
        "frames": 4
    },
    {
        "id": "14_crouch",
        "name": "Crouch & Sneak",
        "action": "crouching low to ground, sneaking stealth crawling stance",
        "fps": 5.0,
        "frames": 4
    },

    # --- REACTIONS & CONDITIONS (6) ---
    {
        "id": "15_hurt",
        "name": "Hurt / Flinch",
        "action": "taking damage, flinching backwards in pain from hit impact",
        "fps": 7.0,
        "frames": 4
    },
    {
        "id": "16_stunned",
        "name": "Stunned / Dizzy",
        "action": "dazed dizzy stunned animation, wobbling head and off-balance posture",
        "fps": 5.0,
        "frames": 4
    },
    {
        "id": "17_knockdown",
        "name": "Knockdown",
        "action": "knocked off feet flying backwards onto back on the ground",
        "fps": 6.0,
        "frames": 4
    },
    {
        "id": "18_get_up",
        "name": "Get Up Recovery",
        "action": "standing back up from the ground recovery animation onto feet",
        "fps": 6.0,
        "frames": 4
    },
    {
        "id": "19_death",
        "name": "Death / Defeat",
        "action": "defeat collapse animation, falling limp onto the floor",
        "fps": 5.0,
        "frames": 4
    },
    {
        "id": "20_victory",
        "name": "Victory / Celebration",
        "action": "victory celebration cheer animation, raising fist in triumph",
        "fps": 6.0,
        "frames": 4
    },

    # --- 4 DIRECTIONAL & SPECIAL VARIATIONS (4) ---
    {
        "id": "21_walk_down",
        "name": "Walk Down (Facing South / Front)",
        "action": "front view facing camera walking forward downwards, frontal footsteps cycle",
        "fps": 6.0,
        "frames": 4
    },
    {
        "id": "22_walk_up",
        "name": "Walk Up (Facing North / Back)",
        "action": "back view walking away from camera upwards, rear footsteps cycle",
        "fps": 6.0,
        "frames": 4
    },
    {
        "id": "23_walk_left",
        "name": "Walk Left (Facing West)",
        "action": "side view walking to the left, sequential footsteps moving leftwards",
        "fps": 6.0,
        "frames": 4
    },
    {
        "id": "24_special_ultimate",
        "name": "Ultimate Special Move",
        "action": "super special ultimate power surge charging stance, glowing aura burst pose",
        "fps": 7.0,
        "frames": 4
    }
]


def build_workflow_prompt(char_desc, action_info, seed, base_prefix):
    """Constructs the ComfyUI node execution graph for a single animation."""
    prefix = f"{base_prefix}_{action_info['id']}"
    num_frames = action_info.get("frames", 4)
    canvas_w = 256 * num_frames
    canvas_h = 256
    
    pos_prompt = (
        f"pixel art 2d sprite sheet of {char_desc}, "
        f"{num_frames} animation frames in a horizontal sequence, "
        f"{action_info['action']}, "
        f"clean 16-bit retro game sprite, bold outlines, flat solid pure white background, "
        f"distinct separated frames, full body, consistent character design"
    )
    neg_prompt = "3d render, photorealistic, noise, gradients, complex background, text, watermark, blurry, overlapping frames"

    return {
        "1": {"class_type": "UNETLoader", "inputs": {"unet_name": "z_image_turbo_bf16.safetensors", "weight_dtype": "default"}},
        "2": {"class_type": "CLIPLoader", "inputs": {"clip_name": "qwen_3_4b.safetensors", "type": "qwen_image"}},
        "3": {"class_type": "VAELoader", "inputs": {"vae_name": "z-image-ae.safetensors"}},
        "4": {"class_type": "TextEncodeZImageOmni", "inputs": {"prompt": pos_prompt, "auto_resize_images": True, "clip": ["2", 0]}},
        "5": {"class_type": "TextEncodeZImageOmni", "inputs": {"prompt": neg_prompt, "auto_resize_images": True, "clip": ["2", 0]}},
        "6": {"class_type": "EmptyLatentImage", "inputs": {"width": canvas_w, "height": canvas_h, "batch_size": 1}},
        "7": {"class_type": "KSampler", "inputs": {
            "model": ["1", 0], "positive": ["4", 0], "negative": ["5", 0], "latent_image": ["6", 0],
            "seed": seed, "control_after_generate": "fixed", "steps": 8, "cfg": 1.0,
            "sampler_name": "dpmpp_sde", "scheduler": "beta", "denoise": 1.0
        }},
        "8": {"class_type": "VAEDecode", "inputs": {"samples": ["7", 0], "vae": ["3", 0]}},
        # Background cutout using BiRefNet Toonout
        "9": {"class_type": "BiRefNetRMBG", "inputs": {
            "image": ["8", 0], "model": "BiRefNet_toonout", "mask_blur": 0, "mask_offset": 0,
            "invert_output": False, "refine_foreground": False, "background": "Alpha", "background_color": "#222222"
        }},
        # Slice strip into frames
        "10": {"class_type": "SplitImageToTileList", "inputs": {"image": ["9", 0], "tile_width": 256, "tile_height": 256, "overlap": 0}},
        # Rebatch frames
        "11": {"class_type": "RebatchImages", "inputs": {"images": ["10", 0], "batch_size": num_frames}},
        # Save transparent Animated APNG preview
        "12": {"class_type": "SaveAnimatedPNG", "inputs": {
            "images": ["11", 0], "filename_prefix": f"{prefix}_anim", "fps": float(action_info["fps"]), "compress_level": 4
        }},
        # Save Animated WebP
        "13": {"class_type": "SaveAnimatedWEBP", "inputs": {
            "images": ["11", 0], "filename_prefix": f"{prefix}_webp", "fps": float(action_info["fps"]),
            "lossless": True, "quality": 90, "method": "default"
        }},
        # PixelLab Retro Downscaler / Upscaler
        "14": {"class_type": "ImageScale", "inputs": {"image": ["11", 0], "upscale_method": "nearest-exact", "width": 48, "height": 48, "crop": "disabled"}},
        "15": {"class_type": "ImageScale", "inputs": {"image": ["14", 0], "upscale_method": "nearest-exact", "width": 192, "height": 192, "crop": "disabled"}},
        # Save Retro APNG
        "16": {"class_type": "SaveAnimatedPNG", "inputs": {
            "images": ["15", 0], "filename_prefix": f"{prefix}_retro_anim", "fps": float(action_info["fps"]), "compress_level": 4
        }},
        # Pack into clean master Sprite Sheet
        "17": {"class_type": "ImageGrid", "inputs": {"images": ["15", 0], "columns": num_frames, "cell_width": 192, "cell_height": 192, "padding": 0}},
        "18": {"class_type": "SaveImage", "inputs": {"images": ["17", 0], "filename_prefix": f"{prefix}_spritesheet"}}
    }


def queue_prompt(prompt_dict):
    """Sends a single job to ComfyUI's queue."""
    req = urllib.request.Request(
        f"{COMFY_URL}/prompt",
        data=json.dumps({"prompt": prompt_dict}).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))["prompt_id"]


def is_comfy_running():
    try:
        urllib.request.urlopen(f"{COMFY_URL}/system_stats", timeout=3)
        return True
    except Exception:
        return False


def main():
    parser = argparse.ArgumentParser(description="Generate complete 24-animation 2D sprite set using ComfyUI")
    parser.add_argument("--character", "-c", type=str, default="a brave chibi knight in silver armor with a blue cape and glowing sword",
                        help="Description of the character")
    parser.add_argument("--name", "-n", type=str, default="knight",
                        help="Short name/prefix for the character (e.g. knight, goblin, mage)")
    parser.add_argument("--seed", "-s", type=int, default=424242,
                        help="Base random seed for visual consistency across animations")
    parser.add_argument("--count", type=int, default=24,
                        help="How many animations to generate (up to 24: 20 defaults + 4 specials)")

    args = parser.parse_args()

    print("=" * 65)
    print(">> 2D SPRITE AUTOMATION PACK (20 Defaults + 4 Specials)")
    print("=" * 65)
    print(f"Character: '{args.character}'")
    print(f"Name Tag:  '{args.name}'")
    print(f"Base Seed: {args.seed}")
    print(f"Server:    {COMFY_URL}")
    print("=" * 65)

    if not is_comfy_running():
        print("[ERROR] ComfyUI does not appear to be running on http://127.0.0.1:8188.")
        print("Please ensure ComfyUI is running before launching the batch.")
        sys.exit(1)

    selected_presets = ANIMATION_PRESETS[:args.count]
    print(f"\n>> Queuing {len(selected_presets)} animations into ComfyUI...")

    queued_ids = []
    for i, preset in enumerate(selected_presets, 1):
        prompt_dict = build_workflow_prompt(args.character, preset, args.seed, args.name)
        try:
            pid = queue_prompt(prompt_dict)
            queued_ids.append((pid, preset["name"], preset["id"]))
            print(f"  [{i:02d}/{len(selected_presets):02d}] Queued: {preset['name']:<32} (ID: {pid[:8]}...)")
        except urllib.error.HTTPError as e:
            print(f"  [ERROR] Failed to queue {preset['name']}: {e.read().decode('utf-8')}")
        except Exception as e:
            print(f"  [ERROR] Failed to queue {preset['name']}: {e}")

    print("\n" + "=" * 65)
    print(f"[SUCCESS] Successfully queued all {len(queued_ids)} animations!")

    print(f"All files will be automatically written to:")
    print(f"  C:\\Users\\USER\\AppData\\Local\\Comfy-Desktop\\ComfyUI-Shared\\output\\")
    print("\nEach animation produces:")
    print("  1. <name>_<action>_anim.png        -> Transparent Looping APNG")
    print("  2. <name>_<action>_webp.webp       -> High Quality Animated WebP")
    print("  3. <name>_<action>_retro_anim.png  -> PixelLab 16-bit Snapped Animation")
    print("  4. <name>_<action>_spritesheet.png -> Clean Master Sprite Sheet PNG")
    print("=" * 65)


if __name__ == "__main__":
    main()
