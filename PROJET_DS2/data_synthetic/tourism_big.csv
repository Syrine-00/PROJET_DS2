import pandas as pd
import random
from datetime import datetime, timedelta

regions = ["Tunis", "Sousse", "Hammamet", "Djerba", "Monastir"]
hotels = ["Hotel A", "Hotel B", "Hotel C", "Hotel D"]

start_date = datetime(2024, 1, 1)

data = []

for i in range(365):  # 1 année
    date = start_date + timedelta(days=i)

    for region in regions:
        for hotel in hotels:

            # saison (été plus touristique)
            if date.month in [6, 7, 8]:
                occupancy = random.uniform(0.7, 0.95)
            else:
                occupancy = random.uniform(0.5, 0.8)

            bookings = random.randint(80, 200)
            cancellations = random.randint(5, 20)
            revenue = bookings * random.randint(80, 150)

            data.append([
                region,
                hotel,
                date.strftime("%Y-%m-%d"),
                round(occupancy, 2),
                bookings,
                cancellations,
                revenue
            ])

df = pd.DataFrame(data, columns=[
    "region", "hotel_name", "date",
    "occupancy_rate", "bookings",
    "cancellations", "revenue"
])

df.to_csv("data_synthetic/tourism_big.csv", index=False)

print("Dataset généré ✔")
