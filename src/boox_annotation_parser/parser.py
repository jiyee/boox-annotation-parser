from enum import Enum
import dataclasses
import datetime
import re
from typing import List, Optional, TextIO, Tuple


class ParsingPhase(Enum):
    SECTION_NAME = 0
    TIME_AND_PAGE_NO = 1
    ORIGINAL_TEXT = 2
    ANNOTATIONS = 3
    END = 5


@dataclasses.dataclass
class Annotation:
    section_name: str
    time: datetime.datetime
    page_number: int
    original_text: str
    annotations: str


@dataclasses.dataclass
class AnnotationList:
    name: str
    author: str
    annotations: List[Annotation]


def parse_name_and_author(line: str) -> Tuple[str, str]:
    match = re.compile(r"^.*<<(.*)>>(.*)$").search(line)

    if not match:
        raise ValueError(f"Could not find book name and author in line: {line}")

    return match.group(1), match.group(2)


def parse_author(line: str) -> str:
    return line.strip()


def parse_section_name(line: str) -> str:
    match = re.compile(r".*(\d{4}-\d{2}-\d{2} \d{2}:\d{2})\s*\|\s*Page No\.:\s*(\d+).*").search(line)
    if match:
        return None

    return line.strip()

def parse_time_and_page_no(line: str) -> Tuple[datetime.datetime, int]:
    match = re.compile(r".*(\d{4}-\d{2}-\d{2} \d{2}:\d{2})\s*\|\s*Page No\.:\s*(\d+).*").search(line)
    if not match:
        raise ValueError(f"Could not parse time and page no: {line}")

    return datetime.datetime.strptime(match.group(1), "%Y-%m-%d %H:%M"), int(match.group(2))


def parse_possible_prefix_line(line: str) -> Tuple[Optional[str], str]:
    match = re.compile(r"^\u3010(.*)\u3011(.*)$").search(line)

    if not match:
        return (None, line.strip())

    return match.group(1), match.group(2).strip()


def is_annotation_end(line: str) -> bool:
    match = re.compile(r"^-+$").search(line)

    if not match:
        return False

    return True


def get_annotations(file: TextIO) -> AnnotationList:
    name = ""
    author = ""
    all_annotations: List[Annotation] = []

    section_name: Optional[str] = None
    time: Optional[datetime.datetime] = None
    page_number: Optional[int] = None
    original_text: List[str] = []
    annotations: List[str] = []

    parsing_phase = ParsingPhase.SECTION_NAME
    last_section_name = None

    for line_no, line in enumerate(file):
        prefix, line_data = parse_possible_prefix_line(line)
        if prefix == "Note":
            parsing_phase = ParsingPhase.ANNOTATIONS
        elif is_annotation_end(line):
            parsing_phase = ParsingPhase.END

        if line_no == 0:
            name, author = parse_name_and_author(line)
        elif parsing_phase == ParsingPhase.SECTION_NAME:
            section_name = parse_section_name(line)
            if section_name is None:
                section_name = last_section_name
                parsing_phase = ParsingPhase.TIME_AND_PAGE_NO
                time, page_number = parse_time_and_page_no(line)
                parsing_phase = ParsingPhase.ORIGINAL_TEXT
            else:
                last_section_name = section_name
                parsing_phase = ParsingPhase.TIME_AND_PAGE_NO
        elif parsing_phase == ParsingPhase.TIME_AND_PAGE_NO:
            time, page_number = parse_time_and_page_no(line)
            parsing_phase = ParsingPhase.ORIGINAL_TEXT
        elif parsing_phase == ParsingPhase.ORIGINAL_TEXT:
            original_text.append(line_data)
        elif parsing_phase == ParsingPhase.ANNOTATIONS:
            annotations.append(line_data)
        elif parsing_phase == ParsingPhase.END:
            if section_name is None:
                raise ValueError(
                    "Found no section_name in section ending " f"at line {line_no}."
                )
            elif time is None:
                raise ValueError(f"Found no time in section ending at line {line_no}.")
            elif page_number is None:
                raise ValueError(
                    "Found no page_number in section ending " f"at line {line_no}."
                )

            all_annotations.append(
                Annotation(
                    section_name=section_name,
                    time=time,
                    page_number=page_number,
                    original_text="\n".join(original_text),
                    annotations="\n".join(annotations),
                )
            )
            section_name = None
            time = None
            original_text = []
            annotations = []
            page_number = None
            parsing_phase = ParsingPhase.SECTION_NAME

    return AnnotationList(
        name=name,
        author=author,
        annotations=all_annotations,
    )
