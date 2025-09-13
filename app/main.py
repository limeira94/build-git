import sys
import os
import zlib
import hashlib

class InitCommand:    
    def execute(self):
        os.mkdir(".git")
        os.mkdir(".git/objects")
        os.mkdir(".git/refs")
        with open(".git/HEAD", "w") as f:
            f.write("ref: refs/heads/main\n")
        print("Initialized git directory")

class CatFileCommand:
    def __init__(self, object_hash):
        self.hash = object_hash
        
    def execute(self):
        filename = f".git/objects/{self.hash[0:2]}/{self.hash[2:]}"
        with open(filename, "rb") as f:
            data = f.read()
            decompress_data = zlib.decompress(data)
            header_end = decompress_data.index(b"\x00")
            content = decompress_data[header_end + 1 :].strip()
            print(content.decode("utf-8"), end="")

class HashObjectCommand:
    def __init__(self, filename):
        self.filename = filename
    
    def execute(self):
        with open(self.filename, "rb") as f:
            data = f.read()
            header = f"blob {len(data)}\x00".encode("utf-8")
            stored_data = header + data
            hash_object = hashlib.sha1()
            hash_object.update(stored_data)
            sha1_hash = hash_object.hexdigest()
            compressed_data = zlib.compress(stored_data)
            dir_path = f".git/objects/{sha1_hash[0:2]}"
            if not os.path.exists(dir_path):
                os.mkdir(dir_path)
                with open(f"{dir_path}/{sha1_hash[2:]}", "wb") as obj_file:
                    obj_file.write(compressed_data)
            print(sha1_hash)

def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!", file=sys.stderr)
    
    command = sys.argv[1]
    if command == "init":
        cmd = InitCommand()
        cmd.execute()
    elif command == "cat-file" and sys.argv[2] == "-p":
        object_hash = sys.argv[3]
        cmd = CatFileCommand(object_hash)
        cmd.execute()
    elif command == "hash-object" and sys.argv[2] == "-w":
        filename = sys.argv[3]
        cmd = HashObjectCommand(filename)
        cmd.execute()
    elif command == "ls-tree":
        is_name_only = "--name-only" in sys.argv
        
        if is_name_only:
            object_hash = sys.argv[3]
        else:
            object_hash = sys.argv[2]
    
        file_path = f".git/objects/{object_hash[0:2]}/{object_hash[2:]}"
        with open(file_path, "rb") as f:
            data = f.read()
            decompress_data = zlib.decompress(data)
            header_end = decompress_data.index(b"\x00")
            content = decompress_data[header_end + 1 :]
        
        entries = []
        while content:
            space_index = content.index(b" ")
            null_index = content.index(b"\x00", space_index)
            
            name_bytes = content[space_index + 1 : null_index]
            name = name_bytes.decode("utf-8")
            
            if is_name_only:
                entries.append(name)
            
            else:    
                mode = content[:space_index].decode("utf-8")
                
                type_mode = ""
                if mode == "40000":  # Directory
                    type_mode = "tree"
                elif mode == "100644":  # Regular file
                    type_mode = "blob"
                
                binary_hash = content[null_index + 1 : null_index + 1 + 20]
                sha = binary_hash.hex()
                
                row_format = f"{mode} {type_mode} {sha}\t{name}"

                entries.append(row_format)
            end_of_entry = null_index + 1 + 20
            content = content[end_of_entry:]

        entries.sort()
        for entry in entries:
            print(entry)

    else:
        raise RuntimeError(f"Unknown command #{command}")


if __name__ == "__main__":
    main()
