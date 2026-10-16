"""Focused archive verifier checks; no production source access."""
import gzip
import hashlib
import io
import os
from pathlib import Path
import tarfile
import tempfile
import types
import unittest

HERE = Path(__file__).resolve().parent
m = types.ModuleType('prepare_support')
m.__file__ = str(HERE / 'prepare.py')
exec(compile((HERE / 'prepare.py').read_bytes(), m.__file__, 'exec'), m.__dict__)


class SupportArchiveTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.stage = self.base / 'stage'
        self.stage.mkdir()
        (self.stage / 'failed-attempt').mkdir(mode=0o750)
        (self.stage / 'failed-attempt/error.log').write_bytes(b'preserved failure\n')
        (self.stage / 'failed-attempt/error.log').chmod(0o640)
        (self.stage / '.ignored').write_bytes(b'also retained')
        (self.stage / 'external-link').symlink_to('/outside/not-a-real-target')
        os.chmod(self.stage / 'external-link', 0o755, follow_symlinks=False)
        self.rows = [{**x, 'path': x['path'][6:]} for x in m.inventory(self.stage, 'stage')
                     if x['path'] != 'stage']
        self.archive = self.base / 'support.tar.gz'

    def write_modified(self, change=None, extra=None, omit=None):
        with gzip.open(self.archive, 'wb') as zipped, tarfile.open(fileobj=zipped, mode='w|') as tar:
            for row in self.rows:
                if row['path'] == omit:
                    continue
                ti = tarfile.TarInfo(row['path'])
                ti.mode = row['mode']
                data = None
                if row['kind'] == 'directory':
                    ti.type = tarfile.DIRTYPE
                elif row['kind'] == 'symlink':
                    ti.type = tarfile.SYMTYPE
                    ti.linkname = row['link_target']
                else:
                    data = (self.stage / row['path']).read_bytes()
                    ti.size = len(data)
                if change:
                    ti, data = change(ti, data)
                tar.addfile(ti, io.BytesIO(data) if data is not None else None)
            if extra:
                tar.addfile(extra)

    def test_roundtrip_preserves_failure_hidden_file_modes_literal_external_link(self):
        m.write_archive(self.archive, self.stage, self.rows)
        self.assertTrue(m.verify_archive(self.archive, self.rows)['verified'])
        self.assertFalse((self.base / 'outside').exists())

    def test_bytes_tamper_rejected(self):
        def change(ti, data):
            return ti, b'X' * len(data) if data else data
        self.write_modified(change)
        with self.assertRaisesRegex(ValueError, 'Byte mismatch'):
            m.verify_archive(self.archive, self.rows)

    def test_symlink_mode_rejected(self):
        def change(ti, data):
            if ti.issym(): ti.mode = 0o777
            return ti, data
        self.write_modified(change)
        with self.assertRaisesRegex(ValueError, 'Mode mismatch'):
            m.verify_archive(self.archive, self.rows)

    def test_symlink_target_rejected(self):
        def change(ti, data):
            if ti.issym(): ti.linkname = '/different'
            return ti, data
        self.write_modified(change)
        with self.assertRaisesRegex(ValueError, 'Literal link mismatch'):
            m.verify_archive(self.archive, self.rows)

    def test_missing_rejected(self):
        self.write_modified(omit='.ignored')
        with self.assertRaisesRegex(ValueError, 'Missing archive member'):
            m.verify_archive(self.archive, self.rows)

    def test_duplicate_rejected(self):
        extra = tarfile.TarInfo('external-link')
        self.write_modified(extra=extra)
        with self.assertRaisesRegex(ValueError, 'Duplicate or unexpected'):
            m.verify_archive(self.archive, self.rows)

    def test_unexpected_rejected(self):
        self.write_modified(extra=tarfile.TarInfo('unexpected'))
        with self.assertRaisesRegex(ValueError, 'Duplicate or unexpected'):
            m.verify_archive(self.archive, self.rows)

    def test_hardlink_rejected(self):
        def change(ti, data):
            if ti.issym(): ti.type = tarfile.LNKTYPE
            return ti, data
        self.write_modified(change)
        with self.assertRaisesRegex(ValueError, 'Kind mismatch'):
            m.verify_archive(self.archive, self.rows)

    def test_truncated_gzip_rejected(self):
        m.write_archive(self.archive, self.stage, self.rows)
        self.archive.write_bytes(self.archive.read_bytes()[:-5])
        with self.assertRaises((EOFError, OSError)):
            m.verify_archive(self.archive, self.rows)


if __name__ == '__main__':
    unittest.main(verbosity=2)
