"""
Seed the hubs and transporters tables so Hub-Assisted Fulfillment,
Hub Suggestion, and Delivery Recommendation work out of the box in production.
"""

from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import SessionLocal, engine, Base
from app.models import Hub, Transporter, VehicleType, PriceRecord
from app.services.kisan_rail_routes import lookup as kisan_rail_lookup

# Seed hubs covering all major agricultural states and districts
# (district, market_name, state, lat, lng)
DEFAULT_HUBS: list[tuple[str, str, str, Optional[float], Optional[float]]] = [
    # West Bengal
    ("Kolkata", "Kolkata Market", "West Bengal", 22.5726, 88.3639),
    ("Howrah", "Howrah Mandi", "West Bengal", 22.5958, 88.2636),
    ("Paschim Bardhaman", "Asansol Market", "West Bengal", 23.6739, 86.9524),
    ("Purba Bardhaman", "Bardhaman Market Yard", "West Bengal", 23.2324, 87.8615),
    ("Hooghly", "Hooghly Mandi", "West Bengal", 22.9000, 88.3900),
    ("North 24 Parganas", "Barasat Market", "West Bengal", 22.7200, 88.4800),
    ("South 24 Parganas", "Diamond Harbour Market", "West Bengal", 22.1900, 88.1900),
    ("Nadia", "Kalyani APMC", "West Bengal", 22.9750, 88.4344),
    ("Darjeeling", "Siliguri Market", "West Bengal", 26.7271, 88.3953),
    ("Murshidabad", "Baharampur Market", "West Bengal", 24.1000, 88.2500),
    ("Malda", "Malda APMC", "West Bengal", 25.0000, 88.1400),
    ("Bankura", "Bankura Mandi", "West Bengal", 23.2300, 87.0700),
    ("Birbhum", "Bolpur APMC", "West Bengal", 23.6700, 87.7200),
    ("Paschim Medinipur", "Midnapore Market", "West Bengal", 22.4200, 87.3200),
    ("Purba Medinipur", "Tamluk Market", "West Bengal", 22.3000, 87.9200),

    # Maharashtra
    ("Pune", "Pune Market Yard", "Maharashtra", 18.5204, 73.8567),
    ("Nashik", "Nashik APMC", "Maharashtra", 19.9975, 73.7898),
    ("Mumbai City", "Mumbai APMC", "Maharashtra", 19.0760, 72.8777),
    ("Thane", "Thane Market", "Maharashtra", 19.2183, 72.9781),
    ("Nagpur", "Nagpur Mandi", "Maharashtra", 21.1458, 79.0882),
    ("Ahmednagar", "Ahmednagar Market", "Maharashtra", 19.0948, 74.7480),
    ("Solapur", "Solapur Mandi", "Maharashtra", 17.6599, 75.9064),
    ("Kolhapur", "Kolhapur Market", "Maharashtra", 16.7050, 74.2433),
    ("Amravati", "Amravati Mandi", "Maharashtra", 20.9374, 77.7796),

    # Delhi
    ("New Delhi", "Azadpur Mandi", "Delhi", 28.6139, 77.2090),
    ("South Delhi", "Okhla Market", "Delhi", 28.5355, 77.2800),

    # Gujarat
    ("Ahmedabad", "Ahmedabad APMC", "Gujarat", 23.0225, 72.5714),
    ("Rajkot", "Rajkot Mandi", "Gujarat", 22.3039, 70.8022),
    ("Surat", "Surat Market", "Gujarat", 21.1702, 72.8311),

    # Karnataka
    ("Bangalore", "Yeshwanthpur APMC", "Karnataka", 12.9716, 77.5946),
    ("Bengaluru", "Yeshwanthpur APMC", "Karnataka", 12.9716, 77.5946),
    ("Hubli", "Hubli Market", "Karnataka", 15.3647, 75.1240),
    ("Mysore", "Mysore Mandi", "Karnataka", 12.2958, 76.6394),

    # Tamil Nadu
    ("Chennai", "Koyambedu Market", "Tamil Nadu", 13.0827, 80.2707),
    ("Coimbatore", "Coimbatore Mandi", "Tamil Nadu", 11.0168, 76.9558),
    ("Madurai", "Madurai Market", "Tamil Nadu", 9.9252, 78.1198),

    # Telangana
    ("Hyderabad", "Hyderabad Market", "Telangana", 17.3850, 78.4867),
    ("Warangal", "Warangal Mandi", "Telangana", 17.9689, 79.5941),

    # Andhra Pradesh
    ("Guntur", "Guntur Market Yard", "Andhra Pradesh", 16.3067, 80.4365),
    ("Krishna", "Vijayawada Market", "Andhra Pradesh", 16.5062, 80.6480),
    ("Kurnool", "Kurnool Mandi", "Andhra Pradesh", 15.8281, 78.0373),

    # Uttar Pradesh
    ("Lucknow", "Lucknow Mandi", "Uttar Pradesh", 26.8467, 80.9462),
    ("Agra", "Agra Market", "Uttar Pradesh", 27.1767, 78.0081),
    ("Varanasi", "Varanasi Mandi", "Uttar Pradesh", 25.3176, 82.9739),
    ("Kanpur Nagar", "Kanpur Market", "Uttar Pradesh", 26.4499, 80.3319),

    # Punjab
    ("Ludhiana", "Ludhiana Mandi", "Punjab", 30.9010, 75.8573),
    ("Amritsar", "Amritsar Mandi", "Punjab", 31.6340, 74.8723),
    ("Patiala", "Patiala Market", "Punjab", 30.3398, 76.3869),

    # Haryana
    ("Karnal", "Karnal Mandi", "Haryana", 29.6857, 76.9905),
    ("Hisar", "Hisar Mandi", "Haryana", 29.1492, 75.7217),
    ("Ambala", "Ambala Market", "Haryana", 30.3782, 76.7767),

    # Rajasthan
    ("Jaipur", "Jaipur Mandi", "Rajasthan", 26.9124, 75.7873),
    ("Jodhpur", "Jodhpur Market", "Rajasthan", 26.2389, 73.0243),
    ("Kota", "Kota Mandi", "Rajasthan", 25.2138, 75.8648),

    # Madhya Pradesh
    ("Indore", "Indore Mandi", "Madhya Pradesh", 22.7196, 75.8577),
    ("Bhopal", "Bhopal Market", "Madhya Pradesh", 23.2599, 77.4126),
    ("Jabalpur", "Jabalpur Mandi", "Madhya Pradesh", 23.1815, 79.9864),

    # Bihar
    ("Patna", "Patna Market Yard", "Bihar", 25.5941, 85.1376),
    ("Muzaffarpur", "Muzaffarpur Mandi", "Bihar", 26.1209, 85.3647),
    ("Gaya", "Gaya Market", "Bihar", 24.7914, 85.0002),

    # Kerala
    ("Ernakulam", "Kochi Market", "Kerala", 9.9816, 76.2999),
    ("Thiruvananthapuram", "Trivandrum Market", "Kerala", 8.5241, 76.9366),

    # Odisha
    ("Khordha", "Bhubaneswar Market", "Odisha", 20.2961, 85.8245),
    ("Cuttack", "Cuttack Mandi", "Odisha", 20.4625, 85.8830),

    # Assam
    ("Kamrup", "Guwahati Market", "Assam", 26.1445, 91.7362),
    ("Nagaon", "Nagaon Mandi", "Assam", 26.3463, 92.6840),

    # Jharkhand
    ("Ranchi", "Ranchi Market Yard", "Jharkhand", 23.3441, 85.3096),
    ("Dhanbad", "Dhanbad Mandi", "Jharkhand", 23.7957, 86.4304),

    # Chhattisgarh
    ("Raipur", "Raipur Mandi", "Chhattisgarh", 21.2514, 81.6296),
    ("Durg", "Durg Market", "Chhattisgarh", 21.1904, 81.2849),

    # Himachal Pradesh
    ("Shimla", "Shimla Market", "Himachal Pradesh", 31.1048, 77.1734),
    ("Kullu", "Kullu Mandi", "Himachal Pradesh", 31.9579, 77.1095),

    # Uttarakhand
    ("Dehradun", "Dehradun Mandi", "Uttarakhand", 30.3165, 78.0322),
    ("Haridwar", "Haridwar Market", "Uttarakhand", 29.9457, 78.1642),

    # Jammu & Kashmir
    ("Srinagar", "Srinagar Market", "Jammu and Kashmir", 34.0837, 74.7973),
    ("Jammu", "Jammu Mandi", "Jammu and Kashmir", 32.7266, 74.8570),

    # Goa
    ("North Goa", "Mapusa Market", "Goa", 15.5937, 73.8142),
    ("South Goa", "Margao Market", "Goa", 15.2832, 73.9862),

    # Northeast & UTs
    ("Papum Pare", "Itanagar Market", "Arunachal Pradesh", 27.0844, 93.6053),
    ("East Khasi Hills", "Shillong Market", "Meghalaya", 25.5788, 91.8933),
    ("Aizawl", "Aizawl Market", "Mizoram", 23.7271, 92.7176),
    ("Dimapur", "Dimapur Market", "Nagaland", 25.9094, 93.7266),
    ("Imphal West", "Imphal Market", "Manipur", 24.8170, 93.9368),
    ("West Tripura", "Agartala Market", "Tripura", 23.8315, 91.2868),
    ("Gangtok", "Gangtok Market", "Sikkim", 27.3389, 88.6065),
    ("South Andaman", "Port Blair Market", "Andaman and Nicobar", 11.6234, 92.7265),
    ("Chandigarh", "Chandigarh Mandi", "Chandigarh", 30.7333, 76.7794),
    ("Leh", "Leh Market", "Ladakh", 34.1526, 77.5771),
    ("Puducherry", "Puducherry Market", "Puducherry", 11.9416, 79.8083),
]

DEFAULT_TRANSPORTERS = [
    {"name": "Bengal Express Logistics", "district": "Kolkata", "vehicle_type": VehicleType.mini_truck, "capacity_kg": 1500, "verified": True},
    {"name": "Howrah Freight Cargo", "district": "Howrah", "vehicle_type": VehicleType.medium_truck, "capacity_kg": 4000, "verified": True},
    {"name": "Bardhaman Agri Transport", "district": "Paschim Bardhaman", "vehicle_type": VehicleType.medium_truck, "capacity_kg": 3500, "verified": True},
    {"name": "Pune Kisan Carrier", "district": "Pune", "vehicle_type": VehicleType.mini_truck, "capacity_kg": 1200, "verified": True},
    {"name": "Maharashtra Agri Haulage", "district": "Nashik", "vehicle_type": VehicleType.medium_truck, "capacity_kg": 5000, "verified": True},
    {"name": "Delhi NCR Fleet", "district": "New Delhi", "vehicle_type": VehicleType.large_truck, "capacity_kg": 10000, "verified": True},
    {"name": "South India Agro Express", "district": "Bangalore", "vehicle_type": VehicleType.medium_truck, "capacity_kg": 4500, "verified": True},
    {"name": "Guntur Produce Freight", "district": "Guntur", "vehicle_type": VehicleType.medium_truck, "capacity_kg": 3000, "verified": True},
]


def seed_hubs(clear_existing: bool = False) -> int:
    """Seed hubs table from predefined hubs and distinct price_records."""
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()
    total_added = 0
    try:
        if clear_existing:
            db.query(Hub).delete()
            db.commit()

        existing_pairs = {
            (normalize(h.district), normalize(h.state))
            for h in db.query(Hub).all()
        }

        for district, name, state, lat, lng in DEFAULT_HUBS:
            key = (normalize(district), normalize(state))
            if key in existing_pairs:
                continue

            rail_info = kisan_rail_lookup(district)
            has_rail = rail_info.get("exists", False)
            stn_name = rail_info.get("station_name")

            hub = Hub(
                name=name,
                district=district,
                state=state,
                lat=lat,
                lng=lng,
                has_kisan_rail_station=has_rail,
                kisan_rail_station_name=stn_name,
            )
            db.add(hub)
            existing_pairs.add(key)
            total_added += 1

        # Also pull any distinct (market, district, state) from price_records if present
        try:
            mandi_rows = (
                db.query(PriceRecord.market, PriceRecord.district, PriceRecord.state)
                .filter(
                    PriceRecord.market.isnot(None),
                    PriceRecord.district.isnot(None),
                    PriceRecord.state.isnot(None),
                )
                .distinct()
                .all()
            )
            for market, dist, st in mandi_rows:
                key = (normalize(dist), normalize(st))
                if key in existing_pairs:
                    continue
                rail_info = kisan_rail_lookup(dist)
                db.add(
                    Hub(
                        name=f"{market} Mandi" if not market.endswith(("Mandi", "Market", "APMC")) else market,
                        district=dist,
                        state=st,
                        has_kisan_rail_station=rail_info.get("exists", False),
                        kisan_rail_station_name=rail_info.get("station_name"),
                    )
                )
                existing_pairs.add(key)
                total_added += 1
        except Exception:
            pass

        db.commit()

        # Also ensure transporters exist
        seed_transporters_if_empty(db)

        count = db.query(Hub).count()
        print(f"[seed_hubs] Total hubs in DB: {count} (added {total_added})")
        return count
    finally:
        db.close()


def seed_transporters_if_empty(db: Optional[Session] = None) -> int:
    """Ensure baseline transporters are seeded for demo fulfillment recommendations."""
    owns_session = False
    if db is None:
        db = SessionLocal()
        owns_session = True

    try:
        existing = db.query(Transporter).count()
        if existing > 0:
            return existing

        for item in DEFAULT_TRANSPORTERS:
            db.add(
                Transporter(
                    name=item["name"],
                    district=item["district"],
                    vehicle_type=item["vehicle_type"],
                    capacity_kg=item["capacity_kg"],
                    verified=item["verified"],
                )
            )
        db.commit()
        return len(DEFAULT_TRANSPORTERS)
    finally:
        if owns_session:
            db.close()


def seed_hubs_if_empty() -> int:
    """Safe startup helper: only seeds if hubs table is currently empty."""
    db = SessionLocal()
    try:
        count = db.query(Hub).count()
        if count == 0:
            print("[seed_hubs] No hubs found in database. Seeding now...")
            return seed_hubs(clear_existing=False)
        return count
    finally:
        db.close()


def normalize(s: Optional[str]) -> str:
    return (s or "").strip().lower()


if __name__ == "__main__":
    import sys
    force = "--force" in sys.argv
    seed_hubs(clear_existing=force)
