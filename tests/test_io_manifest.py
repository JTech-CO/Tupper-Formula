import unittest
import tempfile
import json
from copy import deepcopy
from pathlib import Path
from xml.etree import ElementTree as ET
from tupper_formula import Bitmap
from tupper_formula.io import read_bitmap, pbm, svg
from tupper_formula.manifest import make_manifest, verify_manifest, write_bundle

A=Bitmap(("010","101","111","101","101"))

class IOTests(unittest.TestCase):
    def test_pbm_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/"a.pbm"; p.write_text(pbm(A))
            self.assertEqual(read_bitmap(p),A)

    def test_ascii_dot_hash(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/"a.txt"; p.write_text(".#.\n#.#\n###\n#.#\n#.#\n")
            self.assertEqual(read_bitmap(p),A)

    def test_pbm_comments(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/"a.pbm"; p.write_text("P1 # comment\n2 1\n1 # more\n0\n")
            self.assertEqual(read_bitmap(p).rows,("10",))

    def test_pbm_bad_count(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/"a.pbm"; p.write_text("P1\n2 2\n1 0\n")
            with self.assertRaises(ValueError): read_bitmap(p)

    def test_svg_escaped_and_valid(self):
        root=ET.fromstring(svg(A,title='<script>alert("x")</script>'))
        self.assertEqual(root.find('{http://www.w3.org/2000/svg}title').text,'<script>alert("x")</script>')
        self.assertNotIn('<script>',svg(A,title='<script>'))

    def test_svg_historical(self):
        self.assertIn('Display: historical',svg(A,'historical'))

class ManifestTests(unittest.TestCase):
    def test_literal_verification(self):
        result=verify_manifest(make_manifest(A),literal=True)
        self.assertTrue(result['passed']); self.assertEqual(result['literal_midpoints'],15)

    def test_tampering_rejected(self):
        original=make_manifest(A)
        changes={'N':'1','k':'1','bitmap_sha256':'0'*64,'height':6,'width':True,
                 'formula_latex':'x=y','canonical':False,'encoding':'row-major',
                 'schema':'other','domain':{},'display_orientation':'hidden'}
        for key,value in changes.items():
            with self.subTest(field=key):
                data=deepcopy(original);data[key]=value
                with self.assertRaises((ValueError,TypeError)):verify_manifest(data)

    def test_stored_verification_flag_not_trusted(self):
        data=make_manifest(A);data['verification']={'passed':True};data['k']='1'
        with self.assertRaises(ValueError): verify_manifest(data)

    def test_digest_includes_dimensions(self):
        self.assertNotEqual(Bitmap(("01","01")).digest(),Bitmap(("0101",)).digest())

    def test_bundle_no_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"new";data=write_bundle(A,path)
            self.assertTrue(verify_manifest(data)['passed'])
            self.assertEqual((path/'target.pbm').read_bytes(),(path/'decoded.pbm').read_bytes())
            with self.assertRaises(FileExistsError):write_bundle(A,path)

    def test_all_checked_in_examples(self):
        root=Path(__file__).resolve().parents[1]
        paths=list((root/'examples').glob('*/experiment.json'))
        self.assertGreaterEqual(len(paths),3)
        for p in paths:
            with self.subTest(path=p.name):
                self.assertTrue(verify_manifest(json.loads(p.read_text()))['passed'])
