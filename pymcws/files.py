def transform_path(files, search_for: str, replace_with: str,
                   win_to_unix: bool = False, unix_to_win: bool = false):
    """
    """
    for file in files:
        file = file.replace(search_for, replace_with)
        if win_to_unix:
            file = file.replace('\\', '/')
        elif unix_to_win:
            file = file.replace('/', '\\')
    return files
