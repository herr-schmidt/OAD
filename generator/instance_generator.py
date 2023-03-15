from numpy import random
from generator.data import addresses, procedure_time_mapping, procedure_avg_occurrences_mapping, Procedures, distance_matrix, skills_matrix


class OADInstanceGenerator():

    def __init__(self, seed=781015):
        """Class used for generating an event calendar and an input for the OAD model.

        Args:
            seed (int, optional): Seed for underlying random number generator, in order to ensure replicability. Defaults to 781015.
        """
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

    def generate_events_calendar(self, timespan=30, treatment_span_range=(5, 30), take_in_charge_probability=1/25):
        """Method used for generating a calendar of take-in-charge and dismission events, with a timespan specified by the user.

        Args:
            timespan (int, optional): Length of the calendar horizon. Defaults to 30.
            treatment_span_range (tuple, optional): Extremes of the interval from which the distance take_in_charge--dismission is sampled. Defaults to (5, 30).
            take_in_charge_probability (float, optional): Probability of having a take-in-charge event on any given day. Defaults to 1/25.

        Returns:
            dict[str, dict[int, dict[int, int]]]: A dict containing information about take-in-charge and dismission events for each address and each day in the horizon.
        """
        calendar = {address: {day: {}
                              for day in range(timespan)} for address in addresses}

        for address in calendar.keys():
            day = 0
            while day < timespan:
                take_in_charge = random.uniform() <= take_in_charge_probability

                if take_in_charge:
                    calendar[address][day] = {Procedures.PRESAINCARICO.value: 90}

                    treatment_span = random.randint(low=treatment_span_range[0],
                                                    high=treatment_span_range[1])

                    dismission_day = day + treatment_span + 1
                    if dismission_day < timespan:
                        calendar[address][dismission_day] = {Procedures.DIMISSIONE.value: 35}

                    day = dismission_day + 1

                else:
                    day += 1

        return calendar

    def generate_input(self, calendar, first_day, last_day, treatments_number_range=(2, 5)):
        """Generates an input for our model given an event calendar, slicing it from first_day (included) to last_day (excluded).

        Args:
            calendar (dict[str, dict[int, dict[int, int]]]): Event calendar with take-in-charge and dismission events.
            first_day (int): First day from which input is generated from the event calendar.
            last_day (int): Day following the last from which input is generated from the event calendar.
            treatments_number_range (tuple, optional): Interval [a, b) from which the number of daily treatments for each patients is sampled. Defaults to (2, 5).

        Returns:
            dict: A dict containing the parameters for the model.
        """
        take_in_charge = {}
        dismission = {}
        addresses = {}

        patient = 0
        for address in calendar.keys():
            previous_tic_found = False
            for day in range(first_day, last_day):
                if Procedures.PRESAINCARICO.value in calendar[address][day]:
                    previous_tic_found = True
                    patient += 1
                    take_in_charge[patient] = day + 1
                if Procedures.DIMISSIONE.value in calendar[address][day]:
                    if not previous_tic_found:
                        patient += 1
                    else:
                        previous_tic_found = False
                    dismission[patient] = day + 1
                if patient > 0:
                    addresses[patient] = address

        for p in range(1, patient + 1):
            if not p in take_in_charge:
                take_in_charge[p] = -1
            if not p in dismission:
                dismission[p] = -1

        treatments_per_week = {p: random.randint(
            low=1, high=6) for p in range(1, patient + 1)}

        procedures = {}
        daily_treatments_duration = {}
        for p in range(1, patient + 1):
            patient_procedures = {procedure: procedure_time_mapping[procedure] for procedure in self.generate_procedures_set(treatments_number_range)}
            procedures[p] = patient_procedures
            daily_treatments_duration[p] = sum(procedure_time for procedure_time in patient_procedures.values())

        average_distances = self.compute_average_distances(addresses)

        return {"take_in_charge": take_in_charge,
                "dismission": dismission,
                "treatments_per_week": treatments_per_week,
                "procedures": procedures,
                "daily_treatments_duration": daily_treatments_duration,
                "addresses": addresses,
                "average_distances": average_distances,
                "skills": skills_matrix,
                "patients": patient,
                "teams": len(skills_matrix[1])
                }

    def compute_average_distances(self, addresses):
        average_distances = {}
        for p in range(1, len(addresses) + 1):
            patient_address = addresses[p]
            all_patients_addresses = frozenset(addresses.values())
            average_distance = 0
            for address in all_patients_addresses:
                if address == patient_address:
                    continue
                average_distance += distance_matrix[(frozenset([address, patient_address]))]
            average_distance = average_distance / (len(all_patients_addresses) - 1)
            average_distances[p] = average_distance

        return average_distances
