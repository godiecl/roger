"""
Tests de integración para scripts/ingest_storage.py.

Estrategia: subprocess con env vars sobreescritas (DATABASE_URL, STORAGE_PATH)
para aislar completamente del .env y la BD real del proyecto.

Cubre:
  - descubrimiento con estructura cajón / lugar / archivos
  - --dry-run no escribe en la BD
  - ingesta real puebla colección + caja + roll + photograph + photograph_file
  - idempotencia: re-correr no duplica
  - extensiones no soportadas (.txt, .cr2) se ignoran
  - archivo suelto bajo el cajón → roll "sin clasificar"
  - carpeta de cajón sin número parseable → skip
"""
from __future__ import annotations

import os
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest

VALERIA_DIR = Path(__file__).resolve().parents[3]


def _make_file(p: Path, size_bytes: int = 64) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(b"\xff\xd8\xff\xe0" + os.urandom(size_bytes - 4))


@pytest.fixture
def storage_tree(tmp_path: Path) -> Path:
    """
    Crea una jerarquía representativa:
        storage/images/
          cajon_11/
            Tunja/             img_a.jpg   img_b.tif   notas.txt
            La_Paz/            img_c.cr3
            extra_suelto.cr2   (RAW no soportado → ignora)
          caja_22/
            img_at_root.jpg   (archivo suelto → roll "sin clasificar")
          box_99/
            sub/               IMG_001.png
          sin_numero/
            x/                 nope.jpg    (sin número de cajón → skip)
    """
    root = tmp_path / "storage" / "images"

    # cajón 11
    _make_file(root / "cajon_11" / "Tunja" / "img_a.jpg")
    _make_file(root / "cajon_11" / "Tunja" / "img_b.tif")
    (root / "cajon_11" / "Tunja" / "notas.txt").write_text("ignorame")
    _make_file(root / "cajon_11" / "La_Paz" / "img_c.cr3")
    _make_file(root / "cajon_11" / "extra_suelto.cr2")  # RAW no en enum

    # caja 22 — archivo directo bajo el cajón
    _make_file(root / "caja_22" / "img_at_root.jpg")

    # box 99 — formato alternativo
    _make_file(root / "box_99" / "sub" / "IMG_001.png")

    # sin número parseable
    _make_file(root / "sin_numero" / "x" / "nope.jpg")

    return root


@pytest.fixture
def script_env(tmp_path: Path, storage_tree: Path) -> dict[str, str]:
    db_path = tmp_path / "test.db"
    env = os.environ.copy()
    env["DATABASE_URL"] = f"sqlite+aiosqlite:///{db_path.as_posix()}"
    env["STORAGE_PATH"] = str(storage_tree)
    # Defaults seguros para que Settings cargue sin pedir secretos:
    env.setdefault("SECRET_KEY", "test-secret-for-ingest-storage")
    env.setdefault("LLM_PROVIDER", "groq")
    env.setdefault("GROQ_API_KEY", "test-key-not-used")
    env.setdefault("REDIS_ENABLED", "false")
    env["_TEST_DB_PATH"] = str(db_path)
    return env


def _run_script(env: dict[str, str], *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "scripts.ingest_storage", *args],
        cwd=str(VALERIA_DIR),
        env=env,
        capture_output=True,
        text=True,
        timeout=60,
    )


def _count(db_path: str, table: str, where: str = "") -> int:
    con = sqlite3.connect(db_path)
    try:
        sql = f"SELECT COUNT(*) FROM {table}"
        if where:
            sql += f" WHERE {where}"
        return con.execute(sql).fetchone()[0]
    finally:
        con.close()


def _rows(db_path: str, query: str) -> list[tuple]:
    con = sqlite3.connect(db_path)
    try:
        return con.execute(query).fetchall()
    finally:
        con.close()


# ── Tests ─────────────────────────────────────────────────────────────────────


def test_dry_run_no_escribe_en_bd(script_env):
    proc = _run_script(script_env, "--dry-run")
    assert proc.returncode == 0, f"stderr={proc.stderr}"
    assert "Dry-run: no se escribe nada" in proc.stdout
    # La BD ni siquiera debería existir todavía
    assert not Path(script_env["_TEST_DB_PATH"]).exists()


def test_dry_run_reporta_descubrimiento_correcto(script_env):
    proc = _run_script(script_env, "--dry-run")
    out = proc.stdout
    # Cajones detectados: 11, 22, 99 (sin_numero descartado)
    assert "Cajón 11:" in out
    assert "Cajón 22:" in out
    assert "Cajón 99:" in out
    assert "sin_numero" in out  # se reporta como skip
    assert "no se pudo parsear" in out


def test_ingesta_real_puebla_jerarquia(script_env):
    proc = _run_script(script_env)
    assert proc.returncode == 0, f"stderr={proc.stderr}"
    db = script_env["_TEST_DB_PATH"]

    assert _count(db, "collections") == 1
    assert _count(db, "boxes") == 3                  # 11, 22, 99
    # Rolls esperados:
    #   cajón 11: Tunja, La_Paz       (2)
    #   cajón 22: "sin clasificar"    (1)  ← archivo suelto en el cajón
    #   cajón 99: sub                 (1)
    assert _count(db, "rolls") == 4

    # Photographs: img_a, img_b (en Tunja), img_c (La_Paz),
    #              img_at_root (caja_22), IMG_001 (box_99) = 5
    # extra_suelto.cr2 y notas.txt y nope.jpg (sin_numero) ignorados.
    assert _count(db, "photographs") == 5
    assert _count(db, "photograph_files") == 5


def test_idempotencia_segunda_corrida_no_duplica(script_env):
    first = _run_script(script_env)
    assert first.returncode == 0
    db = script_env["_TEST_DB_PATH"]
    before = (
        _count(db, "boxes"),
        _count(db, "rolls"),
        _count(db, "photographs"),
        _count(db, "photograph_files"),
    )

    second = _run_script(script_env)
    assert second.returncode == 0
    after = (
        _count(db, "boxes"),
        _count(db, "rolls"),
        _count(db, "photographs"),
        _count(db, "photograph_files"),
    )
    assert before == after
    assert "boxes: +0" in second.stdout
    assert "rolls: +0" in second.stdout
    assert "photos: +0" in second.stdout
    assert "files: +0" in second.stdout


def test_file_types_mapeados_correctamente(script_env):
    _run_script(script_env)
    db = script_env["_TEST_DB_PATH"]
    rows = _rows(db, "SELECT file_type, is_master FROM photograph_files ORDER BY file_path")
    types = sorted(r[0] for r in rows)
    # JPG x2 (img_a, img_at_root), TIFF x1 (img_b), CR3 x1 (img_c), PNG x1 (IMG_001)
    assert types == ["cr3", "jpg", "jpg", "png", "tiff"]
    # is_master = True solo para CR3 y TIFF
    masters = [r for r in rows if r[1] == 1]
    masters_types = sorted(r[0] for r in masters)
    assert masters_types == ["cr3", "tiff"]


def test_roll_sin_clasificar_para_archivo_suelto(script_env):
    _run_script(script_env)
    db = script_env["_TEST_DB_PATH"]
    rows = _rows(
        db,
        """
        SELECT r.name
        FROM rolls r
        JOIN boxes b ON r.box_id = b.id
        WHERE b.box_number = 22
        """,
    )
    assert rows == [("sin clasificar",)]


def test_extensiones_no_soportadas_se_ignoran(script_env):
    _run_script(script_env)
    db = script_env["_TEST_DB_PATH"]
    paths = [r[0] for r in _rows(db, "SELECT file_path FROM photograph_files")]
    # .txt, .cr2 y nope.jpg (cajón sin número) no deben aparecer
    assert not any(p.endswith(".txt") for p in paths)
    assert not any(p.endswith(".cr2") for p in paths)
    assert not any("nope" in p for p in paths)


def test_identifier_es_filename_sin_extension(script_env):
    _run_script(script_env)
    db = script_env["_TEST_DB_PATH"]
    identifiers = sorted(r[0] for r in _rows(db, "SELECT identifier FROM photographs"))
    assert identifiers == ["IMG_001", "img_a", "img_at_root", "img_b", "img_c"]
