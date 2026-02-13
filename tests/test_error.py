import pytest
from unittest.mock import patch
import os
import main

def test_run_fail_error():
    """ 異常系: 異常発生時の終了テスト """
    with patch.dict(os.environ, {"S3_PREFIX": "p"}, clear=True), \
         patch("main.setup_logging"):
        with pytest.raises(SystemExit) as e:
            main.run()

    assert e.value.code == 1
