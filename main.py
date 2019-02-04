import logging
from redfin import Redfin

def config_logger(log_path, file_name):
    log_formatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
    root_logger = logging.getLogger()

    file_handler = logging.FileHandler("{0}/{1}.log".format(log_path, file_name))
    file_handler.setFormatter(log_formatter)
    root_logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    root_logger.addHandler(console_handler)


if __name__ == '__main__':
    config_logger("./", "redfin_log")
    redfin = Redfin()
    redfin.search_sold_houses()
    # redfin.search_sold_houses_area("city/245/NY/Albany")
    # redfin.search_sold_houses_area('/city/10455/AR/Little-Rock')
    redfin.output()