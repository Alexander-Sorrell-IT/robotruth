from __future__ import annotations
from dataclasses import dataclass, field
from unidiff import PatchSet
from unidiff.errors import UnidiffParseError


@dataclass
class AddedLine:
    file: str
    line: int | None
    content: str


@dataclass
class RemovedLine:
    file: str
    line: int | None
    content: str


@dataclass
class FileChange:
    path: str
    added: list[AddedLine] = field(default_factory=list)
    removed: list[RemovedLine] = field(default_factory=list)
    context: list[str] = field(default_factory=list)
    is_new: bool = False
    is_removed: bool = False


@dataclass
class Diff:
    files: list[FileChange]

    @property
    def paths(self) -> list[str]:
        return [f.path for f in self.files]


def parse_diff(diff_text: str) -> Diff:
    try:
        patch = PatchSet(diff_text)
    except UnidiffParseError as e:
        # Malformed diff text is bad input, not a server fault — surface it as a
        # ValueError so the API layer maps it to 400 instead of crashing 500.
        raise ValueError(f"Malformed diff: {e}") from e
    files: list[FileChange] = []
    for pf in patch:
        fc = FileChange(path=pf.path, is_new=pf.is_added_file, is_removed=pf.is_removed_file)
        for hunk in pf:
            for line in hunk:
                content = line.value.rstrip("\n")
                if line.is_added:
                    fc.added.append(AddedLine(pf.path, line.target_line_no, content))
                elif line.is_removed:
                    fc.removed.append(RemovedLine(pf.path, line.source_line_no, content))
                elif line.is_context:
                    fc.context.append(content)
        files.append(fc)
    return Diff(files=files)
