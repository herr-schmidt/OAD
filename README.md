# OAD
OAD project. For now it contains the instance generator.

## Instance generator
The instance generator allows for generating a plan of given temporal span. The generator works "by rows".

### Class `OadInstanceGenerator`

Constructor arguments:

- `seed`: seed for underlying random number generator, in order to ensure replicability. Defaults to `781015`.

Methods:

- *`generate_instance(self, timespan, treatments_number_range, treatment_days_range, patients_per_day_range)`*

Parameters
   - `timespan`: length in days for the generated instance. Defaults to `100`.
   - `treatments_number_range`: tuple representing the interval from which the number of daily treatments for a given patient is sampled. Defaults to `(2, 5)`.
   - `treatment_days_range`: tuple representing the interval from which the number of treatment days for a given patient is sampled. Defaults to `(5, 30)`.
   - `pattern_mask_size`: size of the list used for defining the care days (which will be randomly generated, with at least 1 day of care per mask). Defaults to `5` (i.e. the working week). For each day in the mask, the probability of having a care is set to `1 / 2`.
   - `take_in_charge_probability`: probability of having a take_in_charge event on a given day. If a take_in_charge event takes place, then the corresponding care plan is generated until dismission. After that, a new take_in_charge event may be extracted. Defaults to `1 / 25`.

   Returns: `instance`.
   
   Return type: `dict`.
   
The following example illustrates the usage of `OADInstanceGenerator` in order to generate an instance:

```code
generator = OADInstanceGenerator(seed=58492)
timespan = 100
instance = generator.generate_instance(timespan=timespan,
                                       treatments_number_range=(2, 5),
                                       treatment_days_range=(5, 30),
                                       pattern_mask_size=5,
                                       take_in_charge_probability=1/18)
```

The generated instance corresponds to the following chart.

![img](./sample_planning.png)