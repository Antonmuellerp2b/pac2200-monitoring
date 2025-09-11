# state.py
from config import ENDPOINTS

# Store last query time for each source (global, for all modules)
last_run: dict[str, float] = {source: 0.0 for source in ENDPOINTS}
