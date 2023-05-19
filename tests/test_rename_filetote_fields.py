"""Tests renaming Filetote custom fields for the beets-filetote plugin."""

import logging

from beets import config

from tests.helper import FiletoteTestCase

log = logging.getLogger("beets")


class FiletoteRenameFiletoteFieldsTest(FiletoteTestCase):
    """
    Tests to check that Filetote renames using Filetote-provided fields as
    expected for custom path formats.
    """

    def setUp(self, audible_plugin: bool = False) -> None:
        """Provides shared setup for tests."""
        super().setUp()

        self._create_flat_import_dir()
        self._setup_import_session(autotag=False)

    def test_rename_field_albumpath(self) -> None:
        """Tests that the value of `albumpath` populates in renaming."""
        config["filetote"]["extensions"] = ".file"
        config["paths"]["ext:file"] = "$albumpath/newname"

        self._run_importer()

        self.assert_in_lib_dir(b"Tag Artist", b"Tag Album", b"newname.file")

    def test_rename_field_old_filename(self) -> None:
        """Tests that the value of `old_filename` populates in renaming."""
        config["filetote"]["extensions"] = ".file"
        config["paths"]["ext:file"] = "$albumpath/$old_filename"

        self._run_importer()

        self.assert_in_lib_dir(b"Tag Artist", b"Tag Album", b"artifact.file")
        self.assert_in_lib_dir(b"Tag Artist", b"Tag Album", b"artifact2.file")

    def test_rename_field_medianame_old(self) -> None:
        """Tests that the value of `medianame_old` populates in renaming."""
        config["filetote"]["extensions"] = ".file"
        config["paths"]["ext:file"] = "$albumpath/$medianame_old"

        self._run_importer()

        self.assert_in_lib_dir(b"Tag Artist", b"Tag Album", b"track_1.file")

    def test_rename_field_medianame_new(self) -> None:
        """Tests that the value of `medianame_new` populates in renaming."""
        config["filetote"]["extensions"] = ".lrc"
        config["filetote"]["pairing"] = {
            "enabled": True,
            "pairing_only": True,
        }
        config["paths"]["ext:lrc"] = "$albumpath/$medianame_new"

        self._run_importer()

        self.assert_in_lib_dir(b"Tag Artist", b"Tag Album", b"Tag Title 1.lrc")
        self.assert_in_lib_dir(b"Tag Artist", b"Tag Album", b"Tag Title 2.lrc")
        self.assert_in_lib_dir(b"Tag Artist", b"Tag Album", b"Tag Title 3.lrc")
