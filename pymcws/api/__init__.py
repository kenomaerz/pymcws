from pymcws.utils import transform_unstructured_response


def alive(media_server):
    response = media_server.send_request("Alive")
    return transform_unstructured_response(response)
