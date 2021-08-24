import pathlib
from PIL import Image
from RPA.FileSystem import FileSystem


def to_jpeg(files, output_dir):
    for file in files:
        image = Image.open(file.path)
        jpeg_file_name = f"{get_base_name(file)}.jpeg"
        image.save(f"{output_dir}/{jpeg_file_name}")
    return FileSystem().find_files(f"{output_dir}/*.jpeg")


def get_base_name(file):
    return pathlib.Path(file.name).stem
