# OAD
OAD project. For now it contains the instance generator.

## Instance generator
The instance generator allows for generating a plan of given temporal span.

### Class `OadInstanceGenerator`

Constructor arguments:

- `seed`: seed for underlying random number generator, in order to ensure replicability. Defaults to `781015`.

Methods:

- *`generate_instance(self, timespan, treatments_number_range, treatment_days_range, patients_per_day_range)`*

Parameters
   - `timespan`: length in days for the generated instance. Defaults to `100`.
   - `treatments_number_range`: tuple representing the extremes values allowed for the interval from which the number of daily treatments for a given patient is sampled. Defaults to `(2, 5)`.
   - `treatment_days_range`: tuple representing the extremes values allowed for the interval from which the number of treatment days for a given patient is sampled. Defaults to `(5, 30)`.
   - `patients_per_day_range`: tuple representing the extremes values allowed for the interval from which the number of daily treated patients is sampled. Defaults to `(18,25)`.

   Returns: `instance`.
   
   Return type: `dict`.
   
The following example illustrates the usage of `OADInstanceGenerator` in order to generate an instance:

```code
generator = OADInstanceGenerator(seed=58492)
instance = generator.generate_instance(timespan=100,
                                       treatments_number_range=(2, 5),
                                       treatment_days_range=(5, 20),
                                       patients_per_day_range=(18, 25))
```

The generated instance corresponds to the following chart.

![img](./sample_planning.png)