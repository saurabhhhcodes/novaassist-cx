from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

class BaseDataAdapter(ABC):
    """
    Abstract interface for data access. 
    Enterprises can implement this to connect Nova to their own DBs.
    """
    @abstractmethod
    def get_record(self, record_id: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def update_record(self, record_id: str, updates: Dict[str, Any]) -> bool:
        pass

    @abstractmethod
    def list_records(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        pass
