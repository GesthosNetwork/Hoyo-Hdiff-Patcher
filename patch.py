import sys
import subprocess
import shutil
from pathlib import Path
import glob
import logging
import re
import json
import stat
import os

GAME_FOLDERS = [
    "GenshinImpact_Data",
    "StarRail_Data",
    "ZenlessZoneZero_Data",
    "Client"
]

TOOLS = ["7z.exe", "hpatchz.exe"]

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger("hdiff-patcher")

GAME_VERSION = None

def detect_game_folder() -> Path:
    for folder in GAME_FOLDERS:
        path = Path(folder)
        if path.is_dir():
            log.info(f"Detected game folder: {folder}")
            return path
    log.error(f"No supported game folder found. Expected one of: {', '.join(GAME_FOLDERS)}")
    sys.exit(1)

def normalize_version(v: str) -> str:
    parts = v.split(".")
    if len(parts) == 2:
        return f"{parts[0]}.{parts[1]}.0"
    return v

def detect_game_version_after_patch(game_folder: Path) -> str | None:
    settings_json = game_folder / "StreamingAssets" / "asb_settings.json"
    if settings_json.exists():
        try:
            data = json.loads(settings_json.read_text(encoding="utf-8"))
            variance = data.get("variance", "")
            match = re.search(r"(\d+\.\d+(?:\.\d+)?)", variance)
            if match:
                return normalize_version(match.group(1))
        except:
            pass
    bin_ver = game_folder / "StreamingAssets" / "BinaryVersion.bytes"
    if bin_ver.exists():
        try:
            data = bin_ver.read_text(errors="ignore")
            match = re.search(r"(\d+\.\d+(?:\.\d+)?)", data)
            if match:
                return normalize_version(match.group(1))
        except:
            pass
    version_info = game_folder / "version_info"
    if version_info.exists():
        try:
            data = version_info.read_text(errors="ignore")
            match = re.search(r"(\d+\.\d+(?:\.\d+)?)", data)
            if match:
                return normalize_version(match.group(1))
        except:
            pass
    log.warning("Game version could not be detected after patch.")
    return None

def check_tools():
    for tool in TOOLS:
        if not Path(tool).exists():
            log.error(f"{tool} is missing.")
            sys.exit(1)

def ensure_writable(path: Path):
    if not path.exists():
        return
    try:
        attrs = path.stat().st_mode
        if not (attrs & stat.S_IWRITE):
            path.chmod(attrs | stat.S_IWRITE)
    except:
        pass

def make_writable_recursive(path: Path):
    if not path.exists():
        return
    if path.is_file():
        try:
            path.chmod(stat.S_IWRITE | stat.S_IREAD)
        except:
            pass
        return
    for p in path.rglob("*"):
        try:
            p.chmod(stat.S_IWRITE | stat.S_IREAD)
        except:
            pass
    try:
        path.chmod(stat.S_IWRITE | stat.S_IREAD)
    except:
        pass

def replace_text_in_file(filepath: Path):
    if not filepath.exists():
        return
    text = filepath.read_text(encoding="utf-8")
    text = text.replace('{"remoteName": "', '').replace('"}', '').replace('/', '\\')
    filepath.write_text(text, encoding="utf-8", newline="\n")

def delete_files():
    delete_txt = Path("deletefiles.txt")
    if not delete_txt.exists():
        return
    replace_text_in_file(delete_txt)
    for line in delete_txt.read_text(encoding="utf-8").splitlines():
        target = Path(line.strip())
        if not target.exists():
            continue
        make_writable_recursive(target)
        try:
            if target.is_file():
                target.unlink()
                log.info(f"Deleted file: {target}")
            elif target.is_dir():
                shutil.rmtree(target, ignore_errors=True)
                log.info(f"Deleted directory tree: {target}")
        except Exception as e:
            log.warning(f"Failed to delete {target}: {e}")
    try:
        delete_txt.unlink()
    except:
        pass

def apply_hdiff() -> bool:
    hdifffiles_txt = Path("hdifffiles.txt")
    if not hdifffiles_txt.exists():
        return False
    replace_text_in_file(hdifffiles_txt)
    patched = False
    for line in hdifffiles_txt.read_text(encoding="utf-8").splitlines():
        target = line.strip()
        if not target:
            continue
        original_file = Path(target)
        hdiff = Path(f"{target}.hdiff")
        if not hdiff.exists():
            continue
        ensure_writable(original_file)
        try:
            subprocess.run([
                str(Path("hpatchz.exe").resolve()),
                "-f",
                str(Path(target).resolve()),
                str(hdiff.resolve()),
                str(Path(target).resolve())
            ], check=True)
            patched = True
        except subprocess.CalledProcessError as e:
            log.error(f"hpatchz failed for {target}: {e}")
            raise
        try:
            hdiff.unlink()
        except:
            pass
        log.info(f"Patched: {target}")
    try:
        hdifffiles_txt.unlink()
    except:
        pass
    return patched

def extract_with_7z(archive: Path):
    subprocess.run([str(Path("7z.exe").resolve()), "x", str(archive), "-o.", "-y"], check=True)

def is_multipart_first(p: Path) -> bool:
    name = p.name.lower()
    if re.search(r"\.(7z|zip|rar)\.0*1$", name):
        return True
    if name.endswith(".part1.rar"):
        return True
    return False

def get_multipart_first_parts() -> list[Path]:
    out = []
    for p in Path.cwd().iterdir():
        if not p.is_file():
            continue
        if is_multipart_first(p):
            out.append(p)
    return sorted(out, key=lambda p: p.name)

def collect_parts_for_first(first: Path) -> list[Path]:
    name = first.name
    lower = name.lower()
    parts = []
    m = re.search(r"^(.*\.(?:7z|zip|rar))\.0*1$", lower)
    if m:
        prefix = m.group(1)
        for candidate in Path.cwd().glob(prefix + ".*"):
            parts.append(candidate)
        return sorted(parts, key=lambda p: p.name)
    if lower.endswith(".part1.rar"):
        prefix = name[: -len(".part1.rar")]
        for candidate in Path.cwd().glob(prefix + ".part*.rar"):
            parts.append(candidate)
        return sorted(parts, key=lambda p: p.name)
    return [first]

def logical_name_from_first(first: Path) -> str:
    name = first.name
    lower = name.lower()
    m = re.search(r"^(.*\.(?:7z|zip|rar))\.0*1$", lower)
    if m:
        return m.group(1)
    if lower.endswith(".part1.rar"):
        return first.name
    return first.name

def extract_multipart_and_process(first: Path, game_folder: Path) -> bool:
    logical = logical_name_from_first(first)
    try:
        log.info(f"Processing multipart archive: {first.name}")
        extract_with_7z(first)
    except Exception as e:
        log.warning(f"Failed to extract multipart {first}: {e}")
    parts = collect_parts_for_first(first)
    for p in parts:
        try:
            p.unlink()
        except:
            pass
    return process_logical_archive(logical, game_folder)

def process_logical_archive(archive_name: str, game_folder: Path) -> bool:
    patched = False
    from_v, to_v = parse_from_to_versions_from_name(archive_name)
    needs_migration = False
    if from_v and to_v:
        try:
            fmaj, fmin = map(int, from_v.split(".")[:2])
            tmaj, tmin = map(int, to_v.split(".")[:2])
            if (fmaj, fmin) < (3, 6) and (tmaj, tmin) >= (3, 6):
                needs_migration = True
        except:
            needs_migration = False
    if needs_migration:
        migrated = migrate_audio_if_needed(game_folder, from_v, to_v)
        if not migrated:
            log.warning("Migration indicated but did not complete; continuing to apply hdiff may fail.")
    else:
        delete_files()
    if apply_hdiff():
        patched = True
    return patched

def extract_all_multipart_and_process(game_folder: Path) -> bool:
    patched_any = False
    multipart_firsts = get_multipart_first_parts()
    for first in multipart_firsts:
        try:
            if extract_multipart_and_process(first, game_folder):
                patched_any = True
        except Exception as e:
            log.warning(f"Error processing multipart {first}: {e}")
    return patched_any

def is_part_file_name(name: str) -> bool:
    ln = name.lower()
    if re.search(r"\.(7z|zip|rar)\.0*1$", ln):
        return True
    if ln.endswith(".part1.rar"):
        return True
    if re.search(r"\.(7z|zip|rar)\.0*\d+$", ln):
        return True
    if re.search(r"\.part\d+\.rar$", ln):
        return True
    return False

def extract_single_archive(archive: Path):
    try:
        log.info(f"Processing archive: {archive.name}")
        extract_with_7z(archive)
    except Exception as e:
        log.warning(f"Failed to extract {archive}: {e}")
    try:
        archive.unlink()
    except:
        pass

def parse_from_to_versions_from_name(name: str):
    m = re.search(r"_(\d+\.\d+(?:\.\d+)?)_(\d+\.\d+(?:\.\d+)?)", name)
    if m:
        return normalize_version(m.group(1)), normalize_version(m.group(2))
    return None, None

def migrate_audio_if_needed(game_folder: Path, version_from: str | None, version_to: str | None):
    try:
        if version_to is None:
            return False
        major, minor, _ = map(int, version_to.split("."))
    except:
        return False
    if (major, minor) < (3, 6):
        return False
    old = game_folder / "StreamingAssets" / "Audio" / "GeneratedSoundBanks" / "Windows"
    new = game_folder / "StreamingAssets" / "AudioAssets"
    if not old.exists():
        return False
    new.mkdir(parents=True, exist_ok=True)
    for p in old.rglob("*"):
        rel = p.relative_to(old)
        dest = new / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        try:
            if p.is_file():
                shutil.move(str(p), str(dest))
            else:
                dest.mkdir(parents=True, exist_ok=True)
        except Exception:
            try:
                shutil.copytree(str(p), str(dest), dirs_exist_ok=True)
            except:
                pass
    shutil.rmtree(old, ignore_errors=True)
    log.info("Audio migration completed.")
    return True

def cleanup_empty_dirs(game_folder: Path):
    while True:
        removed = False
        for path in sorted(game_folder.rglob("*"), reverse=True):
            if path.is_dir():
                try:
                    path.rmdir()
                    removed = True
                except:
                    pass
        if not removed:
            break

def write_config_ini():
    if GAME_VERSION is None:
        return
    content = [
        "[General]",
        "channel=1",
        "cps=hoyoverse",
        f"game_version={GAME_VERSION}",
        "sub_channel=0",
        ""
    ]
    Path("config.ini").write_text("\n".join(content), encoding="utf-8")

def cleanup_aux_files(game_folder: Path):
    patterns = [
        "*.py", "*.bat", "*.zip", "*.zip.*", "*.zip.001", "*.zip.002",
        "*.rar", "*.rar.*", "*.rar.001", "*.rar.002",
        "*.part1.rar", "*.part2.rar", "*.part*.rar",
        "*.7z", "*.7z.*", "*.7z.001", "*.7z.002",
        "hpatchz.exe", "hdiffz.exe", "7z.exe",
        "version.dll", "*.dmp", "*.bak", "*.txt", "*.log"
    ]
    for pat in patterns:
        for p in Path.cwd().rglob(pat):
            try:
                p.unlink()
            except:
                pass
    targets = [
        "SDKCaches", "webCaches", "kr_game_cache", "launcherDownload",
        ".quality", "quality", "CrashSightLog", "pipe_client",
        "TQM64", "wesight"
    ]
    for target in targets:
        for found in game_folder.rglob(target):
            if found.is_dir():
                try:
                    shutil.rmtree(found, ignore_errors=True)
                    log.info(f"Deleted directory tree (flex): {found}")
                except:
                    pass

def main():
    global GAME_VERSION
    game_folder = detect_game_folder()
    check_tools()
    patch_done = False
    pending_delete_for_migration = False
    if extract_all_multipart_and_process(game_folder):
        patch_done = True
    candidates = sorted(glob.glob("*.zip") + glob.glob("*.7z") + glob.glob("*.rar"))
    filtered = []
    for name in candidates:
        if is_part_file_name(name):
            continue
        filtered.append(name)
    for archive_name in filtered:
        archive_path = Path(archive_name)
        extract_single_archive(archive_path)
        if process_logical_archive(archive_name, game_folder):
            patch_done = True
    if patch_done:
        GAME_VERSION = detect_game_version_after_patch(game_folder)
        if pending_delete_for_migration:
            delete_files()
        if GAME_VERSION:
            write_config_ini()
        cleanup_aux_files(game_folder)
    cleanup_empty_dirs(game_folder)
    log.info("Patching finished.")

if __name__ == "__main__":
    main()
