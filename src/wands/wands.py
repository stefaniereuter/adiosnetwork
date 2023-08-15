import requests

# from pathlib import Path
from .wan import WandsWAN
from .data_cache import DataCache
from logger import logger


class Wands:
    """
    Entry class to wands
    """

    def __init__(
        self,
        data_cache_path: str,
        IPAddress="127.0.0.1",
        Port="12345",
        Timeout="30",
        TransportMode="reliable",
        RendezvousReaderCount="1",
        webaddress="http://localhost:8080/data",
    ):
        self._Adiosparams = {
            "IPAddress": IPAddress,
            "Port": Port,
            "Timeout": Timeout,
            "TransportMode": TransportMode,
            "RendezvousReaderCount": RendezvousReaderCount,
            "Threading": "true",
        }

        self._webaddress = webaddress
        self.dataCache = DataCache(data_cache_path)

    def cache_location(self):
        return f"{self.dataCache!s}"

    def request(self, filename: str, data_list: list) -> dict:
        """
        Request the needed data. This function will check if the data is available locally
        and otherwise request the data remotely.
        """
        # only for performance measurement from time import time
        #
        # remove locally available datasets from list
        # only for performance measurement
        logger.debug(f"request: type datalist: {type(data_list)}")

        data_from_remote = {}
        # only for performance measurement timereq = time()

        # create lists to see which data is already local and which data
        # needs to be fetched remotely
        remote_list, local_list = self.dataCache.check_availability(
            filename=filename, data_list=data_list
        )

        # only for performance measurement timecheckav = time()
        # load the data that was previously defined as local from the local cache
        data_from_cache = self.dataCache.load_from_cache(
            filename=filename, local_list=local_list
        )
        # only for performance measurement timedatalocal = time()
        logger.info(f"Signals found locally: {local_list}")
        logger.info(f"Signals to be requested remotely: {remote_list}")
        # fetch data remotely
        if remote_list:
            data = {
                "uri": filename,
                "signals": remote_list,
            }
            response = requests.post(self._webaddress, json=data)
            logger.info(response.status_code)
            logger.info(response.json())
            wandsWAN_obj = WandsWAN(parameters=self._Adiosparams)

            data_from_remote = wandsWAN_obj.receive(remote_list)
            # only for performance measurement timeremote = time()
            self.dataCache.write(filename=filename, data_dict=data_from_remote)
            # only for performance measurement timewrite = time()
        # only for performance measurement
        logger.debug(f"Timings:\n check av = {timecheckav-timereq}\n t_lfc = {timedatalocal-timecheckav}\n ")
        # only for performance measurement if remote_list:
        # only for performance measurement
        logger.debug(f"t_getremote = {timeremote-timedatalocal}\n t_toDB = {timewrite-timeremote}")
        return data_from_remote | data_from_cache
