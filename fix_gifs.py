from PIL import Image, ImageSequence
import os

def set_gif_loop(directory):
    print(f"Scanning {directory} for GIFs...")
    count = 0
    if not os.path.exists(directory):
        print(f"Directory {directory} does not exist.")
        return

    for filename in os.listdir(directory):
        if filename.lower().endswith('.gif'):
            filepath = os.path.join(directory, filename)
            try:
                with Image.open(filepath) as img:
                    # Check if it's animated
                    if getattr(img, "is_animated", False):
                        frames = [frame.copy() for frame in ImageSequence.Iterator(img)]
                        
                        # Save with loop=0 (infinite) and duration preserved
                        frames[0].save(
                            filepath,
                            save_all=True,
                            append_images=frames[1:],
                            loop=0,
                            duration=img.info.get('duration', 100),
                            disposal=2 # Restore to background color
                        )
                        print(f"✅ Fixed looping for: {filename}")
                        count += 1
                    else:
                        print(f"ℹ️ {filename} is not animated.")
            except Exception as e:
                print(f"❌ Error processing {filename}: {e}")
    
    print(f"Done! Fixed {count} GIFs.")

if __name__ == "__main__":
    set_gif_loop("static")
    # Also check nested assets if any (though user said they moved them to static)
    set_gif_loop("static/assets/thumbnails")
