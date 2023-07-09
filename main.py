from generator.instance_generator import OADInstanceGenerator
import pprint
import plotly.express as px
from plotly import graph_objects as go
from generator.data import Procedures
from initialization import perform_initialization
from pandas import read_excel

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
    generator.export_to_xlsx(input, 1)

    perform_initialization("input/INS1.xlsx")

    post_init = generator.generate_post_init_input(event_calendar, init_day=init_day)
    B = 8 # number of batches to consider after initialization
    for post_init_batch in range(1, B + 1):

        # previous_batch_solution = read_excel("output/SLN1.xlsx", sheet_name=None, header=None)
        # TODO: update capacities according to the patients who left in previous batch

        generator.export_to_xlsx(post_init[post_init_batch], post_init_batch + 1)

        # call post-optimization script on newly generated input INS_B