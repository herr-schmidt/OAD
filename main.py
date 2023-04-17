from generator.instance_generator import OADInstanceGenerator
import pprint
import plotly.express as px
from plotly import graph_objects as go
from generator.data import Procedures

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

    solver_input_dict = generator.generate_input(event_calendar, first_day=0, last_day=50)
    # pprint.pp(solver_input_dict)

    generator.export_to_csv(solver_input_dict, input_size=60)