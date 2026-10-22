import subprocess
import sys
from scheduler import Scheduler
from concurrency import JobDispatcher, ConcurrentJob
from pipeline import run_pipeline
from memory import ToyAllocator, get_real_memstat
from filesystem import SimulatedFileSystem

# Initialize OS Subsystems
os_scheduler = Scheduler(policy="FCFS")
buffer_pool = ToyAllocator(total_blocks=5)
fs = SimulatedFileSystem(total_blocks=100)

# Job table to track background processes & link with FS/Memory
job_table = {}
next_job_id = 1

# Keep the shell running until the user chooses "exit"
while True:
    try:
        command = input("PyShell OS> ")
    except (KeyboardInterrupt, EOFError):
        print()
        continue

    # If the user types an empty command, show the prompt again
    if command.strip() == "":
        continue

    # Split command into parts for argument checking
    parts = command.strip().split()
    if not parts:
        continue
    
    cmd_lower = parts[0].lower()

    # If the user types "help", show available commands
    if cmd_lower == "help":
        print("Available commands:")
        print("  help                - Show this help message")
        print("  exit                - Exit the shell")
        print("  jobs                - List background jobs")
        print("  kill <job_id>       - Terminate a background job")
        print("  fg <job_id>         - Bring a background job to the foreground")
        print("  schedule            - Run the CPU scheduler simulation")
        print("  policy <policy>     - View or set policy (FCFS, RR, PRIORITY)")
        print("  concurrency         - Run multi-job concurrent execution simulation")
        print("  pipeline            - Run Producer-Consumer pipeline simulation")
        print("  memstat             - Show real memory usage of jobs")
        print("  pool                - Interact with the toy memory buffer allocator")
        print("  fs                  - Display simulated filesystem tree")
        print("  fsstat              - Show filesystem statistics")
        print("  cat <path>          - Read a file from the simulated filesystem")
        print("  <cmd> &             - Run command in the background")
        continue

    # If the user types "exit", stop the loop
    if cmd_lower == "exit":
        print("Goodbye!")
        break

    # Handle "schedule" command
    if cmd_lower == "schedule":
        results = os_scheduler.schedule()
        print(f"Scheduling policy: {os_scheduler.policy}\n")
        for job in results:
            print(f"{job.name}")
            print(f"Wait time: {job.wait_time:.2f}s")
            print(f"Turnaround: {job.turnaround_time:.2f}s\n")
        continue

    # Handle "policy" command
    if cmd_lower == "policy":
        if len(parts) > 1:
            new_policy = parts[1].upper()
            if new_policy in ["FCFS", "RR", "ROUND ROBIN", "PRIORITY"]:
                os_scheduler.set_policy(new_policy)
                print(f"Scheduling policy updated to: {os_scheduler.policy}")
            else:
                print("Invalid policy. Choose from: FCFS, RR, PRIORITY")
        else:
            print(f"Current scheduling policy: {os_scheduler.policy}")
        continue

    # Handle "concurrency" command
    if cmd_lower == "concurrency":
        sample_jobs = [
            ConcurrentJob(1, "Job 1", duration=1.5),
            ConcurrentJob(2, "Job 2", duration=1.0),
            ConcurrentJob(3, "Job 3", duration=2.0),
            ConcurrentJob(4, "Job 4", duration=1.2)
        ]
        dispatcher = JobDispatcher(num_workers=2)
        dispatcher.run_simulation(sample_jobs)
        continue

    # Handle "pipeline" command
    if cmd_lower == "pipeline":
        run_pipeline()
        continue

    # Handle "memstat" command (Memory Subsystem Integration)
    if cmd_lower == "memstat":
        stats = get_real_memstat(job_table)
        print(f"{'Job':<10} {'PID':<8} {'Memory':<10}")
        print("-" * 30)
        for stat in stats:
            print(f"{stat['name']:<10} {stat['pid']:<8} {stat['memory']:<10}")
        continue

    # Handle "pool" command (Toy Allocator Subsystem)
    if cmd_lower == "pool":
        print("Output Buffer Pool:")
        print(buffer_pool.get_status_string())
        print("\nCommands: pool alloc  OR  pool free <index_0_to_4>")
        
        if len(parts) > 1:
            action = parts[1].lower()
            if action == "alloc":
                idx = buffer_pool.allocate()
                if idx is not None:
                    print(f"Successfully allocated block at index {idx}")
                else:
                    print("Allocation failed: Buffer Pool is FULL!")
                print(f"New Pool State: {buffer_pool.get_status_string()}")
            elif action == "free" and len(parts) > 2:
                try:
                    idx = int(parts[2])
                    if buffer_pool.free(idx):
                        print(f"Successfully freed block at index {idx}")
                    else:
                        print("Invalid block index.")
                    print(f"New Pool State: {buffer_pool.get_status_string()}")
                except ValueError:
                    print("Invalid index. Usage: pool free <index>")
        continue

    # Handle "fs" command
    if cmd_lower == "fs":
        fs.print_tree()
        continue

    # Handle "fsstat" command (Filesystem Subsystem Integration)
    if cmd_lower == "fsstat":
        stats = fs.get_stats()
        print(f"Files: {stats['files']}")
        print(f"Directories: {stats['directories']}")
        print(f"Used blocks: {stats['used_blocks']}")
        print(f"Free blocks: {stats['free_blocks']}")
        continue

    # Handle "cat <path>" command
    if cmd_lower == "cat" and len(parts) > 1:
        filepath = parts[1]
        content = fs.read_file(filepath)
        if content is not None:
            print(content)
        else:
            print(f"File not found or is a directory: {filepath}")
        continue

    # Handle "jobs" command
    if command.strip() == "jobs":
        print("Job ID | PID   | Command            | Status")
        print("-" * 50)
        for jid, job_info in list(job_table.items()):
            proc = job_info["process"]
            ret = proc.poll()
            status = "Running" if ret is None else f"Done ({ret})"
            print(f"{jid:<6} | {proc.pid:<5} | {job_info['cmd']:<18} | {status}")
        continue

    # Handle "kill <job_id>" command
    if cmd_lower == "kill" and len(parts) > 1:
        try:
            target_id = int(parts[1])
            if target_id in job_table:
                job_table[target_id]["process"].terminate()
                print(f"Job {target_id} terminated.")
            else:
                print(f"Job {target_id} not found.")
        except ValueError:
            print("Invalid Job ID. Usage: kill <job_id>")
        continue

    # Handle "fg <job_id>" command
    if cmd_lower == "fg" and len(parts) > 1:
        try:
            target_id = int(parts[1])
            if target_id in job_table:
                job_info = job_table[target_id]
                proc = job_info["process"]
                if proc.poll() is not None:
                    print(f"Job {target_id} has already finished.")
                    del job_table[target_id]
                else:
                    print(f"Bringing job {target_id} ({job_info['cmd']}) to foreground...")
                    proc.wait()
                    print(f"Job {target_id} finished.")
                    del job_table[target_id]
            else:
                print(f"Job {target_id} not found.")
        except ValueError:
            print("Invalid Job ID. Usage: fg <job_id>")
        continue

    # Check if the command should run in the background (&)
    is_background = False
    if parts[-1] == "&":
        is_background = True
        parts = parts[:-1]

    # Run regular or background command via OS Subsystems (Job System + Filesystem Log Integration)
    try:
        if is_background:
            proc = subprocess.Popen(parts)
            job_table[next_job_id] = {
                "process": proc,
                "cmd": " ".join(parts)
            }
            
            # OS Integration: Automatically save a job log in the simulated filesystem!
            log_path = f"/job_logs/job{next_job_id}"
            log_content = f"Command: {' '.join(parts)}\nPID: {proc.pid}\nStatus: Running"
            fs.write_file(log_path, log_content)

            print(f"Job #{next_job_id} created (PID: {proc.pid}) -> Log saved to {log_path}")
            next_job_id += 1
        else:
            subprocess.run(parts)

    except FileNotFoundError:
        print(f"Command not found: {parts[0]}")
    except Exception as e:
        print(f"An error occurred: {e}")