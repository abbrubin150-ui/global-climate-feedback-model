import numpy as np

STEFAN_BOLTZMANN = 5.67e-8
LATENT_HEAT_VAPORIZATION = 2.5e6
WATER_DENSITY = 1000
SECONDS_PER_DAY = 86400

class GridCell:
    """
    תא רשת בודד: אנרגיה, מים, צמחייה (אב-טיפוס).
    """
    def __init__(self, lat, lon, land_type='desert', effective_soil_depth=1.0):
        self.latitude = lat
        self.longitude = lon
        self.land_type = land_type
        self.effective_soil_depth = effective_soil_depth

        # מצב
        self.ts = 298.15       # K
        self.q = 0.005         # kg/kg
        self.w = 0.10          # m3/m3
        self.lai = 0.10        # m2/m2
        self.veg_carbon = 5.0  # kgC/m2

        self.update_parameters()

    # פרמטרים תלויי-מצב
    def update_parameters(self):
        self.albedo = float(np.clip(0.35 - 0.2 * (self.lai / 5.0), 0.08, 0.45))
        self.c_eff = 2.5e6
        self.soil_capacity = 0.40

    # חישוב שטפים
    def calculate_fluxes(self, solar_rad, wind_speed):
        emissivity = 0.95 + 0.05 * self.lai
        olr = emissivity * STEFAN_BOLTZMANN * (self.ts**4)

        potential_et = max(0.0, solar_rad * 1e-4 * (1 + self.lai) * max(0.0, self.ts - 280.0) / 15.0)
        actual_et_m_per_s = potential_et * self.w * 2e-8  # פשטני

        evaporation_kg_per_s = actual_et_m_per_s * WATER_DENSITY
        latent_heat = evaporation_kg_per_s * LATENT_HEAT_VAPORIZATION

        sensible_heat = (self.ts - 295.0) * 10.0  # פשטני

        return olr, latent_heat, sensible_heat, actual_et_m_per_s

    # צעד יומי מקומי
    def run_daily_local_step(self, solar_rad, precipitation_mm, wind_speed, irrigation_mm=0.0):
        olr, lat_h, sens_h, et_m_s = self.calculate_fluxes(solar_rad, wind_speed)
        net_rad = solar_rad * (1.0 - self.albedo)
        dTs_dt = (net_rad - olr - lat_h - sens_h) / self.c_eff
        self.ts += dTs_dt * SECONDS_PER_DAY

        # מים
        p_m_s = (precipitation_mm / 1000.0) / SECONDS_PER_DAY
        i_m_s = (irrigation_mm / 1000.0) / SECONDS_PER_DAY
        runoff = p_m_s * (self.w / self.soil_capacity)**2
        drainage = (self.w / self.soil_capacity)**4 * 1e-7
        dW_dt = p_m_s + i_m_s - et_m_s - runoff - drainage
        self.w += (dW_dt * SECONDS_PER_DAY) / self.effective_soil_depth
        self.w = float(np.clip(self.w, 0.01, self.soil_capacity))

        # צמחייה/פחמן
        growth_factor = np.clip((self.ts - 280.0) / 20.0, 0.0, 1.0) * self.w
        npp = solar_rad * growth_factor * 1e-4
        respiration = self.veg_carbon * 1e-3 * ((max(0.0, self.ts - 273.15))/30.0)**2
        dC = npp - respiration
        self.veg_carbon = max(0.0, self.veg_carbon + dC)
        self.lai = max(0.0, self.veg_carbon * 0.5)

        self.update_parameters()

    def __repr__(self):
        return f"Cell({self.latitude:.2f},{self.longitude:.2f}) Ts={self.ts-273.15:.2f}C q={self.q:.4f}"
