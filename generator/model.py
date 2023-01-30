import pprint

class Patient():

    def __init__(self, id: int, address: str, treatments_by_day: dict):
        self.id = id
        self.address = address
        self.treatments_by_day = treatments_by_day

    def __str__(self) -> str:
        return "Patient ID: " + str(self.id) + "\nPatient address: " + str(self.address) + "\nTreatments by day:\n" + pprint.pformat(self.treatments_by_day, indent=4) + "\n"
