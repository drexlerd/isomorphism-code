import os
import errno


def create_directory_for_filename(filename):
    """ Creates all directories necessary to store the given filename. """
    if not os.path.exists(os.path.dirname(filename)):
        try:
            os.makedirs(os.path.dirname(filename))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise
