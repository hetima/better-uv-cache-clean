# better-uv-cache-clean

A tool to clean up uv cache

## Overview

This tool is a script for identifying and removing unused packages in the uv package manager's cache directory. It safely identifies packages that are not currently being used by any project by checking hard link counts.

## Features

- Automatic detection of uv cache directory
- Scanning of packages in the `archive-v0` folder
- Identification of unused packages based on hard link counts
- Move to trash (using send2trash) or permanent deletion (using shutil.rmtree)

## Installation

### Dependencies

```bash
pip install tqdm send2trash
```

## Usage

### Basic Usage

```bash
python better_uv_cache_clean.py
```

or execute it by specifying the URL directly.

```bash
uv run https://raw.githubusercontent.com/hetima/better-uv-cache-clean/main/better_uv_cache_clean.py
```

Running this command will:
1. Detect the uv cache directory
2. Scan all subfolders in the `archive-v0` folder
3. Identify packages with hard link count of 1 (unused)
4. Display a list of deletable packages
5. Prompt for confirmation before deletion (yes/no)

### Options

#### `--force-delete`

By default, packages are moved to the trash. Use this option to permanently delete packages.

```bash
python better_uv_cache_clean.py --force-delete
```

**Caution**: Using `--force-delete` will permanently delete packages and they cannot be recovered.

## How It Works

This tool operates through the following steps:

1. **Cache Directory Detection**: Executes `uv cache dir` command to get the cache directory path
2. **Scanning**: Scans each subfolder in the `archive-v0` folder
3. **Hard Link Count Check**: Checks the hard link count of all files in each subfolder
   - If all files have a hard link count of 1 → Deletable
   - If any file has a hard link count of 2 or more → Not deletable (in use)
4. **Size Calculation**: Calculates the on-disk size of each subfolder
5. **Display and Deletion**: Displays a list of deletable packages and deletes them upon confirmation

## Example Output

```
uv cache directory: C:\Users\user\AppData\Local\uv\cache
Scanning subfolders: 100%|████████████████████| 320/320 [00:05<00:00, 60.0folder/s]

  package-a (C:\Users\user\AppData\Local\uv\cache\archive-v0\abc123) - 2.50 MiB
  package-b (C:\Users\user\AppData\Local\uv\cache\archive-v0\def456) - 1.20 MiB
  package-c (C:\Users\user\AppData\Local\uv\cache\archive-v0\ghi789) - 5.00 MiB

Deletable subfolders (all files have link count 1): [100/320]
Total size of deletable subfolders: 8.70 MiB

Folders will be moved to trash.
Do you want to proceed? (yes/no): yes
Deleting folders: 100%|████████████████████| 100/100 [00:02<00:00, 50.0folder/s]
Moved to trash: package-a (2.50 MiB)
Moved to trash: package-b (1.20 MiB)
Moved to trash: package-c (5.00 MiB)

Successfully processed 100 folders.
```

## Notes

- This tool only targets packages with a hard link count of 1
- Packages with a hard link count of 2 or more are currently in use somewhere and will not be deleted
- By default, packages are moved to the trash, so they can be recovered if accidentally deleted
- Use the `--force-delete` option with caution

## License

MIT License
