import sys
import os
import zlib
import hashlib


def write_tree(directory="."): 
    list_os = os.listdir(directory)
    tree_entries = []
    for entry in sorted(list_os):
        if entry == ".git":
            continue
        path_completo = os.path.join(directory, entry)
        if os.path.isdir(path_completo):
            subdir_sha1_hex = write_tree(path_completo)
            mode = b"40000"
            name_bytes = entry.encode("utf-8")
            subdir_sha_bytes = bytes.fromhex(subdir_sha1_hex)
            entry_bytes = mode + b" " + name_bytes + b"\x00" + subdir_sha_bytes
            tree_entries.append(entry_bytes)

        elif os.path.isfile(path_completo):
            with open(path_completo, "rb") as f:
                data = f.read()
                header = f"blob {len(data)}\x00".encode("utf-8")
                stored_data = header + data
                hash_object = hashlib.sha1()
                hash_object.update(stored_data)
                sha1_hex = hash_object.hexdigest()
                compressed_data = zlib.compress(stored_data)
                dir_path = f".git/objects/{sha1_hex[0:2]}"
                name_bytes = entry.encode("utf-8")
                mode = b"100644"
                sha_bytes = bytes.fromhex(sha1_hex)
                if not os.path.exists(dir_path):
                    os.mkdir(dir_path)
                    with open(f"{dir_path}/{sha1_hex[2:]}", "wb") as obj_file:
                        obj_file.write(compressed_data)
                entry_bytes = mode + b" " + name_bytes + b"\x00" + sha_bytes
                tree_entries.append(entry_bytes)

    tree_content = b"".join(tree_entries)
    tree_header = f"tree {len(tree_content)}\x00".encode("utf-8")
    final_tree_data = tree_header + tree_content
    tree_hash_object = hashlib.sha1()
    tree_hash_object.update(final_tree_data) 
    tree_sha1_hex = tree_hash_object.hexdigest()
    compressed_tree_data = zlib.compress(final_tree_data)
    tree_dir_path = f".git/objects/{tree_sha1_hex[0:2]}"
    if not os.path.exists(tree_dir_path):
        os.mkdir(tree_dir_path)
        with open(f"{tree_dir_path}/{tree_sha1_hex[2:]}", "wb") as tree_obj_file:
            tree_obj_file.write(compressed_tree_data)
    return tree_sha1_hex

def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!", file=sys.stderr)
    
    command = sys.argv[1]
    if command == "init":
        os.mkdir(".git")
        os.mkdir(".git/objects")
        os.mkdir(".git/refs")
        with open(".git/HEAD", "w") as f:
            f.write("ref: refs/heads/main\n")
        print("Initialized git directory")
        
    elif command == "cat-file" and sys.argv[2] == "-p":
        object_hash = sys.argv[3]
        filename = f".git/objects/{object_hash[0:2]}/{object_hash[2:]}"
        with open(filename, "rb") as f:
            data = f.read()
            decompress_data = zlib.decompress(data)
            header_end = decompress_data.index(b"\x00")
            content = decompress_data[header_end + 1 :].strip()
            print(content.decode("utf-8"), end="")
    
    elif command == "hash-object" and sys.argv[2] == "-w":
        filename = sys.argv[3]
        with open(filename, "rb") as f:
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
    elif command == "write-tree":
        tree_sha = write_tree()
        print(tree_sha)
    
    else:
        raise RuntimeError(f"Unknown command #{command}")


if __name__ == "__main__":
    main()
