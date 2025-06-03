#!/usr/bin/env python3
"""
Commit message helper for generating properly formatted commit messages
"""

import textwrap
import re


def format_commit_message(title_en: str, title_cn: str,
                         changes_en: list, changes_cn: list) -> str:
    """
    Format commit message with proper structure:
    - Title line (50 chars max)
    - Empty line
    - Body with bullet points (72 chars max per line)
    - Chinese translation
    """

    # Ensure title is not too long
    if len(title_en) > 50:
        print(f"Warning: Title too long ({len(title_en)} chars): {title_en}")

    lines = []

    # Title
    lines.append(title_en)
    lines.append("")  # Empty line

    # English changes
    for change in changes_en:
        # Wrap long lines to 72 characters, with proper indentation
        wrapped = textwrap.fill(f"- {change}",
                               width=72,
                               subsequent_indent="  ")
        lines.append(wrapped)

    # Add empty line before Chinese section
    lines.append("")

    # Chinese title and changes
    lines.append(title_cn)
    lines.append("")

    for change in changes_cn:
        # Wrap Chinese text to 72 characters
        wrapped = textwrap.fill(f"- {change}",
                               width=72,
                               subsequent_indent="  ")
        lines.append(wrapped)

    return "\n".join(lines)


def create_commit_with_message(message: str):
    """Create a git commit with the formatted message"""
    import subprocess
    import tempfile
    import os

    # Write message to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(message)
        temp_file = f.name

    try:
        # Use git commit with the message file
        result = subprocess.run(['git', 'commit', '-F', temp_file],
                              capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    finally:
        # Clean up temp file
        os.unlink(temp_file)


if __name__ == "__main__":
    # Example usage
    title_en = "fix: Improve commit message formatting"
    title_cn = "修复：改进commit信息格式"

    changes_en = [
        "Add commit helper script for proper message formatting",
        "Ensure title line stays under 50 characters",
        "Wrap body lines to 72 characters maximum",
        "Separate English and Chinese sections with empty lines",
        "Follow conventional commit format with type prefixes"
    ]

    changes_cn = [
        "添加commit辅助脚本以确保正确的信息格式",
        "确保标题行保持在50字符以内",
        "将正文行包装到最多72字符",
        "用空行分隔英文和中文部分",
        "遵循带有类型前缀的常规commit格式"
    ]

    message = format_commit_message(title_en, title_cn, changes_en, changes_cn)
    print("Generated commit message:")
    print("=" * 50)
    print(message)
    print("=" * 50)
