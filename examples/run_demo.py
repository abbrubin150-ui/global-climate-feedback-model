import numpy as np
from climodel import ClimateModel

def main():
    model = ClimateModel(grid_size=(10, 20))
    # כתם לחות במערב
    model.inject_moisture_patch(slice(3,7), slice(2,5))
    print("מצב התחלתי (q):")
    print(np.round((model.q_grid()-0.005)*2000).clip(0,9).astype(int))

    print("\nמתחילים 5 ימי סימולציה עם רוח מערבית...")
    model.run(days=5, verbose=True)

    print("\nסיום. שים לב לתנועת הכתם מזרחה.")

if __name__ == "__main__":
    main()
