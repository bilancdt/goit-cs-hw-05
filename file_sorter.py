import os
import shutil
import asyncio
from pathlib import Path
from argparse import ArgumentParser
import logging

# Логування
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Асинхронна функція для копіювання
async def copy_file(file_path: Path, destination_dir: Path):
    try:
        extension = file_path.suffix[1:] 
        if not extension:
            extension = "unknown"  # Якщо розширення немає

        # Директорія для збереження
        target_folder = destination_dir / extension
        target_folder.mkdir(parents=True, exist_ok=True)

        # Копіювання
        target_file = target_folder / file_path.name
        shutil.copy2(file_path, target_file)
        logger.info(f"Copied: {file_path} -> {target_file}")
    except Exception as e:
        logger.error(f"Error copying {file_path}: {e}")

# Асинхронна функція для читання директорії та обробки файлів
async def read_folder(source_dir: Path, destination_dir: Path):
    tasks = []
    try:
        for root, _, files in os.walk(source_dir):
            for file_name in files:
                file_path = Path(root) / file_name
                tasks.append(copy_file(file_path, destination_dir))

        # Виконання задач асинхронно
        await asyncio.gather(*tasks)
    except Exception as e:
        logger.error(f"Error reading folder {source_dir}: {e}")

# Головна функція
async def main(source: str, destination: str):
    source_dir = Path(source)
    destination_dir = Path(destination)

    if not source_dir.is_dir():
        logger.error(f"Source directory does not exist: {source}")
        return

    destination_dir.mkdir(parents=True, exist_ok=True)
    await read_folder(source_dir, destination_dir)
    logger.info("Processing completed.")

if __name__ == "__main__":
    parser = ArgumentParser(description="Asynchronously sort and copy files by extensions.")
    parser.add_argument("source", help="Path to the source folder.")
    parser.add_argument("destination", help="Path to the destination folder.")
    args = parser.parse_args()

    asyncio.run(main(args.source, args.destination))
