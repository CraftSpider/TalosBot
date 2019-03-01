
from typing import Dict, Any

class APIHandler:

    __slots__ = ()

    async def dispatch(self, path: str, data: Dict[str, Any]) -> None: ...
