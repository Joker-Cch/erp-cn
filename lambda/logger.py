import logging

FORMAT = '%(asctime)-15s %(clientip)s %(message)s'
logging.basicConfig(format=FORMAT)
bslog = logging.Logger(__name__)
bslog.setLevel(20)