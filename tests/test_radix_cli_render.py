import contextlib
import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path
from tupper_formula.radix import encode_array,decode_array
from tupper_formula.cli import main

class RadixTests(unittest.TestCase):
    def test_rgb_palette_indices(self):
        values=[0,2,1,2,0,1]
        self.assertEqual(decode_array(encode_array(values,(2,3),3),(2,3),3),values)

    def test_volume(self):
        values=[i%4 for i in range(24)]
        self.assertEqual(decode_array(encode_array(values,(2,3,4),4),(2,3,4),4),values)

    def test_index_order(self):
        self.assertEqual(encode_array([1,0,1,1],(2,2),2),13)

    def test_invalid(self):
        for values,shape,base in (([2],(1,),2),([0],(2,),2),([True],(1,),2),([0],(1,),1)):
            with self.assertRaises((ValueError,TypeError)):encode_array(values,shape,base)

class CLITests(unittest.TestCase):
    def test_end_to_end(self):
        with tempfile.TemporaryDirectory() as tmp, contextlib.redirect_stdout(io.StringIO()):
            path=Path(tmp);(path/'a.txt').write_text('010\n101\n111\n101\n101\n')
            self.assertEqual(main(['encode',str(path/'a.txt'),'-o',str(path/'out')]),0)
            self.assertEqual(main(['verify',str(path/'out/experiment.json'),'--literal']),0)
            self.assertEqual(main(['decode','--k-file',str(path/'out/k.txt'),'--width','3','--height','5','-o',str(path/'a.svg')]),0)
            self.assertEqual(main(['cell',str(path/'out/experiment.json'),'--x','1','--j','4']),0)

    def test_error_exit(self):
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(main(['verify','does-not-exist.json']),2)

@unittest.skipUnless(importlib.util.find_spec('matplotlib') and importlib.util.find_spec('PIL'), 'optional render extras not installed')
class RenderTests(unittest.TestCase):
    def test_construct_formula(self):
        from tupper_formula.render import rasterize_formula
        from tupper_formula.manifest import make_manifest,verify_manifest
        bitmap,source=rasterize_formula(24)
        self.assertEqual(bitmap.height,24)
        self.assertGreater(bitmap.population,0)
        self.assertTrue(verify_manifest(make_manifest(bitmap,source))['passed'])

    def test_transparency(self):
        from PIL import Image
        from tupper_formula.render import load_image
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'transparent.png'
            im=Image.new('RGBA',(2,2),(0,0,0,0));im.putpixel((0,0),(0,0,0,255));im.save(path)
            self.assertEqual(load_image(path).rows,('10','00'))

    def test_unsupported_height(self):
        from tupper_formula.render import rasterize_formula
        with self.assertRaises(ValueError):rasterize_formula(2)
