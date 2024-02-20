import os
#print(os.environ)
root = os.environ['LABEL_STUDIO_LOCAL_FILES_DOCUMENT_ROOT']
print(root)
Path = C:\data\media\Input_Images
if (Path(root) in Path(local_store_path).parents) is False:
        raise ValueError(
            f'{str(Path(root))} is not presented in local_store_path parents: '
            f'{str(Path(local_store_path).parents)}'
        )
    
