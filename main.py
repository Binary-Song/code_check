import os
import sys
import subprocess
import logging
from pathlib import Path
import argparse
from register_rules import register_rules
from code_check import Rule, Check, Line, RawDiff

def print_err(msg):
    print(msg, file=sys.stderr)

def get_file_attrs(path):
    cmd = ['git', 'check-attr', '-a', '-z', '--', path]
    result = subprocess.run(cmd,
                        cwd=repo_path,
                        stdout=subprocess.PIPE,
                        text=False,
                        check=True)
    # example output: "path/to/my/file\0key\0value\0"
    # where \0 is the NUL char.
    output = result.stdout
    attr = { }
    for index, word in enumerate(output.split(b'\x00')):
        if index % 3 == 0:
            continue
        elif index % 3 == 1:
            key = word.decode('utf-8')
        elif index % 3 == 2:
            value = word.decode('utf-8')
            attr[key] = value
    return attr

def get_file_type(path, diff: RawDiff):
    attr = get_file_attrs(path)
    
    # if it contains any lfs attr, then it is a lfs-file
    for lfs_attr in ['diff', 'filter', 'merge']:
        if lfs_attr in attr and attr[lfs_attr] == 'lfs':
            return 'lfs-file'
        
    # if the diff contains '@@ -1,69 +0,0 @@' line, then it is a text file
    for line in diff.lines:
        if line.text.startswith(b'@@'):
            return 'text'
    
    # otherwise, it is a binary file
    return 'binary'
    
def check_diff(repo_path : Path, rules: list[Rule], incremental=False):
    check_empty_repo = ['git', 'rev-parse', 'HEAD']
    result = subprocess.run(check_empty_repo,
                            cwd=repo_path,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.DEVNULL,
                            check=False)
    has_any_commit = result.returncode == 0
    empty_tree_hash = '4b825dc642cb6eb9a060e54bf8d69288fbee4904'
    diff_with = 'HEAD'
    if incremental or not has_any_commit:
        diff_with = empty_tree_hash
    cmd = ['git', 'diff', '--staged', diff_with]
    result = subprocess.run(cmd,
                            cwd=repo_path,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.DEVNULL,
                            text=False,
                            check=True)
    raw_git_diff = result.stdout
    diff_path = repo_path / "log" / "staged.diff"
    with open(diff_path, 'wb') as f:
        f.write(raw_git_diff)

    ok = True
    current_file = None
    file_to_diff: dict[str, RawDiff] = {}

    for i, line in enumerate(raw_git_diff.split(b'\n'), start=1):
        # line example: diff --git a/1.png b/1.png
        if line.startswith(b'diff --git'):
            # current_file example: a/src/test/extension.test.ts
            current_file = line.split()[-1].decode('utf-8')
            if current_file.startswith('a/') or current_file.startswith('b/'):
                # remove the 'a/' prefix
                current_file = current_file[2:]
        else:
            if current_file is None:
                continue
            if current_file not in file_to_diff:
                file_to_diff[current_file] = RawDiff([])
            
            file_to_diff[current_file].lines.append(Line(i, line))
    
    # apply the rules
    ok = True
    for file, diff in file_to_diff.items():
        file_type = get_file_type(file, diff)
        file_attrs = get_file_attrs(file)   
        for rule in rules:
            if not rule.applies_to(file_type):
                continue
            chk_attr_name = f'{rule.name()}'
            chk_attr_on =  chk_attr_name in file_attrs and file_attrs[chk_attr_name] == 'set'
            if not chk_attr_on:
                continue

            chk = Check(file, diff)
            if not rule.check(chk):
                ok = False
                for error in chk.errors:
                    if error.line_no != -1:
                        print_err(f"Error: '{rule.name()}' did not pass for {file}. See diff at {diff_path}:{error.line_no}. Message: {error.message}")
                    else:
                        print_err(f"Error: '{rule.name()}' did not pass for {file}. Message: {error.message}")
            else:
                print(f"'{rule.name()}' passed for {file}")
    return ok

def verify_rules(rules: list[Rule]):
    names = set()
    for rule in rules:
        if rule.name() in names:
            print("Found duplicate rule name: " + rule.name())
        else:
            names.add(rule.name())

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Check for issues in git diffs.")
    parser.add_argument('repo_path', type=str, help='Path to the repository to check.')
    parser.add_argument('--full', action='store_true', help='Run a full check instead of an incremental one.')
    args = parser.parse_args()

    repo_path = Path(args.repo_path)
    log_path = (repo_path / "log").resolve()
    os.makedirs("log", exist_ok=True)
    passed = True

    checks = register_rules()
    verify_rules(checks)
    if not check_diff(repo_path, checks, incremental=not args.full):
        passed = False
    
    if passed:
        print("All checks passed.")
        sys.exit(0)
    else:
        sys.exit(1)
