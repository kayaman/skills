"""Behavioral fixtures for the STL checker; no third-party packages or slicer needed."""
import importlib.util
from pathlib import Path
import struct
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('checker', Path(__file__).with_name('check_stl.py'))
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


def cube(origin=(0, 0, 0), size=1):
    x,y,z = origin
    v = [(x+dx*size,y+dy*size,z+dz*size) for dx,dy,dz in
         [(0,0,0),(1,0,0),(1,1,0),(0,1,0),(0,0,1),(1,0,1),(1,1,1),(0,1,1)]]
    quads = [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
    return [tuple(v[i] for i in tri) for a,b,c,d in quads for tri in [(a,b,c),(a,c,d)]]


def hanging_shape():
    # Closed voxel surface: left post on the bed, top beam, right arm ending at z=4.
    cells = {(x,y,z) for x in range(10) for y in range(2) for z in range(10)
             if x < 2 or z >= 8 or (x >= 8 and z >= 4)}
    directions = [(0,0,-1),(0,0,1),(0,-1,0),(1,0,0),(0,1,0),(-1,0,0)]
    tris=[]
    for x,y,z in cells:
        faces=cube((x,y,z))
        for i,(dx,dy,dz) in enumerate(directions):
            if (x+dx,y+dy,z+dz) not in cells:
                tris.extend(faces[2*i:2*i+2])
    return tris


class MeshChecks(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.path=Path(self.temp.name)/'part.stl'

    def tearDown(self):
        self.temp.cleanup()

    def write(self, tris):
        data=bytearray(80)+struct.pack('<I',len(tris))
        for tri in tris:
            data+=struct.pack('<12fH',0,0,0,*(v for p in tri for v in p),0)
        self.path.write_bytes(data)

    def inspect(self, tris, **kwargs):
        self.write(tris)
        return checker.check(self.path, **kwargs)

    def test_solid_and_enclosed_void(self):
        result=self.inspect(cube(size=10),require_bed=True,envelope=(170,170,170))
        self.assertFalse(result['errors']);self.assertFalse(result['warnings'])
        cavity=[tuple(reversed(tri)) for tri in cube((3,3,3),size=2)]
        result=self.inspect(cube(size=10)+cavity)
        self.assertFalse(result['errors']);self.assertEqual(result['cavities'],1)

    def test_open_and_flipped_faces(self):
        result=self.inspect(cube()[:-1]);self.assertTrue(result['warnings']);self.assertTrue(self.inspect(cube()[:-1],strict_topology=True)['errors'])
        tris=cube();tris[0]=tuple(reversed(tris[0]))
        self.assertTrue(self.inspect(tris)['errors'])
        self.assertTrue(self.inspect([tuple(reversed(t)) for t in cube()])['errors'])

    def test_nonmanifold_and_collapsed_triangles(self):
        tris=cube()
        self.assertTrue(self.inspect(tris+[tris[0]])['errors'])
        self.assertTrue(self.inspect(tris+[((0,0,0),)*3])['warnings'])

    def test_separate_bodies(self):
        self.assertTrue(self.inspect(cube()+cube((3,0,0)))['errors'])

    def test_hanging_arm_is_warning_not_topology_error(self):
        result=self.inspect(hanging_shape(),grid=0.4,layer_height=0.2)
        self.assertFalse(result['errors']);self.assertTrue(result['warnings'])

    def test_envelope_and_bed_are_explicit(self):
        self.assertTrue(self.inspect(cube(size=2),envelope=(1,3,3))['errors'])
        raised=cube((0,0,3))
        result=self.inspect(raised)
        self.assertFalse(result['errors']);self.assertTrue(result['warnings'])
        self.assertTrue(self.inspect(raised,require_bed=True)['errors'])
        self.assertTrue(self.inspect(cube((0,0,-1)),require_bed=True)['errors'])

    def test_malformed_nonfinite_and_empty_inputs(self):
        for data in [b'',b'solid broken\nvertex nope 2 3\n',b'solid x\nendsolid x\n',bytes(84)]:
            self.path.write_bytes(data)
            self.assertTrue(checker.check(self.path)['errors'])
        tris=cube();tris[0]=((float('nan'),0,0),tris[0][1],tris[0][2])
        self.assertTrue(self.inspect(tris)['errors'])
        self.write(cube());self.path.write_bytes(self.path.read_bytes()[:-7])
        self.assertTrue(checker.check(self.path)['errors'])

    def test_ascii_and_sampling_budget(self):
        lines=['solid cube']
        for tri in cube():
            lines+=['facet normal 0 0 0','outer loop']
            lines+=['vertex '+' '.join(map(str,p)) for p in tri]
            lines+=['endloop','endfacet']
        lines+=['endsolid cube']
        self.path.write_text('\n'.join(lines))
        self.assertFalse(checker.check(self.path)['errors'])
        result=checker.check(self.path,layer_height=0.0001)
        self.assertFalse(result['errors']);self.assertTrue(result['warnings'])


if __name__=='__main__': unittest.main()
