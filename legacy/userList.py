import os

directory_path = '/Users'  # Replace this with your directory path
folder_list=[]
if os.path.exists(directory_path) and os.path.isdir(directory_path):
    folder_list = [folder for folder in os.listdir(directory_path) if os.path.isdir(os.path.join(directory_path, folder))]

folder_list.remove("Shared")
print(folder_list)
