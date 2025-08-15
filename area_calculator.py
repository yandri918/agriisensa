import math

class AreaCalculator:
    @staticmethod
    def calculate_polygon_area(coordinates):
        """
        Hitung luas polygon menggunakan rumus shoelace
        coordinates: list of tuples [(lat, lon), (lat, lon), ...]
        """
        if len(coordinates) < 3:
            return 0
        
        # Rumus shoelace untuk koordinat 2D
        total_area = 0
        n = len(coordinates)
        
        for i in range(n):
            j = (i + 1) % n
            total_area += coordinates[i][0] * coordinates[j][1]
            total_area -= coordinates[j][0] * coordinates[i][1]
        
        area = abs(total_area) / 2.0
        # Konversi ke hektar (estimasi)
        area_hectare = area * 1232100 / 10000
        return round(area_hectare, 2)
    
    @staticmethod
    def calculate_approximate_area(latitudes, longitudes):
        """
        Hitung luas area secara approximate
        """
        if len(latitudes) < 3 or len(longitudes) < 3:
            return 0
        
        # Hitung rata-rata koordinat
        avg_lat = sum(latitudes) / len(latitudes)
        avg_lon = sum(longitudes) / len(longitudes)
        
        # Hitung luas dalam meter persegi
        lat_diff = max(latitudes) - min(latitudes)
        lon_diff = max(longitudes) - min(longitudes)
        
        # Konversi ke meter
        lat_meter = lat_diff * 111000  # 1 derajat ~ 111 km
        lon_meter = lon_diff * 111000 * math.cos(math.radians(avg_lat))
        
        area_m2 = lat_meter * lon_meter
        area_hectare = area_m2 / 10000  # Konversi ke hektar
        
        return round(area_hectare, 2)