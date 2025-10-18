"""
Download Gemma-2B GGUF model (quantized) for fast local inference.
Much smaller and faster than the full transformers model.
"""

import os
import sys
import requests
from tqdm import tqdm

def download_file(url, destination):
    """Download file with progress bar."""
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    
    os.makedirs(os.path.dirname(destination), exist_ok=True)
    
    with open(destination, 'wb') as f, tqdm(
        desc=os.path.basename(destination),
        total=total_size,
        unit='iB',
        unit_scale=True,
        unit_divisor=1024,
    ) as pbar:
        for data in response.iter_content(chunk_size=1024):
            size = f.write(data)
            pbar.update(size)

def download_gemma_gguf():
    """Download Gemma-2B GGUF model from Hugging Face."""
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    models_dir = os.path.join(script_dir, "models")
    model_file = os.path.join(models_dir, "gemma-2b-Q4_K_M.gguf")
    
    print("=" * 60)
    print("📦 Downloading Gemma-2B GGUF Model (Quantized)")
    print("=" * 60)
    print(f"Save location: {model_file}")
    print("\n⚠️  File size: ~1.5GB (much smaller than full model!)")
    print("⚠️  Estimated time: 2-10 minutes\n")
    
    # Check if model already exists
    if os.path.exists(model_file):
        print(f"✅ Model already exists at {model_file}")
        size_mb = os.path.getsize(model_file) / (1024 * 1024)
        print(f"💾 Size: {size_mb:.1f} MB")
        response = input("\nDo you want to re-download? (y/N): ")
        if response.lower() != 'y':
            print("✅ Using existing model. Exiting.")
            return
    
    # Hugging Face URL for GGUF model
    # Note: Replace with actual repo if different
    model_repo = "bartowski/gemma-2-2b-it-GGUF"
    model_filename = "gemma-2-2b-it-Q4_K_M.gguf"
    url = f"https://huggingface.co/{model_repo}/resolve/main/{model_filename}"
    
    try:
        print(f"\n📥 Downloading from: {model_repo}")
        print(f"🔗 URL: {url}\n")
        
        download_file(url, model_file)
        
        size_mb = os.path.getsize(model_file) / (1024 * 1024)
        
        print("\n" + "=" * 60)
        print("🎉 SUCCESS! GGUF model downloaded.")
        print("=" * 60)
        print(f"📁 Location: {model_file}")
        print(f"💾 Size: {size_mb:.1f} MB")
        print("\n✅ The app will now use this quantized model.")
        print("✅ Much faster and uses less memory!")
        
    except Exception as e:
        print(f"\n❌ Error downloading model: {e}")
        print("\nTroubleshooting:")
        print("1. Check your internet connection")
        print("2. Verify the Hugging Face repo exists")
        print("3. Try downloading manually from:")
        print(f"   {url}")
        sys.exit(1)

if __name__ == "__main__":
    download_gemma_gguf()