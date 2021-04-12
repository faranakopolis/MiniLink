import redis
import miniLink.redisDriver.conf as conf

r = redis.Redis(host=conf.HOST,
                port=conf.PORT,
                db=conf.DB)


def save_url(hashed, original):
    r.set(hashed, original)
    r.save()


def get_original_url(hashed):
    original = r.get(hashed)
    # Converting Byte to String and then returning it
    return str(original, 'utf-8')
