import time

class Job:
    def __init__(self, job_id, name, burst_time, priority=1):
        self.job_id = job_id
        self.name = name
        self.burst_time = burst_time      # Simulated CPU burst time
        self.priority = priority           # Lower number = higher priority
        self.wait_time = 0.0
        self.turnaround_time = 0.0
        self.completion_time = 0.0

class Scheduler:
    def __init__(self, policy="FCFS", time_quantum=1.0):
        self.policy = policy.upper()
        self.time_quantum = time_quantum
        self.jobs = []
        self.reset_default_jobs()

    def reset_default_jobs(self):
        """Initializes the default 4 jobs for the milestone."""
        self.jobs = [
            Job(1, "Job 1", burst_time=2.0, priority=2),
            Job(2, "Job 2", burst_time=2.1, priority=1),
            Job(3, "Job 3", burst_time=1.5, priority=3),
            Job(4, "Job 4", burst_time=1.8, priority=2)
        ]

    def add_job(self, job):
        self.jobs.append(job)

    def set_policy(self, policy):
        self.policy = policy.upper()

    def schedule(self):
        """Executes scheduling based on the active policy."""
        if self.policy == "FCFS":
            return self._run_fcfs()
        elif self.policy in ("RR", "ROUND ROBIN"):
            return self._run_round_robin()
        elif self.policy == "PRIORITY":
            return self._run_priority()
        else:
            return self._run_fcfs()

    def _run_fcfs(self):
        """First-Come, First-Served Scheduling."""
        current_time = 0.0
        results = []
        
        for job in self.jobs:
            job.wait_time = current_time
            time.sleep(0.01)  # Simulate small CPU execution overhead
            current_time += job.burst_time
            job.turnaround_time = job.wait_time + job.burst_time
            results.append(job)
            
        return results

    def _run_round_robin(self):
        """Round Robin Scheduling with a time quantum."""
        queue = [Job(j.job_id, j.name, j.burst_time, j.priority) for j in self.jobs]
        remaining_bursts = {j.job_id: j.burst_time for j in queue}
        wait_times = {j.job_id: 0.0 for j in queue}
        completion_times = {j.job_id: 0.0 for j in queue}
        
        current_time = 0.0
        queue_list = list(queue)
        
        while queue_list:
            job = queue_list.pop(0)
            exec_time = min(remaining_bursts[job.job_id], self.time_quantum)
            
            # Accumulate wait time for jobs still in the queue
            for other in queue_list:
                wait_times[other.job_id] += exec_time
                
            time.sleep(0.01)
            current_time += exec_time
            remaining_bursts[job.job_id] -= exec_time
            
            if remaining_bursts[job.job_id] > 0:
                queue_list.append(job)
            else:
                completion_times[job.job_id] = current_time

        results = []
        for j in self.jobs:
            j.completion_time = completion_times[j.job_id]
            j.wait_time = wait_times[j.job_id]
            j.turnaround_time = j.wait_time + j.burst_time
            results.append(j)
            
        return results

    def _run_priority(self):
        """Priority Scheduling (lower number runs first)."""
        sorted_jobs = sorted(self.jobs, key=lambda j: j.priority)
        current_time = 0.0
        results = []
        
        for job in sorted_jobs:
            job.wait_time = current_time
            time.sleep(0.01)
            current_time += job.burst_time
            job.turnaround_time = job.wait_time + job.burst_time
            results.append(job)
            
        return results