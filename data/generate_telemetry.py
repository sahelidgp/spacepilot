import sqlite3
import random
from datetime import datetime, timedelta
import os

def create_database(db_path="satellites.db"):
    os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Drop existing tables
    cursor.execute("DROP TABLE IF EXISTS telemetry")
    cursor.execute("DROP TABLE IF EXISTS satellites")

    # 1. Satellites Metadata Table
    cursor.execute("""
    CREATE TABLE satellites (
        satellite_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        operator TEXT NOT NULL,
        mission_type TEXT NOT NULL,
        orbit_type TEXT NOT NULL,
        altitude_km REAL NOT NULL,
        inclination_deg REAL NOT NULL,
        launch_date TEXT NOT NULL,
        status TEXT NOT NULL
    )
    """)

    satellites = [
        ("SAT-ISRO-01", "INSAT-3DR", "ISRO", "Meteorological & Search-and-Rescue", "GEO", 35786.0, 0.05, "2016-09-08", "OPERATIONAL"),
        ("SAT-ISRO-02", "Cartosat-3", "ISRO", "High-Resolution Earth Observation", "SSO", 505.0, 97.5, "2019-11-27", "OPERATIONAL"),
        ("SAT-ISRO-03", "GSAT-29", "ISRO", "High-Throughput Communication", "GEO", 35786.0, 0.08, "2018-11-14", "OPERATIONAL"),
        ("SAT-ISRO-04", "EOS-04 (RISAT-1A)", "ISRO", "Radar Imaging (SAR) Defense Reconnaissance", "SSO", 529.0, 97.5, "2022-02-14", "DEGRADED"),
        ("SAT-ISRO-05", "Chandrayaan-3 Propulsion", "ISRO", "Lunar Transfer & Relay", "HEO", 154000.0, 21.4, "2023-07-14", "OPERATIONAL"),
        ("SAT-DEF-01", "GSAT-7A (Angry Bird)", "Indian Air Force", "Military Aerospace Communication", "GEO", 35786.0, 0.1, "2018-12-19", "OPERATIONAL"),
        ("SAT-DEF-02", "EMISAT", "DRDO / ISRO", "Electromagnetic Electronic Intelligence (ELINT)", "SSO", 748.0, 98.4, "2019-04-01", "OPERATIONAL"),
    ]

    cursor.executemany("""
    INSERT INTO satellites VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, satellites)

    # 2. Telemetry Time-Series Table
    cursor.execute("""
    CREATE TABLE telemetry (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        satellite_id TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        battery_voltage REAL NOT NULL,
        battery_temp_c REAL NOT NULL,
        solar_panel_current REAL NOT NULL,
        gyro_drift_rate REAL NOT NULL,
        signal_strength_dbm REAL NOT NULL,
        subsystem_alert TEXT NOT NULL,
        FOREIGN KEY (satellite_id) REFERENCES satellites(satellite_id)
    )
    """)

    # Generate 7 days of hourly telemetry for each satellite
    now = datetime(2026, 11, 23, 12, 0, 0)
    telemetry_records = []

    for sat_id, name, *_ in satellites:
        for hour in range(168): # 7 days * 24 hours
            ts = (now - timedelta(hours=167 - hour)).strftime("%Y-%m-%d %H:%M:%S")
            
            # Default nominal baseline values
            battery_voltage = round(random.uniform(28.0, 31.5), 2)
            battery_temp_c = round(random.uniform(14.0, 22.0), 2)
            solar_current = round(random.uniform(7.5, 11.2), 2)
            gyro_drift = round(random.uniform(0.001, 0.004), 4)
            signal_dbm = round(random.uniform(-75.0, -68.0), 1)
            alert = "NOMINAL"

            # Injected Realistic Anomaly 1: EOS-04 has sudden Battery Undervolt & Temperature Spikes (Last 24h)
            if sat_id == "SAT-ISRO-04" and hour >= 140 and hour <= 150:
                battery_voltage = round(random.uniform(8.4, 11.2), 2) # Severe undervoltage
                battery_temp_c = round(random.uniform(48.0, 56.5), 2)  # Thermal runaway risk
                alert = "BATTERY_UNDERVOLT_AND_OVERHEAT"

            # Injected Realistic Anomaly 2: EMISAT experiences Gyro Attitude Control Drift
            elif sat_id == "SAT-DEF-02" and hour >= 110 and hour <= 118:
                gyro_drift = round(random.uniform(0.12, 0.28), 4) # 50x normal drift
                alert = "GYRO_ATTITUDE_DRIFT"

            # Injected Realistic Anomaly 3: INSAT-3DR Solar Eclipse Shadow Pass
            elif sat_id == "SAT-ISRO-01" and hour in [36, 60, 84, 108, 132]:
                solar_current = round(random.uniform(0.1, 0.4), 2) # Eclipse zero current
                battery_voltage = round(random.uniform(24.5, 26.0), 2) # Drawdown on batteries
                alert = "ECLIPSE_BATTERY_DISCHARGE"

            telemetry_records.append((
                sat_id, ts, battery_voltage, battery_temp_c, solar_current,
                gyro_drift, signal_dbm, alert
            ))

    cursor.executemany("""
    INSERT INTO telemetry (
        satellite_id, timestamp, battery_voltage, battery_temp_c,
        solar_panel_current, gyro_drift_rate, signal_strength_dbm, subsystem_alert
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, telemetry_records)

    conn.commit()
    print(f"Successfully generated database at {db_path} with {len(satellites)} satellites and {len(telemetry_records)} telemetry points.")
    conn.close()

if __name__ == "__main__":
    db_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "satellites.db")
    create_database(db_file)
