import zipfile
import os, sys

#unzip EcoFashionV11.zip

zip_filepath = os.path.join(os.path.dirname(__file__), 'EcoFashionV11.zip')

print(zip_filepath)
dest_dir = os.path.join(os.path.dirname(__file__), 'EcoFashionV11')
with zipfile.ZipFile(zip_filepath) as zf:
    zf.extractall(dest_dir)
