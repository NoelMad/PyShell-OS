import threading
import queue
import time
import random

def producer(q, num_items=5):
    """Producer thread that generates numbers and puts them into the shared queue."""
    print("[Producer] Starting item generation...")
    for i in range(1, num_items + 1):
        item = random.randint(10, 99)
        print(f"[Producer] Generated number {item} -> Putting in Queue")
        q.put(item)
        time.sleep(0.4)
    
    # Send a sentinel value (None) to signal the consumer that production is done
    q.put(None)
    print("[Producer] Finished generating all items.")

def consumer(q):
    """Consumer thread that retrieves and processes numbers from the shared queue."""
    print("[Consumer] Ready to process items from Queue...")
    while True:
        item = q.get()
        
        # Check for sentinel value to exit safely
        if item is None:
            q.task_done()
            break
            
        print(f"[Consumer] <- Retrieved {item} from Queue. Processing...")
        time.sleep(0.7)  # Simulate processing time
        print(f"[Consumer] Successfully processed number: {item}")
        q.task_done()
        
    print("[Consumer] Finished processing all items.")

def run_pipeline():
    """Orchestrates the Producer-Consumer queue pipeline simulation."""
    # Shared queue with a bounded buffer size of 3
    q = queue.Queue(maxsize=3)
    
    print("=== Producer-Consumer Pipeline Simulation ===")
    print("Producer → Shared Queue (Buffer Size: 3) → Consumer\n")

    # Create threads for Producer and Consumer
    prod_thread = threading.Thread(target=producer, args=(q, 5))
    cons_thread = threading.Thread(target=consumer, args=(q,))

    # Start execution
    prod_thread.start()
    cons_thread.start()

    # Wait for both threads to finish
    prod_thread.join()
    cons_thread.join()

    print("\nPipeline execution finished successfully!")