import os
import psutil

class ToyAllocator:
    def __init__(self, total_blocks=5):
        self.total_blocks = total_blocks
        # False = FREE, True = USED
        self.blocks = [False] * total_blocks

    def allocate(self):
        """Allocates the first available free block. Returns block index or None."""
        for i in range(self.total_blocks):
            if not self.blocks[i]:
                self.blocks[i] = True
                return i
        return None

    def free(self, index):
        """Frees the block at the given index."""
        if 0 <= index < self.total_blocks:
            self.blocks[index] = False
            return True
        return False

    def get_status_string(self):
        """Returns visual representation of the buffer pool."""
        return " ".join(["[USED]" if used else "[FREE]" for used in self.blocks])

def get_real_memstat(job_table):
    """Queries real memory usage (RSS) of active jobs using psutil."""
    stats = []
    
    # If no background jobs exist, include the shell itself as a demonstration
    if not job_table:
        curr_proc = psutil.Process(os.getpid())
        mem_mb = curr_proc.memory_info().rss / (1024 * 1024)
        stats.append({
            "name": "Shell (Self)",
            "pid": curr_proc.pid,
            "memory": f"{mem_mb:.1f} MB"
        })
        return stats

    for jid, job_info in job_table.items():
        proc = job_info["process"]
        try:
            p = psutil.Process(proc.pid)
            mem_bytes = p.memory_info().rss
            mem_mb = mem_bytes / (1024 * 1024)
            mem_str = f"{mem_mb:.1f} MB"
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            mem_str = "Terminated"

        stats.append({
            "name": f"Job {jid}",
            "pid": proc.pid,
            "memory": mem_str
        })
        
    return stats