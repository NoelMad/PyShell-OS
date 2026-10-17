import subprocess
import sys

# Job table to track background processes
# Format: job_id: {"process": Popen_object, "cmd": command_string}
job_table = {}
next_job_id = 1

# Keep the shell running until the user chooses "exit"
while True:
    try:
        command = input("PyShell> ")
    except (KeyboardInterrupt, EOFError):
        print()
        continue

    # If the user types an empty command, show the prompt again
    if command.strip() == "":
        continue

    # If the user types "help", show available commands
    if command == "help":
        print("Available commands:")
        print("  help          - Show this help message")
        print("  exit          - Exit the shell")
        print("  jobs          - List background jobs")
        print("  kill <job_id> - Terminate a background job")
        print("  fg <job_id>   - Bring a background job to the foreground")
        print("  <cmd> &       - Run command in the background")
        continue

    # If the user types "exit", stop the loop
    if command == "exit":
        print("Goodbye!")
        break

    # Handle "jobs" command
    if command.strip() == "jobs":
        print("Job ID | PID   | Command            | Status")
        print("-" * 50)
        
        # Clean up or check status of jobs
        for jid, job_info in list(job_table.items()):
            proc = job_info["process"]
            ret = proc.poll()
            status = "Running" if ret is None else f"Done ({ret})"
            print(f"{jid:<6} | {proc.pid:<5} | {job_info['cmd']:<18} | {status}")
        continue

    parts = command.split()
    if not parts:
        continue

    # Handle "kill <job_id>" command
    if parts[0] == "kill" and len(parts) > 1:
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
    if parts[0] == "fg" and len(parts) > 1:
        try:
            target_id = int(parts[1])
            if target_id in job_table:
                job_info = job_table[target_id]
                proc = job_info["process"]
                
                # Check if it's already finished
                if proc.poll() is not None:
                    print(f"Job {target_id} has already finished.")
                    del job_table[target_id]
                else:
                    print(f"Bringing job {target_id} ({job_info['cmd']}) to foreground...")
                    # Wait for the background process to finish in the foreground
                    proc.wait()
                    print(f"Job {target_id} finished.")
                    # Remove it from the job table once done
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
        parts = parts[:-1]  # Remove the '&' from the command arguments

    # Run regular or background command
    try:
        if is_background:
            proc = subprocess.Popen(parts)
            job_table[next_job_id] = {
                "process": proc,
                "cmd": " ".join(parts)
            }
            print(f"[{next_job_id}] {proc.pid}")
            next_job_id += 1
        else:
            subprocess.run(parts)

    except FileNotFoundError:
        print(f"Command not found: {parts[0]}")
    except Exception as e:
        print(f"An error occurred: {e}")
    