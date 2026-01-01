import shutil
import os
import datetime

def zip_extension():
    source_dir = r"c:\Users\Vedant Bapuji Patil\OneDrive\Desktop\Hackathon\Veritas-AI\extension\dist"
    output_filename = f"Veritas-AI-Extension-v1.1.0"
    output_path = r"c:\Users\Vedant Bapuji Patil\OneDrive\Desktop\Hackathon\Veritas-AI\extension"
    
    # Create zip
    shutil.make_archive(os.path.join(output_path, output_filename), 'zip', source_dir)
    
    print(f"Extension packaged successfully: {os.path.join(output_path, output_filename)}.zip")

if __name__ == "__main__":
    zip_extension()
