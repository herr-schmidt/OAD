from generator.instance_generator import OADInstanceGenerator
import pprint
import plotly.express as px

if __name__ == "__main__":
    generator = OADInstanceGenerator(seed=58492)
    instance = generator.generate_instance(timespan=90,
                                           treatments_number_range=(2, 5),
                                           treatment_days_range=(5, 30),
                                           patients_per_day_range=(18, 20))

    pprint.pp(instance, indent=4)

    # visual intuition
    heatmap = [[] for _ in instance.keys()]
    i = 0
    for address in instance.keys():
        for day in instance[address].keys():
            if instance[address][day] == {}:
                heatmap[i].append(3)
            elif "DIMISSIONE" in instance[address][day]:
                heatmap[i].append(0)
            elif "PRESAINCARICO" in instance[address][day]:
                heatmap[i].append(1)
            else:
                heatmap[i].append(2)
        i += 1

    fig = px.imshow(heatmap)
    fig.show()