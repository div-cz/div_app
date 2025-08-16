from pathlib import Path

def ensure_directories():
    directories = [
        Path('/div_app/data/div_management/logs'),
        Path('/div_app/data/div_management/books/images'),
        Path('/div_app/data/div_management/cache'),
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"✅ {directory}")
