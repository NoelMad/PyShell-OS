class FSNode:
    def __init__(self, name, is_dir=False, content=""):
        self.name = name
        self.is_dir = is_dir
        self.content = content
        self.children = {} if is_dir else {}
        # Calculate simulated blocks based on content length (min 1 block for files/dirs)
        self.blocks_used = max(1, len(content.encode('utf-8')) // 32 + 1) if not is_dir else 1

class SimulatedFileSystem:
    def __init__(self, total_blocks=100):
        self.root = FSNode("/", is_dir=True)
        self.total_blocks = total_blocks
        self._initialize_default_structure()

    def _initialize_default_structure(self):
        """Initializes default filesystem entries required by milestones."""
        self.mkdir("/job_logs")
        self.write_file("/history", "help\nschedule\nmemstat\nconcurrency\n")
        self.write_file("/aliases", "ll=ls -l\ncls=clear\n")
        self.write_file("/job_logs/job1", "Job 1 completed successfully. Exit code 0.")
        self.write_file("/job_logs/job2", "Job 2 completed successfully. Exit code 0.")
        self.write_file("/job_logs/job3", "Job 3 completed with warnings.")

    def _resolve_path(self, path):
        """Resolves a path string to an FSNode."""
        parts = [p for p in path.strip("/").split("/") if p]
        curr = self.root
        for part in parts:
            if curr.is_dir and part in curr.children:
                curr = curr.children[part]
            else:
                return None
        return curr

    def mkdir(self, path):
        """Creates a directory at the specified path."""
        parts = [p for p in path.strip("/").split("/") if p]
        curr = self.root
        for part in parts:
            if part not in curr.children:
                curr.children[part] = FSNode(part, is_dir=True)
            curr = curr.children[part]
        return True

    def write_file(self, path, content):
        """Writes or updates content in a file at the specified path."""
        parts = [p for p in path.strip("/").split("/") if p]
        if not parts:
            return False
        dir_parts = parts[:-1]
        filename = parts[-1]
        
        curr = self.root
        for part in dir_parts:
            if part not in curr.children:
                curr.children[part] = FSNode(part, is_dir=True)
            curr = curr.children[part]
            
        if filename in curr.children:
            curr.children[filename].content = content
            curr.children[filename].blocks_used = max(1, len(content.encode('utf-8')) // 32 + 1)
        else:
            curr.children[filename] = FSNode(filename, is_dir=False, content=content)
        return True

    def read_file(self, path):
        """Reads content from a file at the specified path."""
        node = self._resolve_path(path)
        if node and not node.is_dir:
            return node.content
        return None

    def get_stats(self):
        """Calculates filesystem statistics (files, directories, block usage)."""
        file_count = 0
        dir_count = 0
        used_blocks = 0

        def traverse(node):
            nonlocal file_count, dir_count, used_blocks
            if node.is_dir:
                dir_count += 1
                for child in node.children.values():
                    traverse(child)
            else:
                file_count += 1
                used_blocks += node.blocks_used

        traverse(self.root)
        free_blocks = max(0, self.total_blocks - used_blocks)
        return {
            "files": file_count,
            "directories": dir_count,
            "used_blocks": used_blocks,
            "free_blocks": free_blocks
        }

    def print_tree(self, node=None, prefix=""):
        """Prints a visual tree of the filesystem."""
        if node is None:
            node = self.root
            print("PyShell File System\n")
            print("/")
        
        children = list(node.children.items())
        for i, (name, child) in enumerate(children):
            connector = "└── " if i == len(children) - 1 else "├── "
            print(f"{prefix}{connector}{name}")
            if child.is_dir:
                extension = "    " if i == len(children) - 1 else "│   "
                self.print_tree(child, prefix + extension)