from agent import verify_and_fetch_dataset
import time

# The files we just registered
files_to_measure = ['data_1MB', 'data_10MB', 'data_50MB']

print("--- RUNNING SCALING EXPERIMENT (VERIFICATION) ---")
results = {}

for unique_id in files_to_measure:
    print(f"\n--- Measuring '{unique_id}' ---")

    # Start the timer
    start_time = time.time()

    verified_path = verify_and_fetch_dataset(unique_id, save_as=f"verified_{unique_id}.dat")

    # Stop the timer
    end_time = time.time()

    if verified_path:
        latency = (end_time - start_time) * 1000  # Convert to milliseconds
        results[unique_id] = latency
        print(f"  - SUCCESS: Verified in {latency:.2f} ms")
    else:
        print(f"  - FAILED: Could not verify {unique_id}")
        results[unique_id] = -1

print("\n--- FINAL LATENCY RESULTS ---")
print("File ID | Latency (ms)")
print("-------------------------")
for unique_id, latency in results.items():
    print(f"{unique_id.ljust(8)}| {latency:.2f} ms")