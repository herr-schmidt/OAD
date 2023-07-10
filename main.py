from generator.instance_generator import OADInstanceGenerator
import pprint
import plotly.express as px
from plotly import graph_objects as go
from generator.data import Procedures
from initialization import perform_initialization
from pandas import read_excel
from math import isnan

if __name__ == "__main__":
    generator = OADInstanceGenerator(seed=58492)
    timespan = 100
    event_calendar = generator.generate_events_calendar(timespan=timespan,
                                                  treatment_span_range=(5, 30))

    # visual intuition
    heatmap_matrix = [[] for _ in event_calendar.keys()]
    i = 0
    for address in event_calendar.keys():
        for day in event_calendar[address].keys():
            if event_calendar[address][day] == {}:
                heatmap_matrix[i].append(3)
            elif Procedures.DIMISSIONE.value in event_calendar[address][day]:
                heatmap_matrix[i].append(0)
            elif Procedures.PRESAINCARICO.value in event_calendar[address][day]:
                heatmap_matrix[i].append(1)
            else:
                heatmap_matrix[i].append(2)
        i += 1

    dismission = "#4B2991"
    take_in_charge = "#C0369D"
    treatment = "#FA7876"
    empty_slot = "#EDD9A3"

    colors = [[0, dismission],
              [0.25, dismission],
              [0.25, take_in_charge],
              [0.5, take_in_charge],
              [0.5, treatment],
              [0.75, treatment],
              [0.75, empty_slot],
              [1, empty_slot]]

    fig = px.imshow(heatmap_matrix,
                    title="Planned treatments - " +
                    str(timespan) + " days horizon",
                    color_continuous_scale=colors,
                    labels={"x": "Horizon day", "y": "Address"})

    fig.update_layout(coloraxis_colorbar=dict(
        title="Slot type",
        tickvals=[3/8, 9/8, 15/8, 21/8],
        ticktext=["Dismission", "Take in charge", "Treatment", "Empty slot"],
        lenmode="pixels",
        len=400
    ))

    # fig.show()

    init_day = 10

    input = generator.generate_initialization_input(event_calendar, init_day=init_day)
    patients_dataframe = generator.export_to_xlsx(input, 1)

    perform_initialization("input/INS1.xlsx", "output/SLN1.xlsx")

    post_init = generator.generate_post_init_input(event_calendar, init_day=init_day)
    B = 1 # number of batches to consider after initialization

    team_patients_map = {team: [] for team in range(0, input["teams"])}
    patients_service_times = {}

    def update_capacities(previous_batch_solution, batch_to_optimize):
        assigned_workloads = previous_batch_solution["Work load"]
        for team in range(0, batch_to_optimize["teams"]):
            available_workload = 1500 - sum(assigned_workloads.iloc[team, :].values.flatten().tolist())
            for patient in batch_to_optimize["previous_batch_dismissed"]:
                if patient in team_patients_map[team]:
                    available_workload += patients_service_times[patient]
            batch_to_optimize["capacity"][team] = available_workload

    def update_maps(batch_solution):
        for team in team_patients_map:
            assigned_patients = list(filter(lambda x: not isnan(x), batch_solution["Operator list"])) # solver ids, they represent line number in sorted input dataframe
            assigned_patients = list(map(lambda x: int(x), assigned_patients)) # pandas loaded them as fp numbers
            for solution_row in assigned_patients:
                patient_id = int(patients_dataframe.iloc[solution_row]["ID"])
                team_patients_map[team].append(patient_id)
                patients_service_times[patient_id] = patients_dataframe.iloc[solution_row]["Treatments_per_week"] * patients_dataframe.iloc[solution_row]["Service_time"]

    for post_init_batch in range(1, B + 1):

        previous_batch_solution = read_excel("output/SLN" + str(post_init_batch) + ".xlsx", sheet_name=None, header=None)
        update_maps(previous_batch_solution)
        update_capacities(previous_batch_solution, post_init[post_init_batch])

        patients_dataframe = generator.export_to_xlsx(post_init[post_init_batch], post_init_batch + 1)

        # call post-optimization script on newly generated input INS_B
