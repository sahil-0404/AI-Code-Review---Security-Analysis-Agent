from pathlib import Path

import pytest
from fastapi import UploadFile

from backend.services.file_service import get_file_extension, language_from_extension


def test_language_from_extension_mapping():
    assert get_file_extension("sample.py") == ".py"
    assert language_from_extension(".py") == "python"
    assert language_from_extension(".java") == "java"


@pytest.mark.asyncio
async def test_save_upload_returns_path_and_code(tmp_path):
    from backend.services import file_service

    file_service.UPLOAD_DIR = tmp_path

    upload = UploadFile(filename="sample.py", file=pytest.importorskip("io").BytesIO(b"print('hi')"))
    saved_path, code = await file_service.save_upload(upload)

    assert saved_path.name.endswith(".py")
    assert saved_path.exists()
    assert code == "print('hi')"
