import pytest
from config.log_constants import LOG_PREFIX
from logger import Logger, default_log_path


@pytest.fixture(autouse=True)
def reset_logger():
    yield
    Logger.close()


@pytest.fixture
def log_file(tmp_path):
    path = tmp_path / "test.txt"
    yield path
    Logger.close()
    if path.exists():
        path.unlink()


class TestLoggerEnable:
    def test_disabled_by_default(self):
        assert not Logger._enabled

    def test_enable_sets_enabled(self):
        Logger.enable()
        assert Logger._enabled

    def test_enable_stdout_sets_no_file(self):
        Logger.enable()
        assert Logger._file is None

    def test_enable_file_opens_file(self, log_file):
        Logger.enable(file_path=log_file)
        assert Logger._file is not None


class TestLoggerLog:
    def test_log_does_nothing_when_disabled(self, capsys):
        Logger.log("should not appear")
        assert capsys.readouterr().out == ""

    def test_log_prints_to_stdout(self, capsys):
        Logger.enable()
        Logger.log("hello world")
        assert "hello world" in capsys.readouterr().out

    def test_log_writes_to_file(self, log_file):
        Logger.enable(file_path=log_file)
        Logger.log("file content")
        Logger.close()
        assert "file content" in log_file.read_text(encoding="utf-8")

    def test_log_empty_message(self, capsys):
        Logger.enable()
        Logger.log()
        assert "\n" in capsys.readouterr().out

    def test_log_multiple_lines(self, capsys):
        Logger.enable()
        Logger.log("line 1")
        Logger.log("line 2")
        out = capsys.readouterr().out
        assert "line 1" in out
        assert "line 2" in out


class TestLoggerFileFirstLine:
    def test_first_line_is_filename(self, tmp_path):
        path = tmp_path / "my-log.txt"
        Logger.enable(file_path=path)
        Logger.close()
        assert path.read_text(encoding="utf-8").splitlines()[0] == "my-log.txt"
        path.unlink()

    def test_log_content_follows_filename(self, log_file):
        Logger.enable(file_path=log_file)
        Logger.log("after filename")
        Logger.close()
        lines = log_file.read_text(encoding="utf-8").splitlines()
        assert lines[0] == "test.txt"
        assert any("after filename" in line for line in lines[1:])


class TestLoggerClose:
    def test_close_disables(self):
        Logger.enable()
        Logger.close()
        assert not Logger._enabled

    def test_close_clears_file_reference(self, log_file):
        Logger.enable(file_path=log_file)
        Logger.close()
        assert Logger._file is None

    def test_close_twice_is_safe(self):
        Logger.enable()
        Logger.close()
        Logger.close()
        assert not Logger._enabled

    def test_after_close_log_does_nothing(self, capsys):
        Logger.enable()
        Logger.close()
        Logger.log("should not appear")
        assert capsys.readouterr().out == ""


class TestDefaultLogPath:
    def test_returns_txt_file(self, tmp_path, monkeypatch):
        import logger as lg
        monkeypatch.setattr(lg, "LOGS_DIR", tmp_path / "logs")
        path = default_log_path()
        assert path.suffix == ".txt"

    def test_filename_contains_prefix(self, tmp_path, monkeypatch):
        import logger as lg
        monkeypatch.setattr(lg, "LOGS_DIR", tmp_path / "logs")
        assert LOG_PREFIX in default_log_path().name

    def test_creates_logs_directory(self, tmp_path, monkeypatch):
        import logger as lg
        logs_dir = tmp_path / "logs"
        monkeypatch.setattr(lg, "LOGS_DIR", logs_dir)
        default_log_path()
        assert logs_dir.exists()

    def test_id_starts_at_0001(self, tmp_path, monkeypatch):
        import logger as lg
        monkeypatch.setattr(lg, "LOGS_DIR", tmp_path / "logs")
        assert "0001" in default_log_path().name

    def test_id_increments_with_existing_files(self, tmp_path, monkeypatch):
        import logger as lg
        logs_dir = tmp_path / "logs"
        logs_dir.mkdir()
        monkeypatch.setattr(lg, "LOGS_DIR", logs_dir)
        first = default_log_path()
        first.touch()
        second = default_log_path()
        assert "0001" in first.name
        assert "0002" in second.name
        first.unlink()
