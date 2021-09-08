# Helper functions used by differet classes

def escape_file_path(file_path):
    return file_path.replace(" ", "\ ").replace("(", "\(").replace(")", "\)").replace("&", "\&")
