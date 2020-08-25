from pymcws.model import MediaFile


def set_info(
    media_server, file: MediaFile, field_filter: dict = None,
):
    changed = file.changed_fields  # use only changed fields
    if field_filter is not None:  # filter fields to save, if indicated
        changed = dict(filter(lambda elem: elem[0] in field_filter, changed.items()))
    payload = {"File": file["Key"], "FileType": "Key"}
    # print(changed)
    if len(changed) > 1:
        payload["List"] = "CSV"
    fields = ""
    values = ""
    for field in changed.keys():
        fields += field + ","
        values += media_server.fields[field]["Encoder"](changed[field]) + ","

    payload["Field"] = fields[:-1]
    payload["Value"] = values[:-1]
    response = media_server.send_request("File/SetInfo", payload)

    return response
