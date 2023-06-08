from numpy import random
from generator.data import addresses, procedure_time_mapping, procedure_avg_occurrences_mapping, Procedures, distance_matrix, skills_matrix, teams, teams_skill
import pandas as pd
import os


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
                    treatment_span = random.randint(low=treatment_span_range[0],
                                                    high=treatment_span_range[1])
                    calendar[address][day] = {Procedures.PRESAINCARICO.value: {"service_time": 90, "duration": treatment_span}}
                    dismission_day = day + treatment_span + 1
                    if dismission_day < timespan:
                        calendar[address][dismission_day] = {Procedures.DIMISSIONE.value: {"service_time": 35, "duration": None}}

                    day = dismission_day + 1
                else:
                    day += 1
        return calendar
    
    def generate_input(self, calendar, init_day, treatments_number_range=(2, 5)):
        input_instances = {"initialization": None,
                           "post_initialization": None}
        
        patient = 0
        for k in input_instances.keys():
            take_in_charge = {}
            dismission = {}
            duration = {}
            addresses = {}

            for address in calendar.keys():
                if k == "initialization":
                    for day in range(init_day, -1, -1):
                        if Procedures.DIMISSIONE.value in calendar[address][day]:
                            break
                        if Procedures.PRESAINCARICO.value in calendar[address][day]:
                            patient += 1
                            take_in_charge[patient] = 0 # day + 1
                            duration[patient] = calendar[address][day][Procedures.PRESAINCARICO.value]["duration"] + 2 # +2: add arrival and dismission
                            dismission[patient] = day + calendar[address][day][Procedures.PRESAINCARICO.value]["duration"] + 1
                            addresses[patient] = address
                            break
                else:            
                    for day in range(init_day + 1, len(calendar[address])):
                        if Procedures.PRESAINCARICO.value in calendar[address][day]:
                            patient += 1
                            take_in_charge[patient] = day - init_day
                            duration[patient] = calendar[address][day][Procedures.PRESAINCARICO.value]["duration"] + 2 # +2: add arrival and dismission
                            dismission[patient] = day + calendar[address][day][Procedures.PRESAINCARICO.value]["duration"] + 1
                            addresses[patient] = address

            treatments_per_week = {p: random.randint(low=1, high=6) for p in list(addresses.keys())}

            procedures = {}
            daily_treatments_duration = {}
            for p in list(addresses.keys()):
                patient_procedures = {procedure: procedure_time_mapping[procedure] for procedure in self.generate_procedures_set(treatments_number_range)}
                procedures[p] = patient_procedures
                daily_treatments_duration[p] = sum(procedure_time for procedure_time in patient_procedures.values())

            average_distances = self.compute_average_distances(addresses)

            input_instances[k] = {"take_in_charge": take_in_charge,
                                  "duration": duration,
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
            
        return input_instances

    def compute_average_distances(self, addresses):
        average_distances = {}
        for p in list(addresses.keys()):
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

    def export_to_csv(self, input_instances):
        for k in input_instances.keys():
            input = input_instances[k]
            file_name = k

            patients_ids = [id for id in list(input["take_in_charge"].keys())]
            service_times = [service_time for service_time in input["daily_treatments_duration"].values()]
            travelling_times = [round(travelling_time, 3) for travelling_time in input["average_distances"].values()]
            take_in_charge_day = [take_in_charge for take_in_charge in input["take_in_charge"].values()]
            durations = [duration for duration in input["duration"].values()]

            patients_data_dict = {"ID": patients_ids}

            patient_skills = self.compute_patients_skills(input["procedures"])
            treatments_per_week = input["treatments_per_week"]

            skills = max(teams_skill.values())
            skills_columns = []

            for skill in range(skills, 0, -1):
                skill_list = {p: 0 for p in patients_ids}
                for patient in patients_ids:
                    if patient_skills[patient] == skill:
                        skill_list[patient] = treatments_per_week[patient]
                skill_column = "Skill_" + str(skill)
                skills_columns.append(skill_column)
                patients_data_dict[skill_column] = list(skill_list.values())

            patients_data_dict["Service_time"] = service_times
            patients_data_dict["Average_travelling_time"] = travelling_times

            patients_data_dict["Arrival_day"] = take_in_charge_day
            patients_data_dict["Duration"] = durations

            patients_data_frame = pd.DataFrame(data=patients_data_dict)
            patients_data_frame.sort_values(by=skills_columns, ascending=False, inplace=True)

            teams_ids = [id for id in range(1, len(teams) + 1)]
            daily_availability = 300
            teams_availability = [daily_availability for _ in range(1, len(teams) + 1)]

            teams_data_dict = {"Team ID": teams_ids,
                               "Team skill": teams_skill.values(),
                               "Daily cap": teams_availability}

            patterns_data_frame = pd.DataFrame(data={"Patterns": self.generate_patterns(total_skills=skills)})

            teams_data_frame = pd.DataFrame(data=teams_data_dict)

            os.makedirs("csv_input", exist_ok=True)
            patients_data_frame.to_csv(path_or_buf="csv_input/" + file_name + ".csv", sep="\t", index=False, mode="w")
            open("csv_input/" + file_name + ".csv", mode="a").write("\n")
            patterns_data_frame.to_csv(path_or_buf="csv_input/" + file_name + ".csv", sep="\t", index=False, mode="a")
            open("csv_input/" + file_name + ".csv", mode="a").write("\n")
            teams_data_frame.to_csv(path_or_buf="csv_input/" + file_name + ".csv", sep="\t", index=False, mode="a")

    def build_teams_procedure_sets(self):
        teams_procedure_sets = {}
        for team_id in teams.keys():
            team_procedures = set()
            for skill in skills_matrix.keys():
                for operator in teams[team_id]:
                    if skills_matrix[skill][operator] == 1:
                        team_procedures.add(skill)
            teams_procedure_sets[team_id] = team_procedures

        return teams_procedure_sets

    def compute_patients_skills(self, patients_procedures):
        teams_procedure_sets = self.build_teams_procedure_sets()
        patient_skills = {}

        for patient in list(patients_procedures.keys()):
            procedures = set(patients_procedures[patient].keys())
            least_skill_level = max(teams_skill.values())  # higher value means higher skill
            for (team, procedure_set) in teams_procedure_sets.items():
                if procedures.issubset(procedure_set) and teams_skill[team] < least_skill_level:
                    least_skill_level = teams_skill[team]

            patient_skills[patient] = least_skill_level

        return patient_skills

    def generate_patterns(self, total_skills, scheduling_horizon=5):
        patterns = []
        for skill in range(1, total_skills + 1):
            skill_treatments_per_week = set([i for i in range(1, scheduling_horizon + 1)])

            for treatments in skill_treatments_per_week:
                schedule = [skill for _ in range(0, treatments)] + [0 for _ in range(treatments + 1, scheduling_horizon + 1)]
                random.shuffle(schedule)
                patterns.append(schedule)
        return patterns
