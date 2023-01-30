from numpy import random
from generator.data import addresses, DISMISSION, FIRST_EXAMINATION, procedure_time_mapping
from generator.model import Patient


class OADInstanceGenerator():

    def __init__(self, seed):
        self.seed = seed
        pass

    def generate_procedures_list(self, treatments_number, first_day=False, last_day=False):
        procedures_dict = {}

        # handle first and last day, which involve a mandatory kind of procedure each
        first_procedure_index = 0
        if first_day:
            procedures_dict[FIRST_EXAMINATION[0]] = FIRST_EXAMINATION[1]
            treatments_number -= 1
            first_procedure_index = 1
        if last_day:
            procedures_dict[DISMISSION[0]] = DISMISSION[1]
            treatments_number -= 1
            first_procedure_index = 1

        for treatment_id in range(first_procedure_index, treatments_number):
            # pick a random procedure according to a uniform distribution;
            # we assume each procedure can be picked at most once per day, per patient (replace=False)
            procedure = random.choice(list(procedure_time_mapping.keys()),
                                      replace=False)
            procedures_dict[procedure] = procedure_time_mapping[procedure]

        return procedures_dict

    def generate_instance(self, patients=100, treatment_days_range=(5, 30), treatments_number_range=(2, 5)):
        instance = []

        for patient_id in range(1, patients + 1):
            # pick a random address according to a uniform distribution
            address = random.choice(addresses)
            treatment_days = random.randint(low=treatment_days_range[0],
                                            high=treatment_days_range[1] + 1)

            treatments_by_day = {}
            for day in range(treatment_days):
                first_day = False
                last_day = False
                if day == 0:
                    first_day = True
                if day == treatment_days - 1:
                    last_day = True

                treatments_number = random.randint(low=treatments_number_range[0],
                                                   high=treatments_number_range[1])

                treatments_by_day[day] = self.generate_procedures_list(treatments_number,
                                                                       first_day=first_day,
                                                                       last_day=last_day)

            patient = Patient(id=patient_id,
                              address=address,
                              treatments_by_day=treatments_by_day)
            instance.append(patient)

        return instance
