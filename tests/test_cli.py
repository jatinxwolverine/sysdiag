import pytest
from unittest.mock import patch
from sysdiag.inspector import get_diagnostics

def test_diagnostics_success():
    data = get_diagnostics()
    assert "python" in data
    assert "disk" in data
    assert "tools" in data

def test_missing_dependency():
    with patch("shutil.which", return_value=None):
        data = get_diagnostics()
        assert data["missing_tools"] is True
        assert data["tools"]["git"]["installed"] is False

def test_malformed_config():
    with pytest.raises(FileNotFoundError):
        get_diagnostics(config_path="non_existent_file.json")
        
    with pytest.raises(ValueError):
        # Create temporary dummy file with invalid extension
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".bad_ext") as tmp:
            get_diagnostics(config_path=tmp.name)