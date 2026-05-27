"""Climate zone to weather file mapping."""

from egc_compliance.models import ClimateZone


# EnergyPlus TMY3 weather files from https://energyplus.net/weather
CLIMATE_ZONE_EPW: dict[ClimateZone, str] = {
    ClimateZone.CZ_1A: "USA_FL_Miami.Intl.AP.722020_TMY3.epw",
    ClimateZone.CZ_2A: "USA_TX_Houston-Bush.Intercontinental.AP.722430_TMY3.epw",
    ClimateZone.CZ_2B: "USA_AZ_Phoenix.Sky.Harbor.Intl.AP.722780_TMY3.epw",
    ClimateZone.CZ_3A: "USA_GA_Atlanta.Hartsfield.Jackson.Intl.AP.722190_TMY3.epw",
    ClimateZone.CZ_3B: "USA_TX_El.Paso.Intl.AP.722700_TMY3.epw",
    ClimateZone.CZ_3C: "USA_CA_San.Francisco.Intl.AP.724940_TMY3.epw",
    ClimateZone.CZ_4A: "USA_MD_Baltimore-Washington.Intl.AP.724060_TMY3.epw",
    ClimateZone.CZ_4B: "USA_NM_Albuquerque.Intl.AP.723650_TMY3.epw",
    ClimateZone.CZ_4C: "USA_OR_Portland.Intl.AP.726980_TMY3.epw",
    ClimateZone.CZ_5A: "USA_MA_Boston-Logan.Intl.AP.725090_TMY3.epw",
    ClimateZone.CZ_5B: "USA_CO_Denver.Intl.AP.725650_TMY3.epw",
    ClimateZone.CZ_5C: "USA_WA_Port.Angeles.727885_TMY3.epw",
    ClimateZone.CZ_6A: "USA_MN_Minneapolis-St.Paul.Intl.AP.726580_TMY3.epw",
    ClimateZone.CZ_6B: "USA_MT_Helena.Rgnl.AP.727720_TMY3.epw",
    ClimateZone.CZ_7:  "USA_MN_International.Falls.Intl.AP.727470_TMY3.epw",
    ClimateZone.CZ_8:  "USA_AK_Fairbanks.Intl.AP.702610_TMY3.epw",
}


# Base URL for EnergyPlus weather data
ENERGYPLUS_WEATHER_BASE_URL = "https://energyplus.net/weather-download"

# North America weather data paths
WEATHER_DOWNLOAD_URLS: dict[ClimateZone, str] = {
    ClimateZone.CZ_1A: f"{ENERGYPLUS_WEATHER_BASE_URL}/north_and_central_america_wmo_region_4/USA/FL/USA_FL_Miami.Intl.AP.722020_TMY3/all",
    ClimateZone.CZ_2A: f"{ENERGYPLUS_WEATHER_BASE_URL}/north_and_central_america_wmo_region_4/USA/TX/USA_TX_Houston-Bush.Intercontinental.AP.722430_TMY3/all",
    ClimateZone.CZ_2B: f"{ENERGYPLUS_WEATHER_BASE_URL}/north_and_central_america_wmo_region_4/USA/AZ/USA_AZ_Phoenix.Sky.Harbor.Intl.AP.722780_TMY3/all",
    ClimateZone.CZ_3A: f"{ENERGYPLUS_WEATHER_BASE_URL}/north_and_central_america_wmo_region_4/USA/GA/USA_GA_Atlanta.Hartsfield.Jackson.Intl.AP.722190_TMY3/all",
    ClimateZone.CZ_3B: f"{ENERGYPLUS_WEATHER_BASE_URL}/north_and_central_america_wmo_region_4/USA/TX/USA_TX_El.Paso.Intl.AP.722700_TMY3/all",
    ClimateZone.CZ_3C: f"{ENERGYPLUS_WEATHER_BASE_URL}/north_and_central_america_wmo_region_4/USA/CA/USA_CA_San.Francisco.Intl.AP.724940_TMY3/all",
    ClimateZone.CZ_4A: f"{ENERGYPLUS_WEATHER_BASE_URL}/north_and_central_america_wmo_region_4/USA/MD/USA_MD_Baltimore-Washington.Intl.AP.724060_TMY3/all",
    ClimateZone.CZ_4B: f"{ENERGYPLUS_WEATHER_BASE_URL}/north_and_central_america_wmo_region_4/USA/NM/USA_NM_Albuquerque.Intl.AP.723650_TMY3/all",
    ClimateZone.CZ_4C: f"{ENERGYPLUS_WEATHER_BASE_URL}/north_and_central_america_wmo_region_4/USA/OR/USA_OR_Portland.Intl.AP.726980_TMY3/all",
    ClimateZone.CZ_5A: f"{ENERGYPLUS_WEATHER_BASE_URL}/north_and_central_america_wmo_region_4/USA/MA/USA_MA_Boston-Logan.Intl.AP.725090_TMY3/all",
    ClimateZone.CZ_5B: f"{ENERGYPLUS_WEATHER_BASE_URL}/north_and_central_america_wmo_region_4/USA/CO/USA_CO_Denver.Intl.AP.725650_TMY3/all",
    ClimateZone.CZ_5C: f"{ENERGYPLUS_WEATHER_BASE_URL}/north_and_central_america_wmo_region_4/USA/WA/USA_WA_Port.Angeles.727885_TMY3/all",
    ClimateZone.CZ_6A: f"{ENERGYPLUS_WEATHER_BASE_URL}/north_and_central_america_wmo_region_4/USA/MN/USA_MN_Minneapolis-St.Paul.Intl.AP.726580_TMY3/all",
    ClimateZone.CZ_6B: f"{ENERGYPLUS_WEATHER_BASE_URL}/north_and_central_america_wmo_region_4/USA/MT/USA_MT_Helena.Rgnl.AP.727720_TMY3/all",
    ClimateZone.CZ_7:  f"{ENERGYPLUS_WEATHER_BASE_URL}/north_and_central_america_wmo_region_4/USA/MN/USA_MN_International.Falls.Intl.AP.727470_TMY3/all",
    ClimateZone.CZ_8:  f"{ENERGYPLUS_WEATHER_BASE_URL}/north_and_central_america_wmo_region_4/USA/AK/USA_AK_Fairbanks.Intl.AP.702610_TMY3/all",
}
