# better-uv-cache-clean

uvキャッシュをクリーンアップするツール

## 概要

このツールは、uvパッケージマネージャーのキャッシュディレクトリ内の未使用のパッケージを特定し、削除するためのスクリプトです。ハードリンク数をチェックすることで、現在どのプロジェクトからも使用されていないパッケージを安全に特定します。

## 機能

- uvキャッシュディレクトリの自動検出
- `archive-v0`フォルダ内のパッケージスキャン
- ハードリンク数に基づく未使用パッケージの特定
- ゴミ箱への移動（send2trash使用）または完全削除（shutil.rmtree使用）

## インストール

### 依存パッケージ

```bash
pip install tqdm send2trash
```

## 使用方法

### 基本的な使用方法

```bash
python better_uv_cache_clean.py
```

このコマンドを実行すると：
1. uvキャッシュディレクトリを検出
2. `archive-v0`フォルダ内のすべてのサブフォルダをスキャン
3. ハードリンク数が1のパッケージ（未使用）を特定
4. 削除可能なパッケージの一覧を表示
5. 削除の確認を求める（yes/no）

### オプション

#### `--force-delete`

デフォルトでは、パッケージはゴミ箱に移動されます。このオプションを使用すると、パッケージを完全に削除します。

```bash
python better_uv_cache_clean.py --force-delete
```

**注意**: `--force-delete`を使用すると、削除されたパッケージは復元できません。

## 動作原理

このツールは以下の手順で動作します：

1. **キャッシュディレクトリの検出**: `uv cache dir`コマンドを実行してキャッシュディレクトリのパスを取得
2. **スキャン**: `archive-v0`フォルダ内の各サブフォルダをスキャン
3. **ハードリンク数のチェック**: 各サブフォルダ内のすべてのファイルのハードリンク数を確認
   - すべてのファイルのハードリンク数が1の場合 → 削除可能
   - ひとつでもハードリンク数が2以上のファイルがある場合 → 削除不可（使用中）
4. **サイズ計算**: 各サブフォルダのディスク上のサイズを計算
5. **表示と削除**: 削除可能なパッケージを一覧表示し、確認後に削除

## 出力例

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

## 注意事項

- このツールは、ハードリンク数が1のパッケージのみを削除対象とします
- ハードリンク数が2以上のパッケージは、現在どこかで使用されているため削除されません
- デフォルトではゴミ箱に移動されるため、誤って削除した場合でも復元可能です
- `--force-delete`オプションを使用する場合は、慎重に使用してください

## ライセンス

MIT License
