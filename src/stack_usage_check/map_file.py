import re

from dataclasses import dataclass
from pathlib import Path


@dataclass
class MapStackAllocVariables:
    """ Class that represents stack allocation data variables within a map file """
    name: str
    type: str = None
    stack_allocation: int = 0


@dataclass
class MapStackAllocList:
    file_path: Path
    list: list[MapStackAllocVariables]


class StackArrayMapParser:
    """Parse _STACK_Array map symbols in the supported column layout."""

    def get_stack_allocation_list(self, map_file: Path) -> list:
        stack_array_search_pattern = re.compile(r'0x.*_STACK_Array.*')
        result = MapStackAllocList(file_path=map_file, list=[])
        content = map_file.read_text()
        match = stack_array_search_pattern.findall(content)
        for m in match:
            data = MapStackAllocVariables
            entry = m.split()
            result.list.append(data(name=entry[4],
                                    type=entry[3],
                                    stack_allocation=int(entry[2])))
        return result
