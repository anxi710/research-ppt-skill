"""Check the acceptance oracle without requiring the PDF backend."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


spec = importlib.util.spec_from_file_location("check_pdf_fidelity", Path(__file__).resolve().parents[1] / "scripts/check_pdf_fidelity.py")
fidelity = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fidelity)


def markdown(rows):
    lines = ["|" + "|".join(cell.replace("|", r"\|") for cell in row) + "|" for row in rows]
    lines.insert(1, "|" + "|".join(["---"] * len(rows[0])) + "|")
    return "\n".join(lines)


class PdfFidelityTests(unittest.TestCase):
    def errors(self, rows):
        return fidelity.table_errors(fidelity.TABLE, fidelity.markdown_tables(markdown(rows)))

    def test_exact_cells_and_pipe_escaping_pass(self):
        self.assertEqual(self.errors(fidelity.TABLE), [])
        self.assertEqual(fidelity.normalize_cell(" A\\|B  \n C "), "A|B C")

    def test_lost_or_reordered_rows_fail(self):
        for rows in [fidelity.TABLE[:2] + fidelity.TABLE[3:],
                     [fidelity.TABLE[0], fidelity.TABLE[2], fidelity.TABLE[1], fidelity.TABLE[3]]]:
            with self.subTest(rows=rows):
                self.assertTrue(self.errors(rows))

    def test_truncated_column_fails(self):
        self.assertTrue(self.errors([row[:-1] for row in fidelity.TABLE]))

    def test_sign_decimal_percent_and_duplicate_value_changes_fail(self):
        for column, value in [(2, "0.50"), (3, "+2.0"), (6, "12.5"), (7, "3.00")]:
            with self.subTest(column=column):
                rows = copy.deepcopy(fidelity.TABLE)
                rows[2][column] = value
                self.assertTrue(self.errors(rows))

    def test_missing_and_extra_tables_fail(self):
        self.assertTrue(fidelity.table_errors(fidelity.TABLE, []))
        tables = fidelity.markdown_tables(markdown(fidelity.TABLE) + "\n\n" + markdown(fidelity.TABLE))
        self.assertTrue(fidelity.table_errors(fidelity.TABLE, tables))

    def test_compare_checks_caption_and_local_figure_pixels(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            expected = root / "expected.json"
            source_pixels = {"width": 800, "height": 400, "rgb_sha256": "source"}
            expected.write_text(json.dumps({"table": fidelity.TABLE, "figure_caption": fidelity.CAPTION,
                                            "figure_pixels": source_pixels}), encoding="utf-8")
            (root / "figure.png").write_bytes(b"synthetic test placeholder")
            converted = root / "paper.md"
            valid = markdown(fidelity.TABLE) + "\n\n" + fidelity.CAPTION + "\n![Figure](figure.png)"
            for text, image, status in [
                (valid, source_pixels, "pass"),
                (valid.replace(fidelity.CAPTION, "Changed caption"), source_pixels, "fail"),
                (valid.replace("figure.png", "missing.png"), source_pixels, "fail"),
                (valid, dict(source_pixels, rgb_sha256="changed"), "fail"),
            ]:
                with self.subTest(text=text, image=image):
                    converted.write_text(text, encoding="utf-8")
                    with patch.object(fidelity, "pixels", return_value=image):
                        self.assertEqual(fidelity.compare(expected, converted)["status"], status)


if __name__ == "__main__":
    unittest.main()
