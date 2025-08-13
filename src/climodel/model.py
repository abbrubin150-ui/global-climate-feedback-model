import numpy as np
from .gridcell import GridCell, SECONDS_PER_DAY

class ClimateModel:
    """
    מודל אקלים מרחבי פשוט: רשת תאים + הסעת לחות (q) בשיטת upwind.
    """
    def __init__(self, grid_size=(10, 20), dx=10000.0, dy=10000.0, default_cell_kwargs=None):
        self.grid_size = grid_size
        self.dx = dx
        self.dy = dy
        self.grid = np.empty(grid_size, dtype=object)

        kwargs = default_cell_kwargs or {}
        for i in range(grid_size[0]):
            for j in range(grid_size[1]):
                self.grid[i, j] = GridCell(lat=float(i), lon=float(j), **kwargs)

        # שדות רוחות (u,v) במ/ש
        self.u = np.full(grid_size, 5.0)   # מערב→מזרח
        self.v = np.zeros(grid_size)       # צפון/דרום

        # נהגים גלובליים פשוטים (ניתן להחלפה בכל יום/תא)
        self.solar_rad = 300.0  # W/m^2
        self.precip_mm = 0.0
        self.irrigation_mm = 0.0

    def set_wind(self, u, v):
        self.u = np.array(u, dtype=float)
        self.v = np.array(v, dtype=float)

    def run_day_local(self):
        for i in range(self.grid_size[0]):
            for j in range(self.grid_size[1]):
                wind_speed = (self.u[i, j]**2 + self.v[i, j]**2)**0.5
                self.grid[i, j].run_daily_local_step(
                    self.solar_rad, self.precip_mm, wind_speed, irrigation_mm=self.irrigation_mm
                )

    def _advect_q_upwind(self):
        """
        הסעת לחות q — upwind מפושט, ללא דיפוזיה א ekspl.
        """
        q = np.array([[self.grid[i, j].q for j in range(self.grid_size[1])] for i in range(self.grid_size[0])], dtype=float)
        nq = q.copy()
        dt = SECONDS_PER_DAY

        # X-direction (u)
        for i in range(self.grid_size[0]):
            for j in range(self.grid_size[1]):
                u = self.u[i, j]
                if u > 0:
                    q_up = q[i, j-1] if j > 0 else q[i, j]
                else:
                    q_up = q[i, j+1] if j < self.grid_size[1]-1 else q[i, j]
                flux_x = u * (q[i, j] - q_up) / self.dx
                nq[i, j] -= dt * flux_x

        # Y-direction (v)
        q2 = nq.copy()
        for i in range(self.grid_size[0]):
            for j in range(self.grid_size[1]):
                v = self.v[i, j]
                if v > 0:
                    q_up = q2[i-1, j] if i > 0 else q2[i, j]
                else:
                    q_up = q2[i+1, j] if i < self.grid_size[0]-1 else q2[i, j]
                flux_y = v * (q2[i, j] - q_up) / self.dy
                nq[i, j] -= dt * flux_y

        # עדכון
        for i in range(self.grid_size[0]):
            for j in range(self.grid_size[1]):
                self.grid[i, j].q = float(max(0.0, nq[i, j]))

    def inject_moisture_patch(self, i_slice, j_slice, q_values=(0.015, 0.025, 0.015)):
        """
        הזרקת "כתם לחות" לצורך הדמה.
        """
        for i in range(i_slice.start, i_slice.stop):
            for k, j in enumerate(range(j_slice.start, j_slice.stop)):
                if 0 <= i < self.grid_size[0] and 0 <= j < self.grid_size[1]:
                    self.grid[i, j].q = float(q_values[min(k, len(q_values)-1)])

    def q_grid(self):
        return np.array([[self.grid[i, j].q for j in range(self.grid_size[1])] for i in range(self.grid_size[0])], dtype=float)

    def run(self, days, verbose=False):
        for day in range(days):
            self.run_day_local()
            self._advect_q_upwind()
            if verbose:
                print(f"--- Day {day+1} ---")
                print(np.round((self.q_grid()-0.005)*2000).clip(0,9).astype(int))
