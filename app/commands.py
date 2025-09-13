import os


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
        file = sys.argv[3]
        filename = f".git/objects/{file[0:2]}/{file[2:]}"
        with open(filename, "rb") as f:
            data = f.read()
            decompress_data = zlib.decompress(data)
            header_end = decompress_data.index(b"\x00")
            content = decompress_data[header_end + 1 :].strip()
            print(content.decode("utf-8"), end="")

class HashObjectCommand:
    def __init__(self, file_path):
        self.file_path = file_path
    
    def execute(self):
        file = sys.argv[3]
        with open(file, "rb") as f:
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

