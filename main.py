from generator.instance_generator import OADInstanceGenerator
import pprint
import plotly.express as px
from plotly import graph_objects as go

if __name__ == "__main__":
    generator = OADInstanceGenerator(seed=58492)
    timespan = 100
    instance = generator.generate_instance(timespan=timespan,
                                           treatments_number_range=(2, 5),
                                           treatment_days_range=(5, 30),
                                           pattern_mask_size=5,
                                           take_in_charge_probability=1/18)

    # pprint.pp(instance, indent=4)

    # visual intuition
    heatmap_matrix = [[] for _ in instance.keys()]
    i = 0
    for address in instance.keys():
        for day in instance[address].keys():
            if instance[address][day] == {}:
                heatmap_matrix[i].append(3)
            elif "DIMISSIONE" in instance[address][day]:
                heatmap_matrix[i].append(0)
            elif "PRESAINCARICO" in instance[address][day]:
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

    fig.show()
