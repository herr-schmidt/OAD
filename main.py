from generator.instance_generator import OADInstanceGenerator

if __name__ == "__main__":
    generator = OADInstanceGenerator(seed=58492)
    instance = generator.generate_instance(patients=10)

    for patient in instance:
        print(patient)
