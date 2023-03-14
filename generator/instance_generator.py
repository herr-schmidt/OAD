from numpy import random
from generator.data import addresses, procedure_time_mapping, procedure_avg_occurrences_mapping


class OADInstanceGenerator():

    def __init__(self, seed= 781015):
        self.seed = seed
        random.seed(seed=seed)
        self.procedures_frequencies = self.generate_procedures_frequencies()

    def generate_procedures_frequencies(self):
        # (1 - 1 / patients_number): probability of a patients being visited
        # / 3: we assume uniform for different types of visits
        # visit_mean = (1 - 1 / patients_number) * patients_number

        # merge (|) day-dependent means with known means
        # mean_values = {"VISITASTRUTTURATO": visit_mean / 3,
        #                "VISITAMEDICO": visit_mean / 3,
        #                "VISITAINFERMIERE": visit_mean / 3,
        #                "INFUSIONESINGOLA": 0.75 * 2 / 3 * patients_number,
        #                "INFUSIONEMULTIPLA": 0.75 / 3 * patients_number,
        #                "MEDICAZIONEMIDLINE": 0.4 * patients_number
        #                } | procedure_avg_occurrences_mapping

        mean_values_sum = sum(procedure_avg_occurrences_mapping.values())

        return {procedure: f / mean_values_sum for (procedure, f) in procedure_avg_occurrences_mapping.items()}

    def generate_procedures_set(self, treatments_number_range):
        procedures_number = random.randint(low=treatments_number_range[0],
                                           high=treatments_number_range[1])

        return random.choice(list(self.procedures_frequencies.keys()),
                             size=procedures_number,
                             replace=False,
                             p=list(self.procedures_frequencies.values()))

    def generate_instance(self, timespan=30, treatment_span_range=(5, 30), take_in_charge_probability=1 / 25):
        instance = {address: {day: {} for day in range(timespan)} for address in addresses}

        for address in instance.keys():
            day = 0
            while day < timespan:
                take_in_charge = random.uniform() <= take_in_charge_probability

                if take_in_charge:
                    instance[address][day] = {"PRESAINCARICO": 90}

                    treatment_span = random.randint(low=treatment_span_range[0],
                                                    high=treatment_span_range[1])

                    dismission_day = day + treatment_span + 1
                    if dismission_day < timespan:
                        instance[address][dismission_day] = {"DIMISSIONE": 35}

                    day = dismission_day + 1

                else:
                    day += 1

        return instance

    def generate_input(self, instance, first_day, last_day, treatments_number_range=(2, 5)):
        take_in_charge = {}
        dismission = {}

        patient = 0
        for address in instance.keys():
            previous_tic_found = False
            for day in range(first_day, last_day + 1):
                if "PRESAINCARICO" in instance[address][day]:
                    previous_tic_found = True
                    patient += 1
                    take_in_charge[patient] = day
                if "DIMISSIONE" in instance[address][day]:
                    if not previous_tic_found:
                        patient += 1
                    else:
                        previous_tic_found = False
                    dismission[patient] = day

        for p in range(1, patient + 1):
            if not p in take_in_charge:
                take_in_charge[p] = -1
            if not p in dismission:
                dismission[p] = -1

        treatments_per_week = {p: random.randint(low=1, high=6) for p in range(1, patient + 1)}

        procedures = {}
        daily_treatments_duration = {}
        for p in range(1, patient + 1):
            patient_procedures = {procedure: procedure_time_mapping[procedure] for procedure in self.generate_procedures_set(treatments_number_range)}
            procedures[p] = patient_procedures
            daily_treatments_duration[p] = sum(procedure_time for procedure_time in patient_procedures.values())

        return {"take_in_charge": take_in_charge,
                "dismission": dismission,
                "treatments_per_week": treatments_per_week,
                "procedures": procedures,
                "daily_treatments_duration": daily_treatments_duration
        }
