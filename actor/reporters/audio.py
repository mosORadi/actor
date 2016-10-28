import os

from plugins import Reporter

AUDIO_CARD_PATH = '/proc/asound/card0/codec#0'

class HeadphonesPluggedReporter(Reporter):
    """
    Detects if headphones are plugged in, returns:
    - True, if headphones were detected
    - False, if headphones were not detected
    - None, if the detection failed
    """

    identifier = 'headphones_plugged'

    def run(self):
        # pylint: disable=arguments-differ

        if os.path.isfile(AUDIO_CARD_PATH):
            with open(AUDIO_CARD_PATH, 'r') as f:
                data = f.read()
                # Audio output jack has Conn set to Analog
                headphone_nodes = [node for node in data.split('Node 0x')
                                   if 'Conn = Analog' in node]

                # If there's not only one headphone node in the data,
                # we don't know what to report
                if len(headphone_nodes) == 1:
                    node = headphone_nodes[0]

                    if 'Pin-ctls: 0x00' in node:
                        return True

                    elif 'Pin-ctls: 0x40' in node:
                        return False
