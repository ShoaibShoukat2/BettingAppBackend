import pandas as pd
import portalocker
import os
from typing import List, Dict, Any
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

def safe_read_csv(filepath: str, default_columns: List[str] = None) -> pd.DataFrame:
    """
    Safely read CSV with file locking. Returns empty DataFrame if file doesn't exist.
    """
    full_path = DATA_DIR / filepath
    
    if not full_path.exists():
        if default_columns:
            return pd.DataFrame(columns=default_columns)
        return pd.DataFrame()
    
    try:
        with open(full_path, 'r') as f:
            portalocker.lock(f, portalocker.LOCK_SH)
            df = pd.read_csv(f)
            portalocker.unlock(f)
        return df
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        if default_columns:
            return pd.DataFrame(columns=default_columns)
        return pd.DataFrame()

def safe_write_csv(filepath: str, df: pd.DataFrame, mode: str = 'w'):
    """
    Safely write CSV with atomic operation and file locking.
    """
    full_path = DATA_DIR / filepath
    temp_path = full_path.with_suffix('.tmp')
    
    try:
        # Write to temporary file
        with open(temp_path, mode) as f:
            portalocker.lock(f, portalocker.LOCK_EX)
            df.to_csv(f, index=False, header=(mode == 'w'))
            portalocker.unlock(f)
        
        # Atomic rename
        if mode == 'w':
            temp_path.replace(full_path)
        else:
            # For append mode, concatenate
            if full_path.exists():
                existing = safe_read_csv(filepath)
                combined = pd.concat([existing, df], ignore_index=True)
                with open(full_path, 'w') as f:
                    portalocker.lock(f, portalocker.LOCK_EX)
                    combined.to_csv(f, index=False)
                    portalocker.unlock(f)
                temp_path.unlink(missing_ok=True)
            else:
                temp_path.replace(full_path)
        
        return True
    except Exception as e:
        print(f"Error writing {filepath}: {e}")
        temp_path.unlink(missing_ok=True)
        return False

def append_row(filepath: str, row: Dict[str, Any]):
    """
    Append a single row to CSV file.
    """
    df = pd.DataFrame([row])
    return safe_write_csv(filepath, df, mode='a')

def get_csv_path(filename: str) -> Path:
    """Get full path for a CSV file in data directory."""
    return DATA_DIR / filename