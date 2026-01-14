from PIL import Image
import os

def check_gif_loop(path):
    if not os.path.exists(path):
        print(f"File not found: {path}")
        return
    
    try:
        with Image.open(path) as img:
            print(f"Checking {path}...")
            print(f"Format: {img.format}")
            print(f"Animated: {getattr(img, 'is_animated', False)}")
            print(f"Frames: {getattr(img, 'n_frames', 1)}")
            print(f"Loop Info from info: {img.info.get('loop', 'Not found in info')}")
            
            # Check duration of first few frames
            print(f"Duration: {img.info.get('duration', 'N/A')}")
            
    except Exception as e:
        print(f"Error reading {path}: {e}")

if __name__ == "__main__":
    check_gif_loop("static/Portfolio.gif")
