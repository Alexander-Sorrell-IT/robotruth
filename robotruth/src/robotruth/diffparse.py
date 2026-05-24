from __future__ import annotations
from dataclasses import dataclass, field
from unidiff import PatchSet


@dataclass
class AddedLine:
    file: str
    line: int | None
    content: str


@dataclass
class RemovedLine:
    file: str
    content: str


@dataclass
class FileChange:
    path: str
    added: list[AddedLine] = field(default_factory=list)
    removed: list[RemovedLine] = field(default_factory=list)
    is_new: bool = False
    is_removed: bool = False


@dataclass
class Diff:
    files: list[FileChange]

    @property
    def paths(self) -> list[str]:
        return [f.path for f in self.files]


def parse_diff(diff_text: str) -> Diff:
    patch = PatchSet(diff_text)
    files: list[FileChange] = []
    for pf in patch:
        fc = FileChange(path=pf.path, is_new=pf.is_added_file, is_removed=pf.is_removed_file)
        for hunk in pf:
            for line in hunk:
                content = line.value.rstrip("\n")
                if line.is_added:
                    fc.added.append(AddedLine(pf.path, line.target_line_no, content))
                elif line.is_removed:
                    fc.removed.append(RemovedLine(pf.path, content))
        files.append(fc)
    return Diff(files=files)
