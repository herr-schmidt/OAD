import unittest
from generator import OADInstanceGenerator

class TestOADInstanceGenerator(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.generator = OADInstanceGenerator(seed=58492)
        self.instance = self.generator.generate_instance(patients=100)

    def test_single_dismission_per_patient(self):
        for patient in self.instance:
            dismissions = 0
            dismission_day = 0
            days = patient.treatments_by_day.keys()
            for day in days:
                for procedure in patient.treatments_by_day[day].keys():
                    if procedure == "DIMISSIONE":
                        dismissions += 1
                        dismission_day = day

            self.assertTrue(dismissions == 1 and dismission_day == len(days) - 1)

    def test_single_take_in_charge_per_patient(self):
        for patient in self.instance:
            takes_in_charge = 0
            take_in_charge_day = 0
            days = patient.treatments_by_day.keys()
            for day in days:
                for procedure in patient.treatments_by_day[day].keys():
                    if procedure == "PRESAINCARICO":
                        takes_in_charge += 1
                        take_in_charge_day = day

            self.assertTrue(takes_in_charge == 1 and take_in_charge_day == 0)
