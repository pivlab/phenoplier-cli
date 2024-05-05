from pathlib import Path
import tempfile

DEFAULT = {
    "ROOT_DIR":         str(Path(tempfile.gettempdir(), "phenoplier").resolve()),
    "MANUSCRIPT_DIR":   str(Path(tempfile.gettempdir(), "manuscript").resolve()),
    "GTEX_V8_DIR":      "",
    # "N_JOBS":           None,
    # "N_JOBS_HIGH":      None,
    }
