import fca

class TestNorris:
    def setUp(self):
        self.big_cxt = fca.read_cxt('small_cxt.cxt')

    def test_norris(self):
        cl = fca.ConceptLattice(self.big_cxt)
        assert fca.Concept(set(), set(self.big_cxt.attributes)) in cl
        assert fca.Concept(set(self.big_cxt.objects), set()) in cl
        assert len(cl) > 2
