import logging


def init_logging(output_dir, file_name, LOGGER):
    LOGGER.setLevel(logging.INFO)
    
    fmt = logging.Formatter('%(asctime)s: [ %(message)s ]',
                            '%m/%d/%Y %I:%M:%S %p')
    
    console = logging.StreamHandler()
    console.setFormatter(fmt)
    LOGGER.addHandler(console)
    
    fileHandler = logging.FileHandler(f"{output_dir}/{file_name}.log")
    fileHandler.setFormatter(fmt)
    LOGGER.addHandler(fileHandler)
