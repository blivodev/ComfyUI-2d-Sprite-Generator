import torch
import torch.nn.functional as F
import numpy as np
from PIL import Image

# Famous retro pixel art color palettes (RGB 0-255)
PALETTES = {
    "Pico-8 (16 Colors)": np.array([
        [0, 0, 0], [29, 43, 83], [126, 37, 83], [0, 135, 81],
        [171, 82, 54], [95, 87, 79], [194, 195, 199], [255, 241, 232],
        [255, 0, 77], [255, 163, 0], [255, 236, 39], [0, 228, 54],
        [41, 173, 255], [131, 118, 156], [255, 119, 168], [255, 204, 170]
    ], dtype=np.float32),

    "GameBoy (4 Colors)": np.array([
        [15, 56, 15], [48, 98, 48], [139, 172, 15], [155, 188, 15]
    ], dtype=np.float32),

    "NES (54 Colors)": np.array([
        [124, 124, 124], [0, 0, 252], [0, 0, 188], [68, 40, 188], [148, 0, 132],
        [168, 0, 32], [168, 16, 0], [136, 20, 0], [80, 48, 0], [0, 120, 0],
        [0, 104, 0], [0, 88, 0], [0, 64, 88], [0, 0, 0], [188, 188, 188],
        [0, 120, 248], [0, 88, 248], [104, 68, 252], [216, 0, 204], [228, 0, 88],
        [248, 56, 0], [228, 92, 16], [172, 124, 0], [0, 184, 0], [0, 168, 0],
        [0, 168, 68], [0, 136, 136], [248, 248, 248], [60, 188, 252], [104, 136, 252],
        [152, 120, 248], [248, 120, 248], [248, 88, 152], [248, 120, 88], [252, 160, 68],
        [248, 184, 0], [184, 248, 24], [88, 216, 84], [88, 248, 152], [0, 232, 216],
        [120, 120, 120], [252, 252, 252], [164, 228, 252], [184, 184, 248], [216, 184, 248],
        [248, 184, 248], [248, 164, 192], [240, 208, 176], [252, 224, 168], [248, 216, 120],
        [216, 248, 120], [184, 248, 184], [184, 248, 216], [0, 252, 252]
    ], dtype=np.float32),

    "Endesga 32": np.array([
        [190, 74, 47], [215, 118, 67], [234, 212, 170], [228, 166, 114],
        [184, 111, 80], [115, 62, 57], [62, 39, 49], [162, 38, 51],
        [228, 59, 68], [247, 118, 34], [254, 174, 52], [254, 231, 97],
        [99, 199, 77], [62, 137, 72], [38, 92, 66], [25, 60, 62],
        [18, 78, 137], [0, 153, 219], [44, 232, 245], [255, 255, 255],
        [192, 203, 220], [139, 155, 180], [90, 105, 136], [58, 68, 102],
        [38, 43, 68], [24, 20, 37], [255, 0, 68], [254, 231, 97],
        [147, 81, 182], [92, 53, 102], [73, 77, 126], [139, 109, 156]
    ], dtype=np.float32),

    "Sweetie 16": np.array([
        [26, 28, 44], [93, 39, 93], [177, 62, 83], [239, 125, 87],
        [255, 205, 117], [167, 240, 112], [56, 183, 100], [37, 113, 121],
        [41, 54, 111], [59, 93, 201], [65, 166, 246], [115, 239, 247],
        [244, 244, 244], [148, 176, 194], [86, 108, 134], [51, 60, 87]
    ], dtype=np.float32)
}


class SpriteSheetSplitter:
    """
    Slices a generated Sprite Sheet (horizontal strip or grid) into individual animation frames.
    Outputs a batch of images [N, H, W, C] ready for APNG preview or game engines.
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "columns": ("INT", {"default": 8, "min": 1, "max": 64, "step": 1}),
                "rows": ("INT", {"default": 1, "min": 1, "max": 64, "step": 1}),
                "total_frames": ("INT", {"default": 0, "min": 0, "max": 256, "step": 1}),
                "crop_padding": ("INT", {"default": 0, "min": 0, "max": 64, "step": 1}),
            }
        }

    RETURN_TYPES = ("IMAGE", "INT", "INT", "INT")
    RETURN_NAMES = ("frames", "frame_count", "frame_width", "frame_height")
    FUNCTION = "split_sheet"
    CATEGORY = "Sprite/Animation"

    def split_sheet(self, image, columns, rows, total_frames, crop_padding):
        # image tensor: [B, H, W, C]
        if image.ndim == 3:
            image = image.unsqueeze(0)
        
        # Take the first image in batch if multiple were provided
        img = image[0]
        H, W, C = img.shape
        
        cell_w = W // columns
        cell_h = H // rows
        
        max_frames = columns * rows if total_frames <= 0 else min(total_frames, columns * rows)
        frames = []
        
        for r in range(rows):
            for c in range(columns):
                if len(frames) >= max_frames:
                    break
                
                x1 = c * cell_w + crop_padding
                x2 = (c + 1) * cell_w - crop_padding
                y1 = r * cell_h + crop_padding
                y2 = (r + 1) * cell_h - crop_padding
                
                # Bounds check
                x1 = max(0, min(W - 1, x1))
                x2 = max(x1 + 1, min(W, x2))
                y1 = max(0, min(H - 1, y1))
                y2 = max(y1 + 1, min(H, y2))
                
                frame = img[y1:y2, x1:x2, :]
                frames.append(frame.unsqueeze(0))
        
        out_batch = torch.cat(frames, dim=0)
        out_h, out_w = out_batch.shape[1], out_batch.shape[2]
        return (out_batch, len(frames), out_w, out_h)


class SpriteSheetPacker:
    """
    Packs a batch of animation frames into a single clean Sprite Sheet image (grid or strip).
    Supports transparent background (RGBA) or solid background.
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE",),
                "columns": ("INT", {"default": 8, "min": 1, "max": 64, "step": 1}),
                "spacing": ("INT", {"default": 0, "min": 0, "max": 64, "step": 1}),
                "bg_mode": (["transparent", "black", "white", "magenta", "chroma_green"],),
            }
        }

    RETURN_TYPES = ("IMAGE", "INT", "INT")
    RETURN_NAMES = ("sprite_sheet", "sheet_width", "sheet_height")
    FUNCTION = "pack_sheet"
    CATEGORY = "Sprite/Animation"

    def pack_sheet(self, images, columns, spacing, bg_mode):
        # images: [N, H, W, C]
        if images.ndim == 3:
            images = images.unsqueeze(0)
            
        N, H, W, C = images.shape
        cols = min(columns, N)
        rows = int(np.ceil(N / cols))
        
        out_w = cols * W + (cols - 1) * spacing
        out_h = rows * H + (rows - 1) * spacing
        
        has_alpha = (C == 4)
        if bg_mode == "transparent":
            sheet_c = 4
            sheet = torch.zeros((1, out_h, out_w, sheet_c), dtype=images.dtype, device=images.device)
        else:
            sheet_c = 3
            sheet = torch.zeros((1, out_h, out_w, sheet_c), dtype=images.dtype, device=images.device)
            if bg_mode == "white":
                sheet.fill_(1.0)
            elif bg_mode == "magenta":
                sheet[:, :, :, 0] = 1.0
                sheet[:, :, :, 2] = 1.0
            elif bg_mode == "chroma_green":
                sheet[:, :, :, 1] = 1.0
        
        for idx in range(N):
            r = idx // cols
            c = idx % cols
            
            x = c * (W + spacing)
            y = r * (H + spacing)
            
            frame = images[idx]
            if sheet_c == 4:
                if C == 3:
                    # add alpha = 1.0
                    alpha = torch.ones((H, W, 1), dtype=frame.dtype, device=frame.device)
                    frame_rgba = torch.cat([frame, alpha], dim=-1)
                    sheet[0, y:y+H, x:x+W, :] = frame_rgba
                else:
                    sheet[0, y:y+H, x:x+W, :] = frame
            else:
                # RGB sheet
                if C == 4:
                    # alpha blend onto background
                    rgb = frame[:, :, :3]
                    alpha = frame[:, :, 3:4]
                    bg = sheet[0, y:y+H, x:x+W, :3]
                    sheet[0, y:y+H, x:x+W, :3] = rgb * alpha + bg * (1.0 - alpha)
                else:
                    sheet[0, y:y+H, x:x+W, :] = frame[:, :, :3]
                    
        return (sheet, out_w, out_h)


class SpriteGrounderAndCentering:
    """
    Fixes the common issue in AI sprite animations where characters jitter or float.
    Detects sprite foreground bounds in each frame and anchors them stably to Bottom-Center
    so feet stay firmly planted on the ground plane across the walk cycle.
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE",),
                "alignment": (["Bottom-Center", "Center", "Bottom-Left", "Bottom-Right"],),
                "threshold": ("FLOAT", {"default": 0.05, "min": 0.01, "max": 0.99, "step": 0.01}),
                "padding": ("INT", {"default": 8, "min": 0, "max": 64, "step": 1}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("stabilized_frames",)
    FUNCTION = "stabilize_frames"
    CATEGORY = "Sprite/Animation"

    def stabilize_frames(self, images, alignment, threshold, padding):
        N, H, W, C = images.shape
        out_frames = []
        
        for i in range(N):
            frame = images[i]
            if C == 4:
                mask = (frame[:, :, 3] > threshold)
            else:
                # RGB: difference from corner background
                bg_val = frame[0, 0, :]
                diff = torch.norm(frame - bg_val, dim=-1)
                mask = (diff > threshold)
                
            coords = torch.nonzero(mask)
            if len(coords) == 0:
                out_frames.append(frame.unsqueeze(0))
                continue
                
            y_min, x_min = coords.min(dim=0)[0]
            y_max, x_max = coords.max(dim=0)[0]
            
            spr_h = (y_max - y_min + 1).item()
            spr_w = (x_max - x_min + 1).item()
            
            cropped_spr = frame[y_min:y_max+1, x_min:x_max+1, :]
            
            # Place into fresh canvas of size H, W
            canvas = torch.zeros((H, W, C), dtype=frame.dtype, device=frame.device)
            
            if alignment == "Bottom-Center":
                dst_y = max(0, H - spr_h - padding)
                dst_x = max(0, (W - spr_w) // 2)
            elif alignment == "Center":
                dst_y = max(0, (H - spr_h) // 2)
                dst_x = max(0, (W - spr_w) // 2)
            elif alignment == "Bottom-Left":
                dst_y = max(0, H - spr_h - padding)
                dst_x = padding
            else: # Bottom-Right
                dst_y = max(0, H - spr_h - padding)
                dst_x = max(0, W - spr_w - padding)
                
            fit_h = min(spr_h, H - dst_y)
            fit_w = min(spr_w, W - dst_x)
            
            canvas[dst_y:dst_y+fit_h, dst_x:dst_x+fit_w, :] = cropped_spr[:fit_h, :fit_w, :]
            out_frames.append(canvas.unsqueeze(0))
            
        return (torch.cat(out_frames, dim=0),)


class PixelArtProcessor:
    """
    Transforms any sprite generation into crisp, retro pixel art like PixelLab / SpriteFusion:
    - Downscales to authentic game resolutions (32x32, 48x48, 64x64, 128x128).
    - Snaps to retro palettes (PICO-8, GameBoy, NES, Endesga 32, Sweetie 16).
    - Adds an optional crisp 1-pixel outline.
    - Upscales cleanly using Nearest-Neighbor to high-res display without blur.
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE",),
                "pixel_size": ("INT", {"default": 64, "min": 16, "max": 512, "step": 8}),
                "palette": (["None (Original)", "Pico-8 (16 Colors)", "GameBoy (4 Colors)", "NES (54 Colors)", "Endesga 32", "Sweetie 16"],),
                "outline": (["None", "Black 1px", "Dark Tone 1px", "White 1px"],),
                "upscale_factor": ("INT", {"default": 4, "min": 1, "max": 16, "step": 1}),
            }
        }

    RETURN_TYPES = ("IMAGE", "IMAGE")
    RETURN_NAMES = ("pixel_art_scaled", "pixel_art_native")
    FUNCTION = "process_pixel_art"
    CATEGORY = "Sprite/Animation"

    def process_pixel_art(self, images, pixel_size, palette, outline, upscale_factor):
        # images: [B, H, W, C]
        B, H, W, C = images.shape
        device = images.device
        
        # Calculate aspect ratio
        aspect = W / H
        target_h = pixel_size
        target_w = max(8, int(round(pixel_size * aspect)))
        
        # 1. Downscale to pixel grid using area interpolation
        # Permute to [B, C, H, W] for torch interpolate
        imgs_t = images.permute(0, 3, 1, 2)
        downsampled = F.interpolate(imgs_t, size=(target_h, target_w), mode='area')
        
        # Back to [B, H, W, C]
        down_frames = downsampled.permute(0, 2, 3, 1)
        
        # 2. Outline processing if requested
        if outline != "None" and C == 4:
            for b in range(B):
                alpha = down_frames[b, :, :, 3]
                # binary mask
                solid = (alpha > 0.4).float()
                # 4-connectivity dilation
                solid_padded = F.pad(solid.unsqueeze(0).unsqueeze(0), (1, 1, 1, 1), mode='constant', value=0)
                dilated = (solid_padded[:, :, 2:, 1:-1] + solid_padded[:, :, :-2, 1:-1] + 
                           solid_padded[:, :, 1:-1, 2:] + solid_padded[:, :, 1:-1, :-2]) > 0
                outline_mask = dilated.squeeze(0).squeeze(0) & (~solid.bool())
                
                if outline == "Black 1px":
                    down_frames[b, outline_mask, :3] = 0.0
                    down_frames[b, outline_mask, 3] = 1.0
                elif outline == "White 1px":
                    down_frames[b, outline_mask, :3] = 1.0
                    down_frames[b, outline_mask, 3] = 1.0
                elif outline == "Dark Tone 1px":
                    down_frames[b, outline_mask, :3] = 0.12
                    down_frames[b, outline_mask, 3] = 1.0

        # 3. Palette snapping
        if palette != "None (Original)" and palette in PALETTES:
            pal_colors = torch.from_numpy(PALETTES[palette] / 255.0).to(device=device, dtype=images.dtype)
            # Shape: [K, 3]
            for b in range(B):
                rgb = down_frames[b, :, :, :3] # [H, W, 3]
                # Distance to each palette color
                diff = rgb.unsqueeze(2) - pal_colors # [H, W, K, 3]
                dist_sq = torch.sum(diff ** 2, dim=-1) # [H, W, K]
                nearest_idx = torch.argmin(dist_sq, dim=-1) # [H, W]
                quantized_rgb = pal_colors[nearest_idx]
                down_frames[b, :, :, :3] = quantized_rgb
                
        # 4. Upscale with Nearest-Neighbor
        native_res = down_frames
        if upscale_factor > 1:
            up_h = target_h * upscale_factor
            up_w = target_w * upscale_factor
            down_t = down_frames.permute(0, 3, 1, 2)
            up_t = F.interpolate(down_t, size=(up_h, up_w), mode='nearest-exact')
            scaled_res = up_t.permute(0, 2, 3, 1)
        else:
            scaled_res = native_res
            
        return (scaled_res, native_res)


class SpriteAnimationLoop:
    """
    Creates animation loop sequences (Forward, Ping-Pong, Reverse) for looping previews.
    Ping-Pong creates smooth back-and-forth loops (0, 1, 2, 3, 2, 1) perfect for idle/breathing/floating.
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE",),
                "loop_mode": (["Forward", "Ping-Pong", "Reverse"],),
                "repeat_count": ("INT", {"default": 1, "min": 1, "max": 10, "step": 1}),
            }
        }

    RETURN_TYPES = ("IMAGE", "INT")
    RETURN_NAMES = ("loop_frames", "total_frames")
    FUNCTION = "create_loop"
    CATEGORY = "Sprite/Animation"

    def create_loop(self, images, loop_mode, repeat_count):
        N = images.shape[0]
        if N <= 1:
            return (images, N)
            
        indices = list(range(N))
        if loop_mode == "Reverse":
            indices = indices[::-1]
        elif loop_mode == "Ping-Pong":
            # 0, 1, 2, ... N-1, N-2, ... 1
            back = indices[-2:0:-1]
            indices = indices + back
            
        final_indices = indices * repeat_count
        looped = images[final_indices]
        return (looped, len(final_indices))


ACTION_PRESETS_DICT = {
    "01_idle": ("standing idle breathing animation, subtle bobbing stance, relaxed breathing motion", 5.0, 4),
    "02_walk": ("side view walking cycle, sequential walking footsteps motion, character moving forward", 6.0, 4),
    "03_run": ("running cycle, forward running fast sprint motion, dynamic running footsteps", 8.0, 4),
    "04_sprint": ("full speed dash sprint motion, leaning forward with motion blur trail effect", 10.0, 4),
    "05_jump": ("jumping up into air, crouch anticipation leap into apex pose", 6.0, 4),
    "06_fall_land": ("falling downwards through air and crouch impact landing on ground", 6.0, 4),
    "07_attack_light": ("quick light jab strike attack animation, fast weapon swing forward", 8.0, 4),
    "08_attack_heavy": ("heavy two-handed overhead strike slash attack, powerful downward swing", 7.0, 4),
    "09_attack_combo": ("spinning roundhouse slash combo attack animation, sweeping strike", 8.0, 4),
    "10_ranged_shoot": ("ranged projectile throw or shooting weapon animation, release motion", 7.0, 4),
    "11_cast_spell": ("magic spell cast animation, raising weapon or hands channeling glowing energy", 6.0, 4),
    "12_block_guard": ("defensive block guard stance, raising shield or arms absorbing impact", 6.0, 4),
    "13_dodge_roll": ("evasive dodge roll forward on the ground, tumbling recovery motion", 8.0, 4),
    "14_crouch": ("crouching low to ground, sneaking stealth crawling stance", 5.0, 4),
    "15_hurt": ("taking damage, flinching backwards in pain from hit impact", 7.0, 4),
    "16_stunned": ("dazed dizzy stunned animation, wobbling head and off-balance posture", 5.0, 4),
    "17_knockdown": ("knocked off feet flying backwards onto back on the ground", 6.0, 4),
    "18_get_up": ("standing back up from the ground recovery animation onto feet", 6.0, 4),
    "19_death": ("defeat collapse animation, falling limp onto the floor", 5.0, 4),
    "20_victory": ("victory celebration cheer animation, raising fist in triumph", 6.0, 4),
    "21_walk_down": ("front view facing camera walking forward downwards, frontal footsteps cycle", 6.0, 4),
    "22_walk_up": ("back view walking away from camera upwards, rear footsteps cycle", 6.0, 4),
    "23_walk_left": ("side view walking to the left, sequential footsteps moving leftwards", 6.0, 4),
    "24_special_ultimate": ("super special ultimate power surge charging stance, glowing aura burst pose", 7.0, 4)
}


class SpriteActionPresetSelector:
    """
    Selects from the 20 Core Game Animations + 4 Directional/Specials,
    combines with character description, and outputs formatted prompt + parameters.
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "character_description": ("STRING", {"multiline": True, "default": "a brave chibi knight in silver armor with a blue cape and glowing sword"}),
                "action_preset": (list(ACTION_PRESETS_DICT.keys()), {"default": "01_idle"}),
                "style": (["16-bit Retro Pixel Art", "Chibi Brawler Sprite", "8-bit Classic NES", "Hand-drawn 2D Cartoon", "Modern Flat Vector"],),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "FLOAT", "INT")
    RETURN_NAMES = ("positive_prompt", "action_name", "recommended_fps", "recommended_frames")
    FUNCTION = "get_preset"
    CATEGORY = "Sprite/Animation"

    def get_preset(self, character_description, action_preset, style):
        desc, fps, frames = ACTION_PRESETS_DICT.get(action_preset, ("", 6.0, 4))
        
        style_tokens = {
            "16-bit Retro Pixel Art": "clean 16-bit retro game sprite, bold outlines, flat solid pure white background, distinct separated frames, full body",
            "Chibi Brawler Sprite": "cute chibi proportions, bold clean cel-shading outlines, saturated colors, flat solid pure white background, separated frames",
            "8-bit Classic NES": "authentic 8-bit pixel art, restricted retro palette, crisp pixel grid, flat solid pure white background",
            "Hand-drawn 2D Cartoon": "hand-drawn 2D animation frames, smooth outlines, expressive poses, flat solid pure white background",
            "Modern Flat Vector": "modern flat vector art, clean sharp geometry, high contrast, flat solid pure white background"
        }
        
        pos_prompt = (
            f"pixel art 2d sprite sheet of {character_description}, "
            f"{frames} animation frames in a horizontal sequence, "
            f"{desc}, {style_tokens.get(style, '')}"
        )
        
        return (pos_prompt, action_preset, fps, frames)


NODE_CLASS_MAPPINGS = {
    "SpriteSheetSplitter": SpriteSheetSplitter,
    "SpriteSheetPacker": SpriteSheetPacker,
    "SpriteGrounderAndCentering": SpriteGrounderAndCentering,
    "PixelArtProcessor": PixelArtProcessor,
    "SpriteAnimationLoop": SpriteAnimationLoop,
    "SpriteActionPresetSelector": SpriteActionPresetSelector
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SpriteSheetSplitter": "✂️ Sprite Sheet Splitter",
    "SpriteSheetPacker": "📦 Sprite Sheet Packer",
    "SpriteGrounderAndCentering": "⚓ Sprite Grounder & Centering",
    "PixelArtProcessor": "👾 Pixel Art Processor (PixelLab Style)",
    "SpriteAnimationLoop": "🔄 Sprite Animation Looper",
    "SpriteActionPresetSelector": "🎯 Sprite Action Preset (20+4 Selector)"
}

