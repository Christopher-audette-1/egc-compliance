"""
WeatherManager - manages EnergyPlus Weather (EPW) files.

This utility maps climate zones to representative weather stations and
downloads/caches EPW files for energy modeling.
"""

import os


class WeatherManager:
    """
    Manages EnergyPlus Weather (EPW) files for energy modeling.

    Maps climate zones to representative weather stations and handles
    downloading and caching of EPW files.
    """

    # Climate zone to weather station mapping
    # Based on ASHRAE 169-2013 climate zones
    CLIMATE_ZONE_WEATHER = {
        '1A': 'USA_FL_Miami.Intl.AP.722020',
        '2A': 'USA_TX_Houston-Bush.Intercontinental.AP.722430',
        '2B': 'USA_AZ_Phoenix-Sky.Harbor.Intl.AP.722780',
        '3A': 'USA_GA_Atlanta-Hartsfield-Jackson.Intl.AP.722190',
        '3B': 'USA_NV_Las.Vegas-McCarran.Intl.AP.723860',
        '3C': 'USA_CA_San.Francisco.Intl.AP.724940',
        '4A': 'USA_MD_Baltimore-Washington.Intl.AP.724060',
        '4B': 'USA_NM_Albuquerque.Intl.Sunport.723650',
        '4C': 'USA_WA_Seattle-Tacoma.Intl.AP.727930',
        '5A': 'USA_IL_Chicago-OHare.Intl.AP.725300',
        '5B': 'USA_CO_Denver.Intl.AP.725650',
        '5C': 'USA_WA_Port.Angeles-William.R.Fairchild.Intl.AP.727885',
        '6A': 'USA_MN_Minneapolis-St.Paul.Intl.AP.726580',
        '6B': 'USA_MT_Helena.Rgnl.AP.727720',
        '7': 'USA_MN_Duluth.Intl.AP.727450',
        '8': 'USA_AK_Fairbanks.Intl.AP.702610',
    }

    def __init__(self, cache_dir: str = None):
        """
        Initialize WeatherManager.

        Args:
            cache_dir: Directory to cache downloaded EPW files.
                       Defaults to ~/.audette/weather if not specified.
        """
        if cache_dir is None:
            cache_dir = os.path.expanduser('~/.audette/weather')
        self.cache_dir = cache_dir
        os.makedirs(self.cache_dir, exist_ok=True)

    def get_weather_file(self, climate_zone: str, custom_epw_path: str = None) -> str:
        """
        Get EPW file for a climate zone, downloading if necessary.

        Args:
            climate_zone: Climate zone code (e.g., '5A', '3C')
            custom_epw_path: Optional path to a custom EPW file (overrides lookup)

        Returns:
            Path to the EPW file

        Raises:
            ValueError: If climate zone is not supported
        """
        if custom_epw_path and os.path.exists(custom_epw_path):
            return custom_epw_path

        if climate_zone not in self.CLIMATE_ZONE_WEATHER:
            raise ValueError(
                f"Unknown climate zone: {climate_zone}. "
                f"Supported zones: {', '.join(sorted(self.CLIMATE_ZONE_WEATHER.keys()))}"
            )

        weather_station = self.CLIMATE_ZONE_WEATHER[climate_zone]
        epw_filename = f"{weather_station}.epw"
        epw_path = os.path.join(self.cache_dir, epw_filename)

        # Return cached file if it exists
        if os.path.exists(epw_path):
            return epw_path

        # Otherwise download it
        self._download_weather_file(weather_station, epw_path)
        return epw_path

    def _download_weather_file(self, weather_station: str, epw_path: str):
        """
        Resolve EPW file for a station using bundled EnergyPlus WeatherData directory.

        Bug 8 fix: the previous stub hardcoded San Francisco coordinates
        (lat=37.62, lon=-122.38, TZ=-8) for every climate zone, causing all
        simulations to use SF/Oakland weather regardless of building location.

        EnergyPlus ships with bundled TMY3/TMY EPW files for all ASHRAE climate
        zone representative cities. We look them up here instead of downloading.

        Args:
            weather_station: Weather station identifier
            epw_path: Path to save/link the EPW file

        Raises:
            FileNotFoundError: If no bundled EPW file found for the station
        """
        import shutil

        ep_dir = os.environ.get('ENERGYPLUS_DIR', '/usr/local/EnergyPlus-24-1-0')
        bundled_dir = os.path.join(ep_dir, 'WeatherData')

        # Try common EPW filename suffixes used by EnergyPlus bundled files
        for suffix in ['_TMY3.epw', '_TMY.epw', '.epw']:
            candidate = os.path.join(bundled_dir, weather_station + suffix)
            if os.path.exists(candidate):
                shutil.copy2(candidate, epw_path)
                return

        # Also try partial match (station codes can vary slightly between EP versions)
        if os.path.isdir(bundled_dir):
            station_base = weather_station.rsplit('.', 1)[0]  # strip WMO number suffix
            for fname in os.listdir(bundled_dir):
                if fname.endswith('.epw') and station_base in fname:
                    shutil.copy2(os.path.join(bundled_dir, fname), epw_path)
                    return

        raise FileNotFoundError(
            f"No bundled EPW file found for weather station '{weather_station}'. "
            f"Checked: {bundled_dir}. "
            f"Ensure EnergyPlus is installed at {ep_dir} with WeatherData files, "
            f"or set ENERGYPLUS_DIR environment variable."
        )
