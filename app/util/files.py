import os


def exists(fn):
    cmd = f"stat {fn} >/dev/null 2>&1"  # Linux
    # cmd = f"stat {fn} >nul 2>&1"
    return os.system(cmd)
