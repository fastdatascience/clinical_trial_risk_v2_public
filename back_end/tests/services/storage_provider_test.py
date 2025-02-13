import pytest

from app.services.storage_provider import LocalStorage


@pytest.fixture
def storage(tmp_path, monkeypatch):
    """Provides isolated LocalStorage instance with temp directory"""
    # monkeypatch.setattr(config, "BUCKET_OR_CONTAINER_NAME", str(tmp_path))
    return LocalStorage()


def test_put_and_get_file(storage):
    # ** Test basic write/read
    storage.put_file("test.txt", b"Hello World")
    assert storage.get_file("test.txt") == b"Hello World"

    # ** Test binary data
    binary_data = bytes(range(256))
    storage.put_file("bytes.bin", binary_data)
    assert storage.get_file("bytes.bin") == binary_data


def test_file_operations(storage):
    # *Test existence check
    assert storage.file_exists("missing.txt") is False
    storage.put_file("test.txt", b"Content")
    assert storage.file_exists("test.txt") is True

    # *Test deletion
    storage.delete_file("test.txt")
    assert storage.file_exists("test.txt") is False


def test_directory_creation(storage):
    # *Verify automatic directory creation
    storage.put_file("nested/path/file.txt", b"Deep")
    assert (storage.base_path / "nested/path/file.txt").exists()


def test_batch_deletion(storage):
    files = ["file1.txt", "file2.txt", "file3.txt"]
    for f in files:
        storage.put_file(f, b"data")

    storage.delete_files(files)
    for f in files:
        assert not storage.file_exists(f)


def test_special_characters(storage):
    # *Test non-ASCII and special chars
    weird_name = "méil €@%!()"
    storage.put_file(weird_name, b"special")
    assert storage.file_exists(weird_name)
    assert storage.get_file(weird_name) == b"special"


def test_empty_file_handling(storage):
    # *Test zero-byte files
    storage.put_file("empty.txt", b"")
    assert storage.get_file("empty.txt") == b""


def test_error_handling(storage):
    # *Test missing file access
    with pytest.raises(FileNotFoundError):
        storage.get_file("non_existent.file")

    # *Test deleting non-existent file (shouldn't crash)
    storage.delete_file("ghost.file")
