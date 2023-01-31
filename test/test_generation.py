import unittest
from generator import OADInstanceGenerator

class TestOADInstanceGenerator(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.generator = OADInstanceGenerator(seed=58492)
        self.instance = self.generator.generate_instance(patients=100)
        