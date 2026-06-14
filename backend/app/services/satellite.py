from app.schemas.response import SatelliteInfo

class SatelliteService:
    def __init__(self, client=None):
        self.client = client

    async def get_satellite_info(self, latitude: float, longitude: float, location_label: str) -> SatelliteInfo:
        # TODO: integrate Sentinel Hub API
        return SatelliteInfo(
            location=location_label,
            image_url=None,
            description=f"Satellite imagery for {location_label} is not yet available. (Integration pending: Sentinel Hub)",
            acquisition_date=None
        )
