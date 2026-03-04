#!/usr/bin/env python3
"""
Script to fix E402 import errors by adding # noqa: E402 comments
"""

import os


def fix_file(filepath):
    """Fix E402 imports in a file"""
    with open(filepath, 'r') as f:
        content = f.read()

    # Check if file has sys.path.insert
    if 'sys.path.insert' not in content:
        return False

    # Split lines
    lines = content.split('\n')

    # Find the line with sys.path.insert
    sys_path_line = -1
    for i, line in enumerate(lines):
        if 'sys.path.insert' in line:
            sys_path_line = i
            break

    if sys_path_line == -1:
        return False

    # Add # noqa: E402 to all imports after sys.path.insert
    changed = False
    for i in range(sys_path_line + 1, len(lines)):
        line = lines[i].strip()
        # Check if line is an import statement
        if line.startswith('from ') or line.startswith('import '):
            # Check if it already has a comment
            if '# noqa: E402' not in line:
                lines[i] = lines[i].rstrip() + '  # noqa: E402'
                changed = True

    if changed:
        with open(filepath, 'w') as f:
            f.write('\n'.join(lines))
        print(f"Fixed {filepath}")
        return True

    return False


def main():
    # Files to fix based on flake8 output
    files_to_fix = [
        'services/api/app/api/analytics.py',
        'services/api/app/api/media.py',
        'services/api/app/api/routes.py',
        'services/api/app/main.py',
        'services/bot/app/bot.py',
        'services/bot/app/main.py',
        'shared/alembic/env.py',
    ]

    fixed_count = 0
    for filepath in files_to_fix:
        if os.path.exists(filepath):
            if fix_file(filepath):
                fixed_count += 1

    print(f"\nFixed {fixed_count} files")

    # Run flake8 to check
    print("\nRunning flake8 check...")
    os.system('python3 -m flake8 --max-line-length=88 --extend-ignore=E203,W503')


if __name__ == '__main__':
    main()
