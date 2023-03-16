# OAD
OAD project. For now it contains the instance generator.

## Instance generator
The instance generator allows the generation of an event calendar, i.e. a calendar of a given timespan containing information about take-in-charge and dismission events. On the rows we represent the addresses, whereas columns represent days in the chosen timespan. The event calendar generator works "by rows". Starting from the generated calendar, it is possible to compute an input for our model, possibly from a sub-calendar of the original event calendar.

### Class `OadInstanceGenerator`

Class used for generating an event calendar and an input for the OAD model.

- `seed`: seed for underlying random number generator, in order to ensure replicability. Defaults to `781015`.

Methods:

- *`generate_events_calendar(self, timespan, treatment_span_range, take_in_charge_probability)`*

Args:
   - timespan (int, optional): Length of the calendar horizon. Defaults to `30`.
   - treatment_span_range (tuple, optional): Extremes of the interval from which the distance take_in_charge--dismission is sampled. Defaults to `(5, 30)`.
   - take_in_charge_probability (float, optional): Probability of having a take-in-charge event on any given day. Defaults to `1/25`.

Returns: A dict containing information about take-in-charge and dismission events for each address and each day in the horizon.
   
Return type: `dict[str, dict[int, dict[int, int]]]`.
   
- *`generate_input(self, calendar, first_day, last_day, treatments_number_range)`*

Args:
   - calendar (dict): Event calendar with take-in-charge and dismission events.
   - first_day (int): First day from which input is generated from the event calendar.
   - last_day (int): Day following the last from which input is generated from the event calendar.
   - treatments_number_range (tuple, optional): Interval `[a, b)` from which the number of daily treatments for each patients is sampled. Defaults to `(2, 5)`.

Returns: A dict containing the parameters for the model.

Return type: `dict`.

### Usage examples

The following example illustrates the usage of `OADInstanceGenerator` in order to generate an event calendar:

```code
    generator = OADInstanceGenerator(seed=58492)
    timespan = 100
    event_calendar = generator.generate_events_calendar(timespan=timespan,
                                                        treatment_span_range=(5, 30))
```

The generated events' calendar corresponds to the following chart.

![img](./sample_planning.png)

Suppose we want to generate the an input from the events' calendar, from day 0 (included) until day 10 (excluded), i.e. an input based on 10 days. Then the following code would do what we need:

```code
    solver_input_dict = generator.generate_input(event_calendar, first_day=0, last_day=10)
```

### Generated input description

As previously said, the generated input for our model consists in a python dict (a hash table). In the following the meaning of its content is explained.

For starters, at the highest level our dict can be accessed by using the following keys (enclosed in "" being them strings):

- `"take_in_charge"`: its associated value consists in a dict with the structure `<patient_id, take_in_charge_day>`. If in the considered window a patient has no take-in-charge, but has a dismission, then the corresponding entry for that patient in the dict will be equal to `-1`.
                
- `"dismission"`: same meaning as for `"take_in_charge"`, but for dismission days.

- `"treatments_per_week"`: its associated value consists in a dict with the structure `<patient_id, treatments_per_week>`. The integer value `treatments_per_week` represents the number of days each patient should be visited during the working week (5 days).

- `"procedures"`: its associated value consists in a dict with the structure `<patient_id, <procedure_id, procedure_time>>`. Notice that `<procedure_id, procedure_time>` is itself a dict.

- `"daily_treatments_duration"`: its associated value consists in a dict with the structure `<patient_id, daily_treatments_duration>`. The integer value `daily_treatments_duration` represents the sum of the service times associated to each one of patient `patient_id`'s procedures on any given care day (we assume the set of treatments to be fixed for any patient).

- `"addresses"`: its associated value consists in a dict with the structure `<patient_id, address>`.

- `"average_distances"`: its associated value consists in a dict with the structure `<patient_id, average_distance>`. The float value `average_distance` is computed as the $\tau_j$ parameter, with the exception that - for now - it does not take into account the starting point of the teams, but only patients' nodes.

- `"skills"`: its associated value consists in a dict with the structure `<procedure_id, <team_id, skill_flag>>`. The binary value `skill_flag` can take value `1` or `0`, depending on whether team `team_id` is able to perform procedure `procedure_id`.

- `"patients"`: its associated value consists in the number of patients in the considered window.

- `"teams"`: its associated value consists in the number of teams, which should be a constant in our setting (equal to `9`).
                
The following is an example of an actual generated input, which may help in better understanding the description given so far.

```code
{'take_in_charge': {1: 20,
                    4: 14,
                    6: 18,
                    8: 15,
                    9: 11,
                    11: 18,
                    12: 13,
                    13: 11,
                    14: 13,
                    16: 17,
                    18: 20,
                    19: 14,
                    2: -1,
                    3: -1,
                    5: -1,
                    7: -1,
                    10: -1,
                    15: -1,
                    17: -1},
 'dismission': {2: 17,
                3: 19,
                5: 12,
                7: 13,
                10: 19,
                12: 19,
                13: 17,
                15: 20,
                17: 12,
                1: -1,
                4: -1,
                6: -1,
                8: -1,
                9: -1,
                11: -1,
                14: -1,
                16: -1,
                18: -1,
                19: -1},
 'treatments_per_week': {1: 3,
                         2: 4,
                         3: 1,
                         4: 1,
                         5: 3,
                         6: 1,
                         7: 3,
                         8: 1,
                         9: 2,
                         10: 1,
                         11: 4,
                         12: 3,
                         13: 5,
                         14: 4,
                         15: 2,
                         16: 4,
                         17: 5,
                         18: 3,
                         19: 1},
 'procedures': {1: {13: 40, 6: 5, 2: 20, 1: 20},
                2: {4: 40, 2: 20, 8: 5},
                3: {7: 5, 4: 40},
                4: {7: 5, 9: 15, 3: 10},
                5: {14: 10, 10: 15},
                6: {9: 15, 8: 5, 1: 20},
                7: {12: 10, 3: 10, 14: 10},
                8: {12: 10, 4: 40, 1: 20},
                9: {8: 5, 4: 40, 12: 10, 15: 15},
                10: {8: 5, 12: 10},
                11: {13: 40, 8: 5, 7: 5},
                12: {2: 20, 16: 20},
                13: {15: 15, 2: 20, 9: 15},
                14: {14: 10, 12: 10},
                15: {8: 5, 9: 15, 3: 10},
                16: {13: 40, 3: 10},
                17: {7: 5, 3: 10},
                18: {7: 5, 3: 10},
                19: {9: 15, 12: 10, 8: 5, 2: 20}},
 'daily_treatments_duration': {1: 85,
                               2: 65,
                               3: 45,
                               4: 30,
                               5: 25,
                               6: 40,
                               7: 30,
                               8: 70,
                               9: 70,
                               10: 15,
                               11: 50,
                               12: 40,
                               13: 50,
                               14: 20,
                               15: 30,
                               16: 50,
                               17: 15,
                               18: 15,
                               19: 50},
 'addresses': {1: 'Corso Maroncelli 35',
               2: 'Via San Pio V 34',
               3: 'Via Enrico Dandolo 21',
               4: 'Largo Saluzzo 36',
               5: 'Via Ventimiglia 18',
               6: 'Piazza Bengasi 26',
               7: 'Via Buenos Aires 4',
               8: 'Via Buenos Aires 4',
               9: 'Via Vigliani 89',
               10: 'Strada dei Tadini 5',
               11: 'Strada degli Alberoni 12',
               12: 'Strada degli Alberoni 12',
               13: 'Via Fratelli Garrone 37',
               14: 'Via San Secondo 53',
               15: 'Via Madama Cristina 88',
               16: 'Via Rubino 18',
               17: 'Corso Salvemini 3',
               18: 'Corso Moncalieri 271',
               19: 'Via Paolo Braccini 1'},
 'average_distances': {1: 9.30675,
                       2: 10.179250000000003,
                       3: 10.383750000000001,
                       4: 10.073937500000001,
                       5: 8.8743125,
                       6: 9.5170625,
                       7: 9.128312499999998,
                       8: 9.128312499999998,
                       9: 10.501187499999999,
                       10: 13.69025,
                       11: 10.134125000000001,
                       12: 10.134125000000001,
                       13: 11.1081875,
                       14: 9.7769375,
                       15: 8.754187499999999,
                       16: 46.9391875,
                       17: 11.511000000000003,
                       18: 9.4306875,
                       19: 10.322750000000001},
 'skills': {1: {1: 1, 2: 1, 3: 1, 4: 1, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0},
            17: {1: 1, 2: 1, 3: 1, 4: 1, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0},
            2: {1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1, 8: 0, 9: 0},
            18: {1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1, 8: 0, 9: 0},
            3: {1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1, 8: 0, 9: 1},
            4: {1: 1, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 1, 9: 0},
            5: {1: 1, 2: 1, 3: 1, 4: 0, 5: 1, 6: 0, 7: 0, 8: 0, 9: 0},
            6: {1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1, 8: 0, 9: 1},
            7: {1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1, 8: 0, 9: 1},
            8: {1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1, 8: 0, 9: 1},
            9: {1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1, 8: 0, 9: 1},
            10: {1: 1, 2: 1, 3: 1, 4: 1, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0},
            11: {1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1, 8: 0, 9: 0},
            12: {1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1, 8: 0, 9: 1},
            13: {1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1, 8: 0, 9: 1},
            14: {1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1, 8: 0, 9: 1},
            15: {1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1, 8: 0, 9: 1},
            16: {1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1, 8: 0, 9: 1}},
 'patients': 19,
 'teams': 9}
 ```