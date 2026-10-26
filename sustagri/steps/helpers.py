import requests
import logging
import pandas as pd

from django.conf import settings

from sustagri.projects.models import Project, Timeseries


def get_data(latitude=52.5200, longitude=13.4050, timeinfo=False):
    logger = logging.getLogger(__name__)
    session = requests.Session()

    headers = {"Referer": settings.WEATHER_DATA_API_HOST + "wefe/"}
    # alternative to avoid payload:
    # url = WEATHER_DATA_API_HOST + f"wefe/?lat={latitude}&lng={longitude}"
    payload = {"latitude": latitude, "longitude": longitude}
    response = session.get(settings.WEATHER_DATA_API_HOST + "wefe/", params=payload, headers=headers)
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data["variables"])
        logger.info("The weather data API fetch worked successfully")

        if timeinfo:
            timeindex = data["time"]
    else:
        df = pd.DataFrame()
        logger.error(f"The weather data API fetch did not work: {response.reason} ({response.status_code})")
        timeindex = None

    if timeinfo:
        return df, timeindex
    else:
        return df


def get_weather_data(proj_id, raw=True):
    """ """
    project = Project.objects.get(id=proj_id)
    qs_ts = Timeseries.objects.filter(project=project, name__startswith="weather_data")
    if not qs_ts.exists():
        df, timeinfo = get_data(latitude=project.latitude, longitude=project.longitude, timeinfo=True)

        if not raw:
            used_cols = ["ghi", "t_air", "t_dew", "windspeed", "fsr", "tp", "e", "cf_aware"]
            df = df[used_cols]

        for col in df.columns:
            ts = Timeseries.objects.create(
                name=f"weather_data_{col}",
                project=project,
                values=df[col].values.tolist(),
                start_time=timeinfo["start"],
                end_time=timeinfo["end"],
                time_step=8760,
            )
            ts.save()
        qs_ts = Timeseries.objects.filter(project=project)
    collected_timeseries = {ts.name: ts.values for ts in qs_ts}
    return collected_timeseries
