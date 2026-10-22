#!/usr/bin/env python3
"""Create a synthetic PDF and check its imported table and figure."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re


# These cells are source truth, never derived from the converter output.
TABLE = [
    ["样本", "成对差分", "中位数", "离散度", "误差", "范围", "概率", "统计量", "自由度", "检验", "附加列"],
    ["次级头", "自定义名称", "甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "次级备注"],
    ["对一", "A|B", "-0.50", "+2.00", "0.00", "-1..+1", "12.5%", "2.00", "8", "pass", "KEEP-11"],
    ["合计", "B", "-0.50", "+2.00", "0.00", "-1..+1", "12.5%", "2.00", "8", "pass", "TOTAL-11"],
]
CAPTION = "Figure 1. Synthetic response over time. Error-free import retains axes, units, and both series."
FIGURE_LABELS = ["Time (s)", "Response (mg/L)", "Series A", "Series B"]


def normalize_cell(value: str) -> str:
    return " ".join(value.replace(r"\|", "|").split())


def markdown_tables(text: str) -> list[list[list[str]]]:
    """Read the flat pipe tables emitted for this fixture."""
    tables = []
    current = []
    for line in text.splitlines() + [""]:
        line = line.strip()
        if line.startswith("|") and line.endswith("|"):
            # shortcut: this fixture has no literal backslashes; extend if its cells change.
            cells = [normalize_cell(cell) for cell in re.split(r"(?<!\\)\|", line[1:-1])]
            if not all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells):
                current.append(cells)
        elif current:
            tables.append(current)
            current = []
    return tables


def table_errors(expected: list[list[str]], actual: list[list[list[str]]]) -> list[str]:
    errors = []
    if len(actual) != 1:
        errors.append(f"Expected 1 table, found {len(actual)}")
    if not actual:
        return errors
    rows = actual[0]
    if len(rows) != len(expected):
        errors.append(f"Expected {len(expected)} rows, found {len(rows)}")
    for index, (want, got) in enumerate(zip(expected, rows), 1):
        if len(got) != len(want):
            errors.append(f"Row {index}: expected {len(want)} columns, found {len(got)}")
        for column, (cell, value) in enumerate(zip(want, got), 1):
            if normalize_cell(cell) != value:
                errors.append(f"Cell {index},{column}: expected {cell!r}, found {value!r}")
    return errors


def pixels(path: Path) -> dict:
    import fitz

    pix = fitz.Pixmap(str(path))
    if pix.alpha:
        pix = fitz.Pixmap(pix, 0)
    if pix.colorspace.n != 3:
        pix = fitz.Pixmap(fitz.csRGB, pix)
    return {"width": pix.width, "height": pix.height,
            "rgb_sha256": hashlib.sha256(pix.samples).hexdigest()}


def make_fixture(output: Path) -> dict:
    import fitz

    names = ["paper.pdf", "figure.png", "expected.json"]
    if any((output / name).exists() for name in names):
        raise ValueError("Fixture files already exist. Use a fresh output directory.")
    output.mkdir(parents=True, exist_ok=True)
    figure_path = output / "figure.png"
    with fitz.open() as chart:
        page = chart.new_page(width=800, height=400)
        page.insert_text((40, 30), "Synthetic response", fontsize=20)
        page.draw_line((100, 310), (680, 310), color=(0, 0, 0))
        page.draw_line((100, 310), (100, 70), color=(0, 0, 0))
        for i, label in enumerate(["0", "1", "2", "3"]):
            x = 100 + i * 180
            page.insert_text((x - 3, 330), label, fontsize=12)
            page.draw_line((x, 310), (x, 315), color=(0, 0, 0))
        for i, label in enumerate(["0", "5", "10"]):
            y = 310 - i * 110
            page.insert_text((72, y + 4), label, fontsize=12)
        page.insert_text((330, 365), FIGURE_LABELS[0], fontsize=16)
        page.insert_text((35, 260), FIGURE_LABELS[1], fontsize=16, rotate=90)
        for values, color, label, x in [([2, 4, 7, 9], (0.1, 0.3, 0.7), FIGURE_LABELS[2], 440),
                                         ([1, 3, 3, 6], (0.8, 0.3, 0.1), FIGURE_LABELS[3], 580)]:
            points = [(100 + i * 180, 310 - value * 22) for i, value in enumerate(values)]
            page.draw_polyline(points, color=color, width=3)
            for point in points:
                page.draw_circle(point, 4, color=color, fill=color)
            page.draw_line((x, 45), (x + 22, 45), color=color, width=3)
            page.insert_text((x + 28, 49), label, fontsize=12)
        page.get_pixmap(alpha=False).save(figure_path)
    with fitz.open() as paper:
        page = paper.new_page(width=1200, height=640)
        page.insert_text((50, 45), "Synthetic paper: PDF data fidelity", fontsize=24)
        page.insert_text((50, 75), "Test data only. These values make no research claim.", fontsize=14)
        page.insert_text((50, 115), "Table 1. Custom paired measurements with a secondary header and total.", fontsize=14)
        x0, y0, width, height = 50, 150, 100, 50
        for row in range(len(TABLE) + 1):
            page.draw_line((x0, y0 + row * height), (x0 + 11 * width, y0 + row * height))
        for column in range(12):
            page.draw_line((x0 + column * width, y0), (x0 + column * width, y0 + len(TABLE) * height))
        for row, cells in enumerate(TABLE):
            for column, cell in enumerate(cells):
                font = "china-s" if re.search(r"[\u4e00-\u9fff]", cell) else "helv"
                assert fitz.get_text_length(cell, fontname=font, fontsize=18) <= width - 10, cell
                page.insert_text((x0 + column * width + 5, y0 + row * height + 29),
                                 cell, fontname=font, fontsize=18)
        page.insert_text((50, 390), "The extra column, repeated values, signs, and decimal places are intentional.", fontsize=14)
        page = paper.new_page(width=1200, height=640)
        page.insert_text((50, 45), "Synthetic figure", fontsize=24)
        page.insert_image(fitz.Rect(200, 90, 1000, 490), filename=str(figure_path))
        page.insert_text((50, 540), CAPTION, fontsize=12)
        paper.save(output / "paper.pdf")
    expected = {"table": TABLE, "figure_caption": CAPTION, "figure_labels": FIGURE_LABELS,
                "figure_pixels": pixels(figure_path), "paper_pages": 2,
                "scope": "Synthetic acceptance fixture. Not a general PDF losslessness guarantee."}
    (output / "expected.json").write_text(json.dumps(expected, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"status": "created", "files": [str(output / name) for name in names]}


def compare(expected_path: Path, markdown_path: Path) -> dict:
    expected = json.loads(expected_path.read_text(encoding="utf-8"))
    text = markdown_path.read_text(encoding="utf-8")
    tables = markdown_tables(text)
    errors = table_errors(expected["table"], tables)
    if normalize_cell(expected["figure_caption"]) not in normalize_cell(text):
        errors.append("Figure caption is missing or changed")
    image_records = []
    for name in re.findall(r"!\[[^\]]*\]\(([^)]+)\)", text):
        path = (markdown_path.parent / name).resolve()
        if not path.is_relative_to(markdown_path.parent.resolve()) or not path.is_file():
            errors.append(f"Image path is missing or outside the import directory: {name}")
            continue
        image_records.append({"path": name, **pixels(path)})
    if not any({key: row[key] for key in expected["figure_pixels"]} == expected["figure_pixels"]
               for row in image_records):
        errors.append("No extracted image matches the source figure pixels, including its labels and units")
    return {"status": "fail" if errors else "pass", "errors": errors,
            "expected": str(expected_path.resolve()), "markdown": str(markdown_path.resolve()),
            "tables": tables, "images": image_records}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    fixture = commands.add_parser("make-fixture")
    fixture.add_argument("output", type=Path)
    check = commands.add_parser("compare")
    check.add_argument("expected", type=Path)
    check.add_argument("markdown", type=Path)
    check.add_argument("--report", required=True, type=Path)
    args = parser.parse_args()
    try:
        report = make_fixture(args.output) if args.command == "make-fixture" else compare(args.expected, args.markdown)
    except (OSError, ValueError, ImportError) as exc:
        report = {"status": "fail", "errors": [str(exc)]}
    payload = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.command == "compare":
        args.report.write_text(payload, encoding="utf-8")
    print(payload, end="")
    return int(report["status"] == "fail")


if __name__ == "__main__":
    raise SystemExit(main())
