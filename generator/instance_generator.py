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
    
    def generate_week_mask(self, mask_size=5):
        mask = random.binomial(n=1, p=0.5, size=mask_size)
        # empty masks are not allowed: we need at least one care day per mask
        while sum(mask) == 0:
             mask = random.binomial(n=1, p=0.5, size=mask_size)
        return mask

    def generate_instance(self, timespan=30, treatments_number_range=(2, 5), treatment_days_range=(5, 30), pattern_mask_size=5, take_in_charge_probability=1 / 25):
        instance = {address: {day: {} for day in range(timespan)} for address in addresses}

        for address in instance.keys():
            day = 0
            while day < timespan:
                take_in_charge = random.uniform() <= take_in_charge_probability

                if take_in_charge:
                    instance[address][day] = {"PRESAINCARICO": 90}
                    day += 1

                    procedures = {procedure: procedure_time_mapping[procedure] for procedure in self.generate_procedures_set(treatments_number_range)}
                    treatment_days = random.randint(low=treatment_days_range[0],
                                                    high=treatment_days_range[1])
                    
                    mask = self.generate_week_mask(mask_size=pattern_mask_size)
                    repeated_masks = 0
                    for d in range(day, timespan):
                        if treatment_days == 0:
                            instance[address][d] = {"DIMISSIONE": 35}
                            break
                        mask_index = d - (day + pattern_mask_size * repeated_masks)
                        if mask[mask_index] == 1:
                            instance[address][d] = procedures
                            treatment_days -= 1
                        if mask_index == pattern_mask_size - 1:
                            repeated_masks += 1
                    day = d + 1
                else:
                    day += 1

        return instance
