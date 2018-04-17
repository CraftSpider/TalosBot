
from typing import Dict, List, Any, Tuple

class TalosUser:

    __slots__ = ("id", "description", "total_commands", "cur_title", "invoked_data", "titles")

    id: int
    description: str
    total_commands: int
    cur_title: str
    invoked_data: List
    titles: List

    def __init__(self, data: Dict[str, List[Any]]):
        pass

    def get_favorite_command(self) -> Tuple[str, int]: ...
