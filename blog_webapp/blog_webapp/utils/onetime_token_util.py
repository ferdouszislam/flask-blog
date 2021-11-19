from blog_webapp import app
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


def get_onetime_token(payload_dict, expire_sec=1800):
    """
    get a time sensitive token for this user
    :param payload_dict: dict to be used in creating the tokenized
    :param expire_sec: token's expiration time in seconds
    :return: token
    """
    serializer = Serializer(app.config['SECRET_KEY'], expire_sec)
    return serializer.dumps(payload_dict).decode('utf-8')


def get_data_from_onetime_token(token, payload_key):
    """
    get onetime token after verification
    :param payload_key: data used for verifying the token
    :param token: token to be verified
    :return: data saved when creating the token
    """
    serializer = Serializer(app.config['SECRET_KEY'])
    try:
        payload_data = serializer.loads(token)[payload_key]
    except Exception as e:
        print(f'token verification failed {str(e)}')
        return None
    return payload_data
