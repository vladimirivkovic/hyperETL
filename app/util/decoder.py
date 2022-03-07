import base64


def decode(content):
    if content == None:
        return None
    try:
        return base64.b64decode(content).decode()
    except:
        return content
