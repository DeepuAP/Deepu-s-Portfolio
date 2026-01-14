import firebase_admin
from firebase_admin import credentials, db
from PIL import Image, ImageSequence
import os

# --- AUTH ---
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_credentials.json")
    firebase_admin.initialize_app(cred, {'databaseURL': "https://loga-portfolio-default-rtdb.firebaseio.com"})

def process_gifs():
    ref = db.reference('projects')
    projects = ref.get() or {}
    
    static_dir = "static"
    if not os.path.exists(static_dir):
        print(f"Static directory {static_dir} not found.")
        return

    # Map filename -> duration
    durations = {}

    print("--- Processing GIFs in static/ ---")
    for filename in os.listdir(static_dir):
        if filename.lower().endswith('.gif'):
            filepath = os.path.join(static_dir, filename)
            try:
                with Image.open(filepath) as img:
                    if getattr(img, "is_animated", False):
                        frames = [frame.copy() for frame in ImageSequence.Iterator(img)]
                        
                        # Calculate Duration
                        duration_ms = sum(f.info.get('duration', 100) for f in frames)
                        durations[filename] = duration_ms
                        
                        # Set loop=1 (Play Once) if needed
                        # We re-save to ensure consistency
                        frames[0].save(
                            filepath,
                            save_all=True,
                            append_images=frames[1:],
                            loop=1, # 1 = Play Once (0 = Infinite)
                            duration=[f.info.get('duration', 100) for f in frames],
                            disposal=2
                        )
                        print(f"✅ processed {filename}: Duration={duration_ms}ms, Loop=1")
                    else:
                        print(f"ℹ️ {filename} is not animated.")
            except Exception as e:
                print(f"❌ Error processing {filename}: {e}")

    # Update Firebase Projects
    print("\n--- Updating Firebase Data ---")
    for pid, pdata in projects.items():
        if pdata.get('media_type') == 'gif':
            gif_name = pdata.get('gifFilename')
            if gif_name and gif_name in durations:
                ref.child(pid).update({'duration': durations[gif_name]})
                print(f"✅ Updated Project '{pdata.get('title')}' with duration {durations[gif_name]}ms")
            else:
                print(f"⚠️ Project '{pdata.get('title')}': GIF {gif_name} not found or calculated.")

if __name__ == "__main__":
    process_gifs()
