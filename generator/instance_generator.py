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

    def generate_initialization_input(self, calendar, init_day, treatments_number_range=(2, 5)):
        self.patient = 0

        take_in_charge = {}
        dismission = {}
        duration = {}
        addresses = {}
        address_patient_id_mapping = {}

        for address in calendar.keys():
            for day in range(init_day, -1, -1):
                if Procedures.DIMISSIONE.value in calendar[address][day]:
                    break
                if Procedures.PRESAINCARICO.value in calendar[address][day]:
                    self.patient += 1
                    take_in_charge[self.patient] = 0  # day + 1
                    duration[self.patient] = calendar[address][day][Procedures.PRESAINCARICO.value]["duration"] + 2  # +2: add arrival and dismission
                    dismission[self.patient] = day + calendar[address][day][Procedures.PRESAINCARICO.value]["duration"] + 1
                    addresses[self.patient] = address
                    address_patient_id_mapping[address] = self.patient
                    break

        treatments_per_week = {p: random.randint(low=1, high=6) for p in list(addresses.keys())}
        activity = {} # -1: no longer active; 0: last lap (dismission found); 1: active

        procedures = {}
        daily_treatments_duration = {}
        for p in list(addresses.keys()):
            patient_procedures = {procedure: procedure_time_mapping[procedure] for procedure in self.generate_procedures_set(treatments_number_range)}
            procedures[p] = patient_procedures
            daily_treatments_duration[p] = sum(procedure_time for procedure_time in patient_procedures.values())
            activity[p] = 1 # initialization: we assume no dismission can occur, so every patient is indefinitely active

            average_distances = self.compute_average_distances(addresses)

        return {"take_in_charge": take_in_charge,
                "duration": duration,
                "dismission": dismission,
                "treatments_per_week": treatments_per_week,
                "procedures": procedures,
                "daily_treatments_duration": daily_treatments_duration,
                "addresses": addresses,
                "average_distances": average_distances,
                "skills": skills_matrix,
                "patients": self.patient,
                "teams": len(skills_matrix[1]),
                "activity": activity,
                "address_patient_id_mapping": address_patient_id_mapping
                }

    def generate_post_init_input(self, calendar, init_day, step=5, treatments_number_range=(2, 5)):
        calendar_span = len(calendar[list(calendar.keys())[0]])

        # full post-initialization batches we can get
        batches = (calendar_span - (init_day + 1)) // step

        take_in_charge = {}
        dismission = {}
        duration = {}
        addresses = {}

        for address in calendar.keys():
            first_batch_day = init_day + (step * (batches - 1) + 1)
            for day in range(first_batch_day, first_batch_day + step):
                procedure = calendar[address][day]
                arrival_departure_events = []
                # take in charge: need to add new patient (new id)
                if procedure in [Procedures.PRESAINCARICO.value]:
                    self.patient += 1
                    take_in_charge[self.patient] = day - init_day
                    duration[self.patient] = calendar[address][day][procedure]["duration"] + 2  # +2: add arrival and dismission
                    dismission[self.patient] = day + calendar[address][day][procedure]["duration"] + 1
                    addresses[self.patient] = address
                    activity[self.patient] = 1 # set active
                
                arrival_departure_events.append(procedure)
                
                if len(arrival_departure_events) == 1 and Procedures.DIMISSIONE.value in arrival_departure_events:
                    #segna come last lap
                    activity[address_patient_id_mapping[address]] = 0
                if len(arrival_departure_events) == 2 and arrival_departure_events[0] == Procedures.DIMISSIONE.value and arrival_departure_events[1] == Procedures.PRESAINCARICO.value:
                    activity[address_patient_id_mapping[address]] = 0


        treatments_per_week = {p: random.randint(low=1, high=6) for p in list(addresses.keys())}

        procedures = {}
        daily_treatments_duration = {}
        for p in list(addresses.keys()):
            patient_procedures = {procedure: procedure_time_mapping[procedure] for procedure in self.generate_procedures_set(treatments_number_range)}
            procedures[p] = patient_procedures
            daily_treatments_duration[p] = sum(procedure_time for procedure_time in patient_procedures.values())

        average_distances = self.compute_average_distances(addresses)

        return {"take_in_charge": take_in_charge,
                "duration": duration,
                "dismission": dismission,
                "treatments_per_week": treatments_per_week,
                "procedures": procedures,
                "daily_treatments_duration": daily_treatments_duration,
                "addresses": addresses,
                "average_distances": average_distances,
                "skills": skills_matrix,
                "patients": self.patient,
                "teams": len(skills_matrix[1])
                }

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

    def export_to_xlsx(self, input, k):

        file_name = "INS" + str(k)

        patients_ids = [id for id in list(input["take_in_charge"].keys())]
        service_times = [service_time for service_time in input["daily_treatments_duration"].values()]
        travelling_times = [round(travelling_time, 3) for travelling_time in input["average_distances"].values()]
        take_in_charge_day = [take_in_charge for take_in_charge in input["take_in_charge"].values()]
        durations = [duration for duration in input["duration"].values()]

        patients_data_dict = {"ID": patients_ids}

        patient_skills = self.compute_patients_skills(input["procedures"])
        treatments_per_week = [visit for visit in input["treatments_per_week"].values()]

        patients_data_dict["Skill"] = [skill for skill in patient_skills.values()]
        patients_data_dict["Treatments_per_week"] = treatments_per_week

        patients_data_dict["Service_time"] = service_times
        patients_data_dict["Average_travelling_time"] = travelling_times

        patients_data_dict["Arrival_day"] = take_in_charge_day
        patients_data_dict["Duration"] = durations

        patients_data_frame = pd.DataFrame(data=patients_data_dict)
        patients_data_frame.sort_values(by=["Skill", "Treatments_per_week"], ascending=[True, False], inplace=True)

        teams_ids = [id for id in range(1, len(teams) + 1)]
        weekly_availability = 1500
        teams_availability = [weekly_availability for _ in range(1, len(teams) + 1)]

        teams_data_dict = {"Team_ID": teams_ids,
                           "Team_skill": teams_skill.values(),
                           "Weekly_capacity": teams_availability}

        total_skills = len(set(teams_skill.values()))
        patterns_data_frame = pd.DataFrame(data={"Patterns": self.generate_patterns(total_skills=total_skills)})

        teams_data_frame = pd.DataFrame(data=teams_data_dict)
        teams_data_frame.sort_values(by="Team_skill", ascending=True, inplace=True)

        teams_number_data_frame = pd.DataFrame(data={"Teams": [len(teams_ids)]})

        sorted_patients_skills = list(reversed(patients_data_frame["Skill"].tolist()))
        skill_match = []
        for skill in range(1, total_skills):
            try:
                skill_match.append(len(sorted_patients_skills) - sorted_patients_skills.index(skill))
            except:
                skill_match.append(-1)

        skill_match_data_frame = pd.DataFrame(data={"Skill_match": skill_match})

        os.makedirs("input", exist_ok=True)
        with pd.ExcelWriter(path="input/" + file_name + ".xlsx", mode="w", engine="openpyxl") as writer:
            patients_data_frame.to_excel(excel_writer=writer, index=False,  columns=["Treatments_per_week"], sheet_name="visit", header=False)
        with pd.ExcelWriter(path="input/" + file_name + ".xlsx", mode="a", engine="openpyxl") as writer:
            teams_number_data_frame.to_excel(excel_writer=writer, index=False,  columns=["Teams"], sheet_name="Operators", header=False)
            teams_data_frame.to_excel(excel_writer=writer, index=False,  columns=["Weekly_capacity"], sheet_name="capacity", header=False)
            patterns_data_frame.to_excel(excel_writer=writer, index=False,  columns=["Patterns"], sheet_name="pattern", header=False)
            patients_data_frame.to_excel(excel_writer=writer, index=False,  columns=["Average_travelling_time"], sheet_name="travel", header=False)
            patients_data_frame.to_excel(excel_writer=writer, index=False,  columns=["Service_time"], sheet_name="service", header=False)
            skill_match_data_frame.to_excel(excel_writer=writer, index=False,  columns=["Skill_match"], sheet_name="SkillMatch", header=False)
            teams_data_frame.to_excel(excel_writer=writer, index=False,  columns=["Team_skill"], sheet_name="TeamsSkills", header=False)

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
        patterns = [[0 for _ in range(0, scheduling_horizon)]]
        for skill in range(1, total_skills + 1):
            skill_treatments_per_week = set([i for i in range(1, scheduling_horizon + 1)])

            for treatments in skill_treatments_per_week:
                schedule = [skill for _ in range(0, treatments)] + [0 for _ in range(treatments + 1, scheduling_horizon + 1)]
                random.shuffle(schedule)
                patterns.append(schedule)
        return patterns
