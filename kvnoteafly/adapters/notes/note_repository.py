import abc
from abc import ABC
from pathlib import Path
from typing import Optional, TypedDict, TYPE_CHECKING

if TYPE_CHECKING:
    from domain.markdown_note import MarkdownNote
    from domain.editable import EditableNote


class NoteDiscovery(TypedDict):
    category: str
    image_path: Optional[Path]
    notes: list[Path]


class AbstractNoteRepository(ABC):
    @property
    @abc.abstractmethod
    def storage_path(self):
        raise NotImplementedError

    @storage_path.setter
    def storage_path(self, path):
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def categories(self) -> list[str]:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def current_category(self):
        raise NotImplementedError

    @current_category.setter
    @abc.abstractmethod
    def current_category(self, value):
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def category_meta(self):
        raise NotImplementedError

    @abc.abstractmethod
    def discover_notes(self) -> list[NoteDiscovery]:
        raise NotImplementedError

    @abc.abstractmethod
    def next_note(self):
        raise NotImplementedError

    @abc.abstractmethod
    def previous_note(self):
        raise NotImplementedError

    @abc.abstractmethod
    def current_note(self):
        raise NotImplementedError

    @abc.abstractmethod
    def get_note(self, category: str, idx: int) -> "MarkdownNote":
        raise NotImplementedError

    @abc.abstractmethod
    def save_note(self, note: "EditableNote") -> "MarkdownNote":
        raise NotImplementedError

    @abc.abstractmethod
    def set_index(self, n: Optional[int]):
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def index(self) -> "NoteIndex":
        raise NotImplementedError

    @abc.abstractmethod
    def index_size(self) -> int:
        raise NotImplementedError


class NoteIndex:
    """
    Handles indexing notes so that we can always call `next` or `previous`

    As with `range`, `end` is not inclusive
    """

    def __init__(self, size: int, current=0):
        self.size = size
        self.start = 0
        self.end = max([0, (size - 1)])
        self.current = current

    def set_current(self, n: int):
        if n >= self.size:
            raise IndexError(f"{n} is greater the {self.size}")
        self.current = n

    def next(self) -> int:
        if self.end == 0:
            return 0
        elif self.current == self.end:
            self.current = 0
            return self.current
        else:
            self.current += 1
            return self.current

    def previous(self) -> int:
        if self.end == 0:
            return 0
        elif self.current == 0:
            self.current = self.end
            return self.current
        else:
            self.current -= 1
            return self.current
