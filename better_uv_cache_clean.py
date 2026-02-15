# /// script
# requires-python = ">=3.8"
# dependencies = ["send2trash", "tqdm"]
# ///

"""
better_uv_cache_clean.py

uvキャッシュをクリーンアップするスクリプト
"""

import sys
import argparse
import subprocess
import shutil
# import time
from pathlib import Path
from typing import List, Dict, Tuple
from tqdm import tqdm
from send2trash import send2trash


def get_uv_cache_dir() -> Path:
    """
    uv cache dirコマンドを実行し、キャッシュディレクトリのパスを取得する
    
    Returns:
        Path: キャッシュディレクトリのパス
    
    Raises:
        SystemExit: uvがインストールされていない場合やキャッシュディレクトリが見つからない場合
    """
    try:
        result = subprocess.run(
            ["uv", "cache", "dir"],
            capture_output=True,
            text=True,
            check=True
        )
        cache_dir = result.stdout.strip()
        return Path(cache_dir)
    except subprocess.CalledProcessError as e:
        print("Error: Failed to get uv cache directory", file=sys.stderr)
        print(f"Command output: {e.stderr}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print("Error: uv is not installed or not found in PATH", file=sys.stderr)
        sys.exit(1)


def check_subfolder(subfolder: Path) -> Tuple[bool, int]:
    """
    サブフォルダ内のすべてのファイルのハードリンク数をチェックし、
    ディスク上のサイズを計算する
    
    すべてのファイルがリンク数1未満（リンク数1のみ）の場合はTrue、
    ひとつでもリンク数2以上のファイルがある場合はFalseを返す
    
    Args:
        subfolder: サブフォルダのパス
    
    Returns:
        Tuple[bool, int]: (すべてのファイルがリンク数1の場合はTrue、それ以外はFalse, ディスク上のサイズ)
    """
    total_size = 0
    for file_path in subfolder.rglob("*"):
        if file_path.is_file():
            stat_result = file_path.stat()
            link_count = stat_result.st_nlink
            if link_count >= 2:
                return False, total_size
            # ディスク上のサイズを加算
            total_size += stat_result.st_size
    return True, total_size


def get_display_name(subfolder: Path) -> str:
    """
    サブフォルダの表示名を取得する
    
    サブフォルダの中のサブフォルダ一覧を取得し、.dist-infoで終わるフォルダがあれば、
    .dist-infoを除去したフォルダ名を採用します。
    見つからなかったら最初のフォルダ名を採用します。
    フォルダが見つからなかったらサブフォルダ自体のフォルダ名を採用します。
    
    Args:
        subfolder: サブフォルダのパス
    
    Returns:
        str: 表示名
    """
    subdirs = [d for d in subfolder.iterdir() if d.is_dir()]
    
    if not subdirs:
        return subfolder.name
    
    # .dist-infoで終わるフォルダを探す
    for subdir in subdirs:
        if subdir.name.endswith(".dist-info"):
            return subdir.name[:-10]  # ".dist-info"を除去
    
    # 見つからなかったら最初のフォルダ名
    return subdirs[0].name


def format_size(size: int) -> str:
    """
    サイズを人間が読みやすい形式にフォーマットする
    
    Args:
        size: バイト単位のサイズ
    
    Returns:
        str: フォーマットされたサイズ文字列
    """
    size_float = float(size)
    for unit in ['B', 'KiB', 'MiB', 'GiB', 'TiB']:
        if size_float < 1024.0:
            return f"{size_float:.2f} {unit}"
        size_float /= 1024.0
    return f"{size_float:.2f} PiB"


def scan_archive_folder(archive_path: Path) -> List[Dict]:
    """
    archive-v0フォルダ内のサブフォルダをスキャンし、ハードリンク数をチェックする
    
    Args:
        archive_path: archive-v0フォルダのパス
    
    Returns:
        List[Dict]: サブフォルダ情報の辞書リスト
            - path: サブフォルダのパス
            - display_name: 表示名
            - is_deletable: 削除可能かどうか
            - size: ディスク上のサイズ（バイト）
    """
    results = []
    
    if not archive_path.exists():
        print(f"Warning: Archive folder not found: {archive_path}", file=sys.stderr)
        return results
    
    # サブフォルダのリストを取得
    subfolders = [d for d in archive_path.iterdir() if d.is_dir()]
    
    # tqdmで進捗表示
    for subfolder in tqdm(subfolders, desc="Scanning subfolders", unit="folder"):
        is_deletable, size = check_subfolder(subfolder)
        display_name = get_display_name(subfolder)
        results.append({
            "path": subfolder,
            "display_name": display_name,
            "is_deletable": is_deletable,
            "size": size
        })
    
    # display_nameでソート
    results.sort(key=lambda x: x["display_name"])
    
    return results


def delete_folders(folders: List[Dict], force_delete: bool = False) -> None:
    """
    フォルダを削除する
    
    Args:
        folders: 削除するフォルダ情報のリスト
        force_delete: Trueの場合はshutil.rmtreeを使用、Falseの場合はsend2trashを使用
    """
    for folder_info in tqdm(folders, desc="Deleting folders", unit="folder"):
        try:
            if force_delete:
                shutil.rmtree(folder_info["path"])
                print(f"\nDeleted: {folder_info['display_name']} ({format_size(folder_info['size'])})")
            else:
                send2trash(folder_info["path"])
                print(f"\nMoved to trash: {folder_info['display_name']} ({format_size(folder_info['size'])})")
        except Exception as e:
            print(f"Error deleting {folder_info['display_name']}: {e}", file=sys.stderr)


def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(
        description="Tool to clean up uv cache"
    )
    parser.add_argument(
        "--force-delete",
        action="store_true",
        help="Force delete mode (use shutil.rmtree instead of send2trash)"
    )
    
    args = parser.parse_args()
    
    # uvキャッシュディレクトリを取得
    cache_dir = get_uv_cache_dir()
    print(f"uv cache directory: {cache_dir}")
    
    # archive-v0フォルダを調査
    archive_path = cache_dir / "archive-v0"
    # start_time = time.time()
    results = scan_archive_folder(archive_path)
    # end_time = time.time()
    # elapsed_time = end_time - start_time
    # print(f"Elapsed time: {elapsed_time:.2f}secs\n")
    print(" ")
    
    # 削除可能なサブフォルダ（True）を一覧表示
    deletable_folders = [r for r in results if r["is_deletable"]]
    
    if deletable_folders:
        total_size = 0
        for folder_info in deletable_folders:
            size_str = format_size(folder_info["size"])
            print(f" [{folder_info['path'].name}] {folder_info['display_name']} - {size_str}")
            total_size += folder_info["size"]
        print(f"\nDeletable subfolders (all files have link count 1): [{len(deletable_folders)}/{len(results)}]")
        print(f"Total size of deletable subfolders: {format_size(total_size)}")
        
        # 削除確認
        if args.force_delete:
            print("\nWarning: Force delete mode enabled. Folders will be permanently deleted.")
        else:
            print("\nFolders will be moved to trash.")
        print("Do you want to proceed? (yes/no): ", end="")
        response = input().strip().lower()
        if response == "yes" or response == "y":
            delete_folders(deletable_folders, force_delete=args.force_delete)
            print(f"\nSuccessfully processed {len(deletable_folders)} folders.")
        else:
            print("\nDeletion cancelled.")
    else:
        print("\nNo deletable subfolders found.")



if __name__ == "__main__":
    main()
