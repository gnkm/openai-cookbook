#!/usr/bin/env python3
"""
OpenAI Cookbook 翻訳スクリプト
OpenRouter API を使用して .md / .ipynb ファイルを日本語に翻訳する
"""

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Optional

import nbformat
from openai import OpenAI

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_MODEL = "anthropic/claude-sonnet-4"
MAX_RETRIES = 3
RETRY_DELAY = 5


def get_client() -> OpenAI:
    """OpenRouter クライアントを取得"""
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY 環境変数が設定されていません")
    return OpenAI(base_url=OPENROUTER_BASE_URL, api_key=api_key)


def translate_text(client: OpenAI, text: str, model: str = DEFAULT_MODEL) -> str:
    """テキストを日本語に翻訳"""
    if not text.strip():
        return text

    system_prompt = """あなたは技術文書の翻訳者です。以下のルールに従って英語を日本語に翻訳してください：

1. コードブロック（```で囲まれた部分）は翻訳せず、そのまま保持する
2. インラインコード（`で囲まれた部分）は翻訳せず、そのまま保持する
3. URL、ファイルパス、変数名、関数名は翻訳しない
4. 技術用語は適切な日本語訳を使用するが、一般的に英語のまま使われる用語（API、SDK、JSON等）はそのまま残す
5. Markdownの書式（見出し、リスト、リンク等）は保持する
6. 自然で読みやすい日本語にする"""

    for attempt in range(MAX_RETRIES):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"以下のテキストを日本語に翻訳してください：\n\n{text}"},
                ],
                temperature=0.3,
            )
            return response.choices[0].message.content
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                print(f"  リトライ中 ({attempt + 1}/{MAX_RETRIES}): {e}", file=sys.stderr)
                time.sleep(RETRY_DELAY * (attempt + 1))
            else:
                raise


def extract_front_matter(content: str) -> tuple[Optional[str], str]:
    """Markdownからfront matterを抽出"""
    if content.startswith("---"):
        match = re.match(r"^---\n(.*?)\n---\n(.*)$", content, re.DOTALL)
        if match:
            return match.group(1), match.group(2)
    return None, content


def translate_markdown_file(client: OpenAI, input_path: Path, output_path: Path, model: str = DEFAULT_MODEL) -> bool:
    """Markdownファイルを翻訳"""
    print(f"翻訳中: {input_path}")

    try:
        content = input_path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"  エラー: ファイル読み込み失敗 - {e}", file=sys.stderr)
        return False

    front_matter, body = extract_front_matter(content)

    try:
        translated_body = translate_text(client, body, model)
    except Exception as e:
        print(f"  エラー: 翻訳失敗 - {e}", file=sys.stderr)
        return False

    if front_matter:
        translated_content = f"---\n{front_matter}\n---\n{translated_body}"
    else:
        translated_content = translated_body

    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(translated_content, encoding="utf-8")
        print(f"  完了: {output_path}")
        return True
    except Exception as e:
        print(f"  エラー: ファイル書き込み失敗 - {e}", file=sys.stderr)
        return False


def translate_notebook_file(client: OpenAI, input_path: Path, output_path: Path, model: str = DEFAULT_MODEL) -> bool:
    """Jupyter Notebookファイルを翻訳（markdownセルのみ）"""
    print(f"翻訳中: {input_path}")

    try:
        nb = nbformat.read(input_path, as_version=4)
    except Exception as e:
        print(f"  エラー: ノートブック読み込み失敗 - {e}", file=sys.stderr)
        return False

    translated_count = 0
    for cell in nb.cells:
        if cell.cell_type == "markdown":
            source = cell.source
            if source.strip():
                try:
                    cell.source = translate_text(client, source, model)
                    translated_count += 1
                except Exception as e:
                    print(f"  警告: セル翻訳失敗 - {e}", file=sys.stderr)
                    continue

    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        nbformat.write(nb, output_path)
        print(f"  完了: {output_path} ({translated_count} セル翻訳)")
        return True
    except Exception as e:
        print(f"  エラー: ノートブック書き込み失敗 - {e}", file=sys.stderr)
        return False


def get_output_path(input_path: Path) -> Path:
    """出力ファイルパスを生成（_jaサフィックス付き）"""
    stem = input_path.stem
    suffix = input_path.suffix
    return input_path.parent / f"{stem}_ja{suffix}"


def translate_file(client: OpenAI, file_path: Path, model: str = DEFAULT_MODEL) -> bool:
    """ファイルを翻訳"""
    output_path = get_output_path(file_path)

    if file_path.suffix == ".md":
        return translate_markdown_file(client, file_path, output_path, model)
    elif file_path.suffix == ".ipynb":
        return translate_notebook_file(client, file_path, output_path, model)
    else:
        print(f"スキップ: サポートされていないファイル形式 - {file_path}", file=sys.stderr)
        return False


def translate_files(file_list: list[Path], model: str = DEFAULT_MODEL) -> tuple[int, int]:
    """複数ファイルを翻訳"""
    client = get_client()
    success_count = 0
    fail_count = 0

    for file_path in file_list:
        if translate_file(client, file_path, model):
            success_count += 1
        else:
            fail_count += 1
        time.sleep(1)

    return success_count, fail_count


def main():
    parser = argparse.ArgumentParser(description="OpenAI Cookbook 翻訳スクリプト")
    parser.add_argument("files", nargs="+", type=Path, help="翻訳するファイルのパス")
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"使用するモデル (デフォルト: {DEFAULT_MODEL})")
    args = parser.parse_args()

    valid_files = []
    for f in args.files:
        if not f.exists():
            print(f"警告: ファイルが見つかりません - {f}", file=sys.stderr)
            continue
        if f.suffix not in (".md", ".ipynb"):
            print(f"警告: サポートされていないファイル形式 - {f}", file=sys.stderr)
            continue
        valid_files.append(f)

    if not valid_files:
        print("翻訳対象のファイルがありません", file=sys.stderr)
        sys.exit(1)

    print(f"翻訳対象: {len(valid_files)} ファイル")
    success, fail = translate_files(valid_files, args.model)
    print(f"\n完了: 成功 {success}, 失敗 {fail}")

    if fail > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
