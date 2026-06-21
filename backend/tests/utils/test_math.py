import math
from app.utils.geo import haversine

def test_haversine_same_point():
    distance = haversine(18.5204, 73.8567, 18.5204, 73.8567)
    assert distance == 0.0

def test_haversine_known_distance():
    # Pune to Mumbai (approx 118km)
    lat1, lon1 = 18.5204, 73.8567  # Pune
    lat2, lon2 = 19.0760, 72.8777  # Mumbai
    distance = haversine(lat1, lon1, lat2, lon2)
    
    # Check if distance is roughly 118km (118000 meters) +/- 5km
    assert 113000 <= distance <= 123000
