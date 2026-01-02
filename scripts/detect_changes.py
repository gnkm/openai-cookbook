#!/usr/bin/env python3
"""
差分検知スクリプト
upstream (openai/openai-cookbook) との差分を検知し、翻訳対象ファイルをリストアップする
"""

import argparse
import subprocess
import sys
from pathlib import Path

UPSTREAM_REMOTE = "upstream"
UPSTREAM_URL = "https://github.com/openai/openai-cookbook.git"
LAST_COMMIT_FILE = ".last_translated_commit"
TARGET_EXTENSIONS = (".md", ".ipynb")
TARGET_DIRECTORIES = ("articles/", "examples/")

_repo_root: Path | None = None


def get_repo_root() -> Path:
    """Git リポジトリのルートディレクトリを取得"""
    global _repo_root
    if _repo_root is None:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            raise RuntimeError("Git リポジトリのルートを取得できません")
        _repo_root = Path(result.stdout.strip())
    return _repo_root


def run_git(args: list[str], check: bool = True) -> subprocess.CompletedProcess:
    """Git コマンドを実行（リポジトリルートから）"""
    result = subprocess.run(
        ["git"] + args,
        capture_output=True,
        text=True,
        check=False,
        cwd=get_repo_root(),
    )
    if check and result.returncode != 0:
        raise RuntimeError(f"Git コマンド失敗: git {' '.join(args)}\n{result.stderr}")
    return result


def ensure_upstream_remote() -> None:
    """upstream リモートが存在することを確認"""
    result = run_git(["remote"], check=False)
    remotes = result.stdout.strip().split("\n")

    if UPSTREAM_REMOTE not in remotes:
        print(f"upstream リモートを追加: {UPSTREAM_URL}")
        run_git(["remote", "add", UPSTREAM_REMOTE, UPSTREAM_URL])


def fetch_upstream() -> None:
    """upstream から fetch"""
    print("upstream から fetch 中...")
    run_git(["fetch", UPSTREAM_REMOTE])


def get_upstream_head() -> str:
    """upstream/main の HEAD コミットハッシュを取得"""
    result = run_git(["rev-parse", f"{UPSTREAM_REMOTE}/main"])
    return result.stdout.strip()


def get_last_translated_commit(repo_root: Path) -> str | None:
    """最後に翻訳したコミットハッシュを取得"""
    commit_file = repo_root / LAST_COMMIT_FILE
    if commit_file.exists():
        return commit_file.read_text().strip()
    return None


def save_last_translated_commit(repo_root: Path, commit_hash: str) -> None:
    """翻訳したコミットハッシュを保存"""
    commit_file = repo_root / LAST_COMMIT_FILE
    commit_file.write_text(commit_hash + "\n")
    print(f"コミットハッシュを保存: {commit_hash}")


def is_target_file(filepath: str) -> bool:
    """ファイルが翻訳対象かどうかを判定"""
    if not any(filepath.endswith(ext) for ext in TARGET_EXTENSIONS):
        return False
    if not any(filepath.startswith(d) for d in TARGET_DIRECTORIES):
        return False
    return True


def get_changed_files(base_commit: str | None, head_commit: str) -> list[str]:
    """変更されたファイルのリストを取得"""
    if base_commit:
        result = run_git(
            ["diff", "--name-only", "--diff-filter=AM", base_commit, head_commit]
        )
    else:
        result = run_git(["ls-tree", "-r", "--name-only", head_commit])

    files = result.stdout.strip().split("\n")
    return [f for f in files if f and is_target_file(f)]


def get_deleted_files(base_commit: str, head_commit: str) -> list[str]:
    """削除されたファイルのリストを取得"""
    result = run_git(
        ["diff", "--name-only", "--diff-filter=D", base_commit, head_commit]
    )
    files = result.stdout.strip().split("\n")
    return [f for f in files if f and is_target_file(f)]


def main():
    parser = argparse.ArgumentParser(description="upstream との差分を検知")
    parser.add_argument(
        "--update-commit",
        action="store_true",
        help="翻訳完了後にコミットハッシュを更新",
    )
    parser.add_argument(
        "--all", action="store_true", help="全ファイルをリストアップ（初回翻訳用）"
    )
    parser.add_argument(
        "--output", type=Path, help="変更ファイルリストを出力するファイル"
    )
    args = parser.parse_args()

    try:
        repo_root = get_repo_root()
    except RuntimeError:
        print("エラー: Git リポジトリ内で実行してください", file=sys.stderr)
        sys.exit(1)

    ensure_upstream_remote()
    fetch_upstream()

    upstream_head = get_upstream_head()
    print(f"upstream/main: {upstream_head}")

    if args.all:
        last_commit = None
        print("全ファイルモード: 全ての対象ファイルをリストアップ")
    else:
        last_commit = get_last_translated_commit(repo_root)
        if last_commit:
            print(f"前回の翻訳コミット: {last_commit}")
        else:
            print("前回の翻訳コミットが見つかりません - 全ファイルを対象")

    changed_files = get_changed_files(last_commit, upstream_head)

    if last_commit:
        deleted_files = get_deleted_files(last_commit, upstream_head)
    else:
        deleted_files = []

    print(f"\n変更/新規ファイル: {len(changed_files)} 件")
    for f in changed_files:
        print(f"  + {f}")

    if deleted_files:
        print(f"\n削除されたファイル: {len(deleted_files)} 件")
        for f in deleted_files:
            print(f"  - {f}")

    if args.output:
        args.output.write_text("\n".join(changed_files))
        print(f"\nファイルリストを出力: {args.output}")

    if args.update_commit:
        save_last_translated_commit(repo_root, upstream_head)

    if not changed_files:
        print("\n変更ファイルはありません")
        sys.exit(0)


if __name__ == "__main__":
    main()
