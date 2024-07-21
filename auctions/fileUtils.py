from django.core.exceptions import ValidationError
import os

def validate_file_size(value):
    filesize = value.size
    if filesize > 10 * 1024 * 1024:
        raise ValidationError("The maximum file size that can be uploaded is 10MB.")

def del_testing_imgsVids(base_path):
    for subdir in ['auction_images', 'auction_videos']:
        path = os.path.join(base_path, subdir)
        if os.path.exists(path):
            for file in os.listdir(path):
                if file.startswith("testDel"):
                    file_path = os.path.join(path, file)
                    if os.path.isfile(file_path):
                        os.remove(file_path)

