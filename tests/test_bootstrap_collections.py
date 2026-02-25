from __future__ import annotations

import importlib.util
import pathlib
import types
import unittest
from unittest import mock


def load_module() -> types.ModuleType:
    script_path = (
        pathlib.Path(__file__).resolve().parents[1]
        / "scripts"
        / "firestore_migrations"
        / "bootstrap_collections.py"
    )
    spec = importlib.util.spec_from_file_location("bootstrap_collections", script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load bootstrap_collections module.")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[attr-defined]
    return module


class BootstrapCollectionsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.module = load_module()

    def test_parse_collections_defaults(self) -> None:
        self.assertEqual(
            tuple(self.module.parse_collections(None)),
            self.module.DEFAULT_COLLECTIONS,
        )

    def test_parse_collections_strips_empty_entries(self) -> None:
        parsed = tuple(self.module.parse_collections("pages, assets, ,revisions"))
        self.assertEqual(parsed, ("pages", "assets", "revisions"))

    def test_bootstrap_collection_success(self) -> None:
        with mock.patch.object(self.module, "request_json", return_value=(201, {})):
            self.module.bootstrap_collection("my-project", "pages", "token")

    def test_bootstrap_collection_raises_on_unexpected_status(self) -> None:
        with mock.patch.object(
            self.module,
            "request_json",
            return_value=(400, {"error": {"message": "bad request"}}),
        ):
            with self.assertRaises(RuntimeError) as exc:
                self.module.bootstrap_collection("my-project", "pages", "token")

        self.assertIn("Failed bootstrapping pages", str(exc.exception))

    def test_cleanup_collection_handles_not_found(self) -> None:
        with mock.patch.object(self.module, "request_json", return_value=(404, {})):
            self.module.cleanup_collection("my-project", "pages", "token")


if __name__ == "__main__":
    unittest.main()
