#!/usr/bin/env python3
"""
Version bumping script for turnpiece.com.
Usage: python bump_version.py <patch|minor|major>
"""

import re
import sys
import subprocess


def get_current_version():
    try:
        with open('version.py', 'r') as f:
            match = re.search(r'__version__ = "([^"]+)"', f.read())
            if match:
                return match.group(1)
    except FileNotFoundError:
        print("❌ version.py not found")
        sys.exit(1)
    print("❌ Could not parse version from version.py")
    sys.exit(1)


def bump_version(current, bump_type):
    parts = current.split('.')
    if len(parts) != 3:
        print("❌ Invalid version format. Expected: major.minor.patch")
        sys.exit(1)
    major, minor, patch = map(int, parts)
    if bump_type == 'patch':
        patch += 1
    elif bump_type == 'minor':
        minor += 1
        patch = 0
    elif bump_type == 'major':
        major += 1
        minor = 0
        patch = 0
    else:
        print("❌ Invalid bump type. Use: patch, minor, or major")
        sys.exit(1)
    return f"{major}.{minor}.{patch}"


def update_version_file(new_version):
    with open('version.py', 'r') as f:
        content = f.read()
    content = re.sub(r'__version__ = "[^"]+"', f'__version__ = "{new_version}"', content)
    version_tuple = tuple(map(int, new_version.split('.')))
    content = re.sub(r'__version_info__ = \([^)]+\)', f'__version_info__ = {version_tuple}', content)
    with open('version.py', 'w') as f:
        f.write(content)
    print(f"✅ Updated version.py to {new_version}")


def git_commit_and_tag(new_version):
    try:
        subprocess.run(['git', 'add', 'version.py'], check=True)
        # Commit message matches existing convention: just the version number
        subprocess.run(['git', 'commit', '-m', new_version], check=True)
        print(f"✅ Committed {new_version}")
        subprocess.run(['git', 'tag', f'v{new_version}'], check=True)
        print(f"✅ Created tag v{new_version}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Git error: {e}")
        sys.exit(1)


def main():
    if len(sys.argv) != 2:
        print("Usage: python bump_version.py <patch|minor|major>")
        print("  patch  1.1.1 -> 1.1.2")
        print("  minor  1.1.1 -> 1.2.0")
        print("  major  1.1.1 -> 2.0.0")
        sys.exit(1)

    bump_type = sys.argv[1]
    current = get_current_version()
    new_version = bump_version(current, bump_type)

    print(f"🔄 {current} -> {new_version}")
    update_version_file(new_version)

    print("\n📝 Git:")
    git_commit_and_tag(new_version)

    print(f"\n🎉 Done — v{new_version}")
    print(f"   git push && git push origin v{new_version}")


if __name__ == "__main__":
    main()
