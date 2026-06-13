from pathlib import Path

class FilesystemServer:

    # List project files
    def list_files(self,directory: str):

        path = Path(directory)

        if not path.exists():
            return []
        
        return [str(item) for item in path.iterdir()]
    

    # Read file content
    def read_file(self, file_path):

        path = Path(file_path)

        if not path.exists():
            return "File not found"
        
        return path.read_text(encoding="utf-8")

    
    # search file 
    def search_files(self,root_directory: str, keyword: str):

        matches = []    

        for file in Path(root_directory).rglob("*"):
            if not file.is_file():
                continue

            try:
                content = file.read_text(encoding="utf-8")

                if keyword.lower() in content.lower():
                    matches.append(
                        str(file)
                    )

            except:
                continue
        return matches
            


    
    

        
