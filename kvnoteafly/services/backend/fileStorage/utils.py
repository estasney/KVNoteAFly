from __future__ import annotations

import asyncio
from _operator import itemgetter
from pathlib import Path
from typing import Mapping

CategoryFiles = Mapping[str, list[Path]]
CategoryNoteMeta = list["NoteMetaData"]


async def _fetch_fp_mtime(f: Path) -> tuple[Path, int]:
    return f, f.lstat().st_mtime_ns


async def _sort_fp_mtimes(files: list[Path], new_first: bool) -> list[Path]:
    """Fetch and sort file modified times

    Parameters
    ----------
    new_first
    """
    fetched = await asyncio.gather(*[_fetch_fp_mtime(f) for f in files])
    fetched = sorted(fetched, key=itemgetter(1), reverse=new_first)
    return [f for f, _ in fetched]


async def _load_category_meta(i: int, note_path: Path) -> tuple[int, str, Path]:
    with note_path.open(mode="r", encoding="utf-8") as fp:
        note_text = fp.read()
    return i, note_text, note_path


async def _load_category_metas(note_paths: list[Path], new_first: bool):
    note_paths_ordered = await _sort_fp_mtimes(note_paths, new_first)
    meta_texts = await asyncio.gather(
        *[_load_category_meta(i, f) for i, f in enumerate(note_paths_ordered)]
    )
    return meta_texts


async def _discover_folder_notes(folder: Path, new_first: bool):
    notes = [f for f in folder.iterdir() if f.is_file()]
    ordered_notes = await _sort_fp_mtimes(notes, new_first)
    return folder, ordered_notes


async def _get_folder_files(folder: Path, new_first):
    categories, folders = zip(*[(f.name, f) for f in folder.iterdir() if f.is_dir()])
    folder_notes = await asyncio.gather(
        *[_discover_folder_notes(f, new_first) for f in folders]
    )
    return {folder.name: items for folder, items in folder_notes}
