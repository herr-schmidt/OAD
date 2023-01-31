from numpy import random
from generator.data import addresses, procedure_time_mapping, procedure_avg_occurrences_mapping


class OADInstanceGenerator():

    def __init__(self, seed):
        self.seed = seed
        pass

    def generate_procedures_frequencies(self, patients_number):
        # (1 - 1 / patients_number): probability of a patients being visited
        # / 3: we assume uniform for different types of visits
        visit_mean = (1 - 1 / patients_number) * patients_number

        mean_values = {"VISITASTRUTTURATO": visit_mean / 3,
                       "VISITAMEDICO": visit_mean / 3,
                       "VISITAINFERMIERE": visit_mean / 3,
                       "INFUSIONESINGOLA": 0.75 * 2 / 3 * patients_number,
                       "INFUSIONEMULTIPLA": 0.75 / 3 * patients_number,
                       "MEDICAZIONEMIDLINE": 0.4 * patients_number
                      } | procedure_avg_occurrences_mapping

        mean_values_sum = sum(mean_values.values())

        return {procedure: f / mean_values_sum for (procedure, f) in mean_values.items()}

    def generate_procedures_set(self, treatments_number_range, patients_number):
        procedures_number = random.randint(low=treatments_number_range[0],
                                           high=treatments_number_range[1])

        procedures_frequencies = self.generate_procedures_frequencies(patients_number)
        return random.choice(list(procedures_frequencies.keys()),
                             size=procedures_number,
                             replace=False, 
                             p=list(procedures_frequencies.values()))

    # TODO
    def initialize_address_procedures_map(self, addresses, treatments_number_range, patients_per_day_range):
        # select a random number of patients 
        address_procedures_map = {}
        for address in addresses:
            patients = random.randint(low=patients_per_day_range[0], high=patients_per_day_range[1])
            procedures = self.generate_procedures_set(treatments_number_range, patients)
            address_procedures_map[address] = {procedure: procedure_time_mapping[procedure] for procedure in procedures}

        return address_procedures_map


    def initialize_address_state_map(self, addresses, treatment_days_range):
        address_state_map = {}
        # -1: patient ready for take in charge
        # 0: patient ready for dismission
        # any other value: patient can be assigned a set of procedures when chosen
        remaining_days = [d for d in range(-1, treatment_days_range[1] - treatment_days_range[0])]
        for address in addresses:
            address_state_map[address] = random.choice(remaining_days)

        return address_state_map

    def generate_instance(self, timespan=30, treatments_number_range=(2, 5), treatment_days_range=(5, 30), patients_per_day_range=(18, 25)): 

        instance = {address: {day: {} for day in range(timespan)} for address in addresses}
        address_state_map = self.initialize_address_state_map(addresses, treatment_days_range)
        address_procedures_map = self.initialize_address_procedures_map(addresses, treatments_number_range, patients_per_day_range)

        for day in range(timespan):
            chosen_addresses_number = random.randint(low=patients_per_day_range[0],
                                                     high=patients_per_day_range[1])
            chosen_addresses = random.choice(addresses,
                                             replace=False, 
                                             size=chosen_addresses_number)

            for address in chosen_addresses:
                # patient ready for being taken charge of
                if address_state_map[address] == -1:
                    instance[address][day] = {"PRESAINCARICO": 90}
                    address_state_map[address] = random.randint(low=treatment_days_range[0],
                                                                high=treatment_days_range[1])

                    procedures = self.generate_procedures_set(treatments_number_range, patients_number=chosen_addresses_number)
                    address_procedures_map[address] = {procedure: procedure_time_mapping[procedure] for procedure in procedures}
                # zero days left: patient dismission
                elif address_state_map[address] == 0:
                    instance[address][day] = {"DIMISSIONE": 35}
                    address_state_map[address] = -1
                else:
                    instance[address][day] = address_procedures_map[address]
                    address_state_map[address] = address_state_map[address] - 1

        return instance
