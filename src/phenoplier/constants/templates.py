from phenoplier.constants.metadata import APP_CODE_DIR, APP_TEST_DIR
from pathlib import Path
import tempfile

USER_SETTINGS = {
    "ROOT_DIR":         str(Path(tempfile.gettempdir(), "phenoplier").resolve()),
    "MANUSCRIPT_DIR":   str(Path(tempfile.gettempdir(), "manuscript").resolve()),
    "GTEX_V8_DIR":      "",
    # "N_JOBS":           None,
    # "N_JOBS_HIGH":      None,
    }