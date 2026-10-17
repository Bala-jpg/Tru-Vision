import os
import sys

def download_include_dataset():
    """
    Downloads the AI4Bharat INCLUDE dataset (pre-extracted MediaPipe landmarks format)
    from Kaggle using the kaggle-api command line tool.
    """
    dataset_slug = "swaptr/isl-mediapipe-holistic-landmarks-generation"
    target_dir = os.path.dirname(os.path.abspath(__file__))
    dataset_dir = os.path.join(target_dir, "dataset")

    print(f"Target dataset directory: {dataset_dir}")
    os.makedirs(dataset_dir, exist_ok=True)

    # Check for kaggle package
    try:
        import kaggle
    except ImportError:
        print("Error: The 'kaggle' python package is not installed.")
        print("Please install it via: pip install kaggle")
        print("Also ensure your API token '~/.kaggle/kaggle.json' is configured.")
        sys.exit(1)

    print(f"Initiating download for Kaggle dataset: '{dataset_slug}'...")
    try:
        from kaggle.api.kaggle_api_extended import KaggleApi
        api = KaggleApi()
        api.authenticate()
        
        # Download and unzip directly
        api.dataset_download_files(dataset_slug, path=dataset_dir, unzip=True)
        print("INCLUDE dataset download and extraction complete!")
    except Exception as e:
        print(f"Failed to download dataset: {e}")
        print("Please verify your Kaggle API credentials.")
        print(f"Alternatively, download it manually from: https://www.kaggle.com/datasets/{dataset_slug}")

if __name__ == "__main__":
    download_include_dataset()
