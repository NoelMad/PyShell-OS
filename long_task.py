import time

print("Long task starting...")
for i in range(5):  # Runs for 5 seconds
    print(f"Working... {i}")
    time.sleep(1)
print("Long task finished!")