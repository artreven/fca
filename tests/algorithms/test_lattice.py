import fca
import os

class TestNorris:
    def setUp(self):
        abspath = os.path.dirname(__file__)
        small_cxt_path = os.path.join(abspath, 'small_cxt.cxt')
        self.small_cxt = fca.read_cxt(small_cxt_path)

    def test_norris(self):
        cl = fca.ConceptLattice(self.small_cxt)
        assert fca.Concept(self.small_cxt.objects, []) in cl
        assert fca.Concept([], self.small_cxt.attributes) in cl
        assert len(cl) > 2
