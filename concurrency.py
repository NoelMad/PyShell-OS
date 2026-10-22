import threading
import queue
import time

class ConcurrentJob:
    def __init__(self, job_id, name, duration):
        self.job_id = job_id
        self.name = name
        self.duration = duration

class JobDispatcher:
    def __init__(self, num_workers=2):
        self.job_queue = queue.Queue()
        self.num_workers = num_workers
        self.lock = threading.Lock()
        self.workers = []
        self.results_log = []
        self.running = False

    def worker_task(self, worker_id):
        """Worker thread function that pulls jobs from the shared queue safely."""
        while self.running:
            try:
                # Fetch job with a timeout so threads can exit gracefully
                job = self.job_queue.get(timeout=0.5)
            except queue.Empty:
                continue

            # Safe access to shared output resources using a Lock
            with self.lock:
                print(f"\n[Worker {worker_id}] Started executing {job.name} (Duration: {job.duration}s)")

            # Simulate execution time outside critical sections where appropriate
            time.sleep(job.duration)

            # Safely update shared results log
            with self.lock:
                print(f"[Worker {worker_id}] Finished {job.name}")
                self.results_log.append(f"{job.name} completed by Worker {worker_id}")

            self.job_queue.task_done()

    def start_workers(self):
        """Starts worker threads."""
        self.running = True
        self.results_log = []
        self.workers = []
        for i in range(1, self.num_workers + 1):
            t = threading.Thread(target=self.worker_task, args=(i,))
            t.daemon = True
            t.start()
            self.workers.append(t)

    def add_jobs(self, jobs):
        """Adds jobs to the shared job queue."""
        for job in jobs:
            self.job_queue.put(job)

    def run_simulation(self, jobs):
        """Starts workers, populates the queue, waits for completion, and stops."""
        print(f"Initializing Shared Job Queue with {len(jobs)} jobs across {self.num_workers} worker threads...\n")
        self.start_workers()
        self.add_jobs(jobs)
        
        # Wait until all jobs in the queue have been processed
        self.job_queue.join()
        
        # Stop worker threads cleanly
        self.running = False
        print("\nAll concurrent jobs finished successfully!")