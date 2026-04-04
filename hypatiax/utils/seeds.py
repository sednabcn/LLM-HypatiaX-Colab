"""Centralised seed management for all HypatiaX experiments.
 
Import this at the top of every experiment script instead of
repeating the seed-setting boilerplate.
"""
import random
import numpy as np
 
SEED: int = 42  # Must match value reported in paper
 
def set_all_seeds(seed: int = SEED) -> None:
    """Set seeds for random, numpy, and (optionally) torch."""
    random.seed(seed)
    np.random.seed(seed)
    try:
        import torch
        torch.manual_seed(seed)
        torch.use_deterministic_algorithms(True)
    except ImportError:
        pass
 
PYSR_KWARGS: dict = {'random_state': SEED, 'deterministic': True}

