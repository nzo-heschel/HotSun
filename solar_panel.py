from config_manager import ConfigGetter


class SolarPanel:
    def __init__(self, amount: int, efficiency: float, lifetime: int, decay_rate: float, config: dict):
        solar_config = config['solar']
        self.efficiency = solar_config['efficiency']
        self.lifetime = solar_config['lifetime']
        self.decay_rate = solar_config['decay_rate']
        self.area = solar_config['area']
        self.amount = amount

    def calc_energy_gen_hourly(self, radiation):
        # TODO: Calc pv production
        return self.amount * self.area * self.efficiency * radiation * 0.75  # 0.75 is a performance ratio
