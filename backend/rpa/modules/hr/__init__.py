"""HR RPA modules"""

try:
    from .hr_login import HRLoginModule
except ImportError:
    HRLoginModule = None

try:
    from .candidate_search import CandidateSearchModule
except ImportError:
    CandidateSearchModule = None

try:
    from .batch_greet import BatchGreetModule
except ImportError:
    BatchGreetModule = None

__all__ = ["HRLoginModule", "CandidateSearchModule", "BatchGreetModule"]
