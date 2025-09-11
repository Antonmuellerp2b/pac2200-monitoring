# state.py
from config import ENDPOINTS

# Store last query time for each source (global, für alle Module!)
last_run: dict[str, float] = {source: 0.0 for source in ENDPOINTS}
