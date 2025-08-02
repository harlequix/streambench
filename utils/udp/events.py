from dataclasses import dataclass
from typing import Optional


@dataclass
class Event:
    id: int
    start_byte: int
    end_byte: int
    start: float
    payload: Optional[list]
    seqnr: Optional[int]
