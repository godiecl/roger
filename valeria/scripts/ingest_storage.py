"""
Ingesta de archivos digitalizados desde el filesystem hacia la base.

Estructura esperada en STORAGE_PATH:
    <storage>/<cajon_X>/<lugar>/<archivo.ext>

Por cada archivo crea (si no existen ya):
  - CollectionModel  (singleton: "Robert Gerstmann")
  - BoxModel         (box_number parseado del primer nivel)
  - RollModel        (name = carpeta de lugar; "sin clasificar" si el archivo
                      cuelga directamente del cajón)
  - PhotographModel  (identifier = nombre del archivo sin extensión)
  - PhotographFileModel (file_path relativo a STORAGE_PATH, file_type por ext)

No completa metadata del Excel — solo registra por nombre. La etapa de match
con docs/photographic_inventory.xlsx vive en otro script.

Uso:
    cd valeria
    python -m scripts.ingest_storage              # ingesta real
    python -m scripts.ingest_storage --dry-run    # solo reporta qué haría
"""
from __future__ import annotations

import argparse
import asyncio
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select

from app.config.settings import settings
from app.infrastructure.database.session import AsyncSessionLocal, init_db
from app.features.view_images.infrastructure.persistence.image_model import CollectionModel
from app.features.archive.infrastructure.persistence.archive_model import (
    BoxModel, RollModel, PhotographModel, PhotographFileModel, FileType,
)

COLLECTION_NAME = "Robert Gerstmann"
COLLECTION_SLUG = "gerstmann"
UNCLASSIFIED_ROLL = "sin clasificar"

EXT_TO_FILETYPE = {
    ".cr3":  FileType.CR3,
    ".tif":  FileType.TIFF,
    ".tiff": FileType.TIFF,
    ".jpg":  FileType.JPG,
    ".jpeg": FileType.JPG,
    ".png":  FileType.PNG,
}
MASTER_EXTS = {".cr3", ".tif", ".tiff"}

BOX_RE = re.compile(r"(?:caj(?:a|on|ón)|box|c)[\s_-]*(\d+)", re.IGNORECASE)


def parse_box_number(folder_name: str) -> int | None:
    m = BOX_RE.search(folder_name)
    if m:
        return int(m.group(1))
    m = re.search(r"\d+", folder_name)
    return int(m.group(0)) if m else None


async def get_or_create_collection(session) -> CollectionModel:
    res = await session.execute(
        select(CollectionModel).where(CollectionModel.slug == COLLECTION_SLUG)
    )
    col = res.scalar_one_or_none()
    if col:
        return col
    col = CollectionModel(
        name=COLLECTION_NAME,
        slug=COLLECTION_SLUG,
        description="Colección creada por ingesta de filesystem.",
        photographer_name="Robert Gerstmann",
        origin_country="Chile",
        is_public=True,
    )
    session.add(col)
    await session.flush()
    return col


async def get_or_create_box(session, collection_id: int, box_number: int) -> BoxModel:
    res = await session.execute(
        select(BoxModel).where(
            BoxModel.collection_id == collection_id,
            BoxModel.box_number == box_number,
        )
    )
    box = res.scalar_one_or_none()
    if box:
        return box
    box = BoxModel(collection_id=collection_id, box_number=box_number, name=f"Cajón {box_number}")
    session.add(box)
    await session.flush()
    return box


async def get_or_create_roll(session, box_id: int, name: str) -> RollModel:
    res = await session.execute(
        select(RollModel).where(RollModel.box_id == box_id, RollModel.name == name)
    )
    roll = res.scalar_one_or_none()
    if roll:
        return roll
    roll = RollModel(box_id=box_id, name=name)
    session.add(roll)
    await session.flush()
    return roll


async def get_or_create_photograph(session, roll_id: int, identifier: str) -> tuple[PhotographModel, bool]:
    res = await session.execute(
        select(PhotographModel).where(
            PhotographModel.roll_id == roll_id,
            PhotographModel.identifier == identifier,
        )
    )
    photo = res.scalar_one_or_none()
    if photo:
        return photo, False
    photo = PhotographModel(roll_id=roll_id, identifier=identifier, is_public=True)
    session.add(photo)
    await session.flush()
    return photo, True


async def ensure_photograph_file(session, photograph_id: int, file_path: str, ext: str, size: int) -> bool:
    res = await session.execute(
        select(PhotographFileModel).where(PhotographFileModel.file_path == file_path)
    )
    if res.scalar_one_or_none():
        return False
    session.add(PhotographFileModel(
        photograph_id=photograph_id,
        file_type=EXT_TO_FILETYPE[ext],
        file_path=file_path,
        is_master=ext in MASTER_EXTS,
        file_size_bytes=size,
    ))
    return True


def discover_files(root: Path) -> list[tuple[int, str, Path]]:
    """Devuelve [(box_number, lugar, file_path_absoluto), ...]"""
    out: list[tuple[int, str, Path]] = []
    if not root.exists():
        return out
    for box_dir in sorted(p for p in root.iterdir() if p.is_dir()):
        box_num = parse_box_number(box_dir.name)
        if box_num is None:
            print(f"  [skip] no se pudo parsear número de cajón: {box_dir.name}")
            continue
        # Archivos directos bajo el cajón → roll "sin clasificar"
        for f in box_dir.iterdir():
            if f.is_file() and f.suffix.lower() in EXT_TO_FILETYPE:
                out.append((box_num, UNCLASSIFIED_ROLL, f))
        # Subcarpetas de lugar
        for place_dir in sorted(p for p in box_dir.iterdir() if p.is_dir()):
            for f in place_dir.rglob("*"):
                if f.is_file() and f.suffix.lower() in EXT_TO_FILETYPE:
                    out.append((box_num, place_dir.name, f))
    return out


async def main(dry_run: bool) -> None:
    root = Path(settings.storage_path).resolve()
    print(f"Storage root: {root}")
    print(f"Dry-run     : {dry_run}\n")

    files = discover_files(root)
    if not files:
        print("Nada que ingerir — storage vacío o no existe.")
        return

    by_box: dict[int, dict[str, list[Path]]] = {}
    for box_num, lugar, f in files:
        by_box.setdefault(box_num, {}).setdefault(lugar, []).append(f)

    print("Descubierto:")
    for box_num in sorted(by_box):
        total = sum(len(v) for v in by_box[box_num].values())
        print(f"  Cajón {box_num}: {total} archivos en {len(by_box[box_num])} carpeta(s)")
        for lugar, lst in by_box[box_num].items():
            print(f"    - {lugar}: {len(lst)}")
    print()

    if dry_run:
        print("Dry-run: no se escribe nada.")
        return

    await init_db()
    created = {"boxes": 0, "rolls": 0, "photos": 0, "files": 0}
    async with AsyncSessionLocal() as session:
        col = await get_or_create_collection(session)

        for box_num, lugares in by_box.items():
            box_pre_id = await session.execute(
                select(BoxModel.id).where(
                    BoxModel.collection_id == col.id, BoxModel.box_number == box_num
                )
            )
            existed = box_pre_id.scalar_one_or_none() is not None
            box = await get_or_create_box(session, col.id, box_num)
            if not existed:
                created["boxes"] += 1

            for lugar, file_list in lugares.items():
                roll_pre = await session.execute(
                    select(RollModel.id).where(
                        RollModel.box_id == box.id, RollModel.name == lugar
                    )
                )
                roll_existed = roll_pre.scalar_one_or_none() is not None
                roll = await get_or_create_roll(session, box.id, lugar)
                if not roll_existed:
                    created["rolls"] += 1

                for f in file_list:
                    rel = str(f.resolve().relative_to(root)).replace("\\", "/")
                    identifier = f.stem
                    ext = f.suffix.lower()
                    photo, was_new_photo = await get_or_create_photograph(
                        session, roll.id, identifier
                    )
                    if was_new_photo:
                        created["photos"] += 1
                    added = await ensure_photograph_file(
                        session, photo.id, rel, ext, f.stat().st_size
                    )
                    if added:
                        created["files"] += 1

        await session.commit()

    print("Ingesta completada:")
    for k, v in created.items():
        print(f"  {k}: +{v}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="No escribe en la base, solo reporta.")
    args = parser.parse_args()
    asyncio.run(main(args.dry_run))
