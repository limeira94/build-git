import sys
import os
import zlib

def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!", file=sys.stderr)

    # Uncomment this block to pass the first stage
    
    command = sys.argv[1]
    if command == "init":
        os.mkdir(".git")
        os.mkdir(".git/objects")
        os.mkdir(".git/refs")
        with open(".git/HEAD", "w") as f:
            f.write("ref: refs/heads/main\n")
        print("Initialized git directory")
    elif command == "cat-file" and sys.argv[2] == "-p":
        file = sys.argv[3]
        filename = f".git/objects/{file[0:2]}/{file[2:]}"
        with open(filename, "rb") as f:
            data = f.read()
            decompress_data = zlib.decompress(data)
            header_end = decompress_data.index(b"\x00")
            content = decompress_data[header_end + 1 :].strip()
            print(content.decode("utf-8"), end="")
     
    else:
        raise RuntimeError(f"Unknown command #{command}")


if __name__ == "__main__":
    main()
