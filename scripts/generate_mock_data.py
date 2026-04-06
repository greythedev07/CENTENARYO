"""
CENTENARYO Synthetic Data Generator
====================================

Generates realistic mock data for all database tables:
- users (system users with different roles)
- senior_citizens (senior registry with Filipino names)
- pension_disbursements (quarterly payment records)
- discount_booklets (benefit booklets inventory)
- senior_ids (QR-coded ID cards)
- anomaly_flags (AI-detected suspicious records)
- audit_logs (system activity tracking)
- system_settings (configuration key-value store)

Usage:
    python scripts/generate_mock_data.py
    python scripts/generate_mock_data.py --seniors 200 --output data/mock_data.json
"""

from faker import Faker
import json
import random
import uuid
import hashlib
from datetime import datetime, date, timedelta
from pathlib import Path

fake = Faker()

# Filipino-specific data for realistic names and locations
FILIPINO_SURNAMES = [
    "Reyes", "Cruz", "Santos", "Garcia", "Mendoza", "Torres", "Tomás", "Andrade",
    "De Leon", "Fernando", "Villanueva", "Ramos", "Castillo", "Navarro", "Lorenzo",
    "Bautista", "Jimenez", "Salazar", "Alvarez", "Aquino", "Valdez", "Morales",
    "Del Rosario", "Gonzales", "Rivera", "Perez", "Santiago", "Flores", "Dela Cruz"
]

FILIPINO_GIVEN_NAMES_MALE = [
    "Juan", "Jose", "Antonio", "Manuel", "Carlos", "Roberto", "Francisco", 
    "Pedro", "Miguel", "Ricardo", "Fernando", "Eduardo", "Ramon", "Alberto",
    "Marcelo", "Arturo", "Victor", "Emilio", "Julio", "Rafael", "Gabriel"
]

FILIPINO_GIVEN_NAMES_FEMALE = [
    "Maria", "Ana", "Carmen", "Rosa", "Teresa", "Consuelo", "Luisa", "Carmela",
    "Dolores", "Elena", "Patricia", "Angelica", "Soledad", "Remedios", "Isabel",
    "Margarita", "Cecilia", "Mercedes", "Josefina", "Lourdes", "Imelda"
]

BARANGAYS = [
    "Poblacion", "San Antonio", "Santa Cruz", "San Jose", "San Miguel",
    "San Juan", "San Pedro", "Santa Rosa", "Santo Niño", "San Isidro",
    "Bagong Silang", "Batasan Hills", "Commonwealth", "Holy Spirit", "Payatas",
    "Libis", "Ugong Norte", "Blue Ridge", "White Plains", "Green Meadows"
]

CITIES = [
    "Quezon City", "Manila", "Caloocan", "Pasig", "Taguig", "Makati",
    "Mandaluyong", "San Juan", "Marikina", "Pasay", "Parañaque", "Muntinlupa",
    "Valenzuela", "Malabon", "Navotas", "Las Piñas"
]

SUFFIXES = ["Jr.", "Sr.", "II", "III", "IV"]

FLAG_REASONS = [
    "duplicate_record",
    "suspicious_claim_pattern", 
    "deceased_but_active",
    "age_inconsistency",
    "multiple_booklets",
    "unusual_disbursement_frequency"
]

def hash_password(password: str) -> str:
    """Simple hash for mock passwords"""
    return hashlib.sha256(password.encode()).hexdigest()[:32]

def generate_users():
    """Generate system users with different roles"""
    users = [
        {
            "id": 1,
            "username": "admin",
            "password_hash": hash_password("admin123"),
            "full_name": "System Administrator",
            "role": "admin",
            "is_active": 1,
            "created_at": "2026-01-01 08:00:00",
            "last_login": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        },
        {
            "id": 2,
            "username": "encoder1",
            "password_hash": hash_password("encoder123"),
            "full_name": "Maria Santos",
            "role": "encoder",
            "is_active": 1,
            "created_at": "2026-01-15 09:00:00",
            "last_login": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
        },
        {
            "id": 3,
            "username": "auditor1",
            "password_hash": hash_password("auditor123"),
            "full_name": "Ricardo Cruz",
            "role": "auditor",
            "is_active": 1,
            "created_at": "2026-02-01 08:30:00",
            "last_login": (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d %H:%M:%S")
        },
        {
            "id": 4,
            "username": "viewer1",
            "password_hash": hash_password("viewer123"),
            "full_name": "Elena Reyes",
            "role": "viewer",
            "is_active": 1,
            "created_at": "2026-02-10 10:00:00",
            "last_login": None
        }
    ]
    return users

def generate_senior_citizens(count=100):
    """Generate realistic senior citizen records"""
    seniors = []
    current_year = datetime.now().year
    
    for i in range(1, count + 1):
        # Generate age between 60 and 95
        age = random.randint(60, 95)
        birth_year = current_year - age
        
        # Random birth date
        birth_date = date(birth_year, random.randint(1, 12), random.randint(1, 28))
        
        # Sex and corresponding name
        sex = random.choice(['M', 'F'])
        if sex == 'M':
            first_name = random.choice(FILIPINO_GIVEN_NAMES_MALE)
        else:
            first_name = random.choice(FILIPINO_GIVEN_NAMES_FEMALE)
        
        middle_name = random.choice(FILIPINO_GIVEN_NAMES_MALE + FILIPINO_GIVEN_NAMES_FEMALE) if random.random() > 0.3 else None
        last_name = random.choice(FILIPINO_SURNAMES)
        suffix = random.choice(SUFFIXES) if random.random() > 0.85 else None
        
        # Some seniors are deceased (about 5%)
        vital_status = 'deceased' if random.random() < 0.05 else 'alive'
        date_of_death = None
        is_active = 1
        
        if vital_status == 'deceased':
            # Died within last 2 years
            days_ago = random.randint(30, 730)
            death_date = datetime.now() - timedelta(days=days_ago)
            date_of_death = death_date.strftime("%Y-%m-%d")
            is_active = 0
        
        # Registration date (within last 5 years)
        reg_days_ago = random.randint(0, 1825)
        registration_date = (datetime.now() - timedelta(days=reg_days_ago)).strftime("%Y-%m-%d")
        
        senior = {
            "id": i,
            "unique_identifier": f"OSCA-{current_year}-{i:06d}",
            "first_name": first_name,
            "middle_name": middle_name,
            "last_name": last_name,
            "suffix": suffix,
            "birth_date": birth_date.strftime("%Y-%m-%d"),
            "age": age,
            "sex": sex,
            "address": fake.street_address(),
            "barangay": random.choice(BARANGAYS),
            "city_municipality": random.choice(CITIES),
            "contact_number": f"09{random.randint(100000000, 999999999)}" if random.random() > 0.2 else None,
            "is_indigent": 1 if random.random() < 0.15 else 0,  # 15% indigent
            "vital_status": vital_status,
            "date_of_death": date_of_death,
            "is_active": is_active,
            "registration_date": registration_date,
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "notes": fake.sentence() if random.random() > 0.8 else None
        }
        
        seniors.append(senior)
    
    return seniors

def generate_pension_disbursements(seniors, users):
    """Generate quarterly pension disbursement records"""
    disbursements = []
    current_year = datetime.now().year
    disbursement_id = 1
    
    # Generate for last 2 years
    years = [current_year - 1, current_year]
    
    for senior in seniors:
        # Skip deceased seniors for recent quarters
        if senior["vital_status"] == "deceased":
            continue
            
        for year in years:
            for quarter in range(1, 5):
                # Not all seniors get all quarters (some delays, some issues)
                if random.random() < 0.9:  # 90% have record
                    # Status distribution
                    status_roll = random.random()
                    if status_roll < 0.75:
                        status = "released"
                        released_by = random.choice([u["id"] for u in users])
                    elif status_roll < 0.95:
                        status = "pending"
                        released_by = None
                    else:
                        status = "cancelled"
                        released_by = None
                    
                    # Disbursement date within quarter
                    month = (quarter - 1) * 3 + random.randint(1, 3)
                    day = random.randint(1, 28)
                    disbursement_date = date(year, month, day)
                    
                    disbursement = {
                        "id": disbursement_id,
                        "senior_id": senior["id"],
                        "quarter": quarter,
                        "year": year,
                        "amount": round(random.uniform(1500, 2000), 2),  # Quarterly amount
                        "disbursement_date": disbursement_date.strftime("%Y-%m-%d"),
                        "status": status,
                        "released_by": released_by,
                        "release_notes": f"Q{quarter} {year} pension" if status == "released" else None,
                        "created_at": disbursement_date.strftime("%Y-%m-%d %H:%M:%S")
                    }
                    
                    disbursements.append(disbursement)
                    disbursement_id += 1
    
    return disbursements

def generate_discount_booklets(seniors):
    """Generate discount booklet records"""
    booklets = []
    current_year = datetime.now().year
    
    for i, senior in enumerate(seniors, 1):
        # Most seniors have booklets
        if random.random() < 0.95:
            issue_date = datetime.strptime(senior["registration_date"], "%Y-%m-%d")
            
            # Some have replacements
            replacements = random.randint(0, 2)
            last_replacement = None
            
            if replacements > 0:
                days_after = random.randint(180, 1095)  # 6 months to 3 years
                last_replacement = (issue_date + timedelta(days=days_after)).strftime("%Y-%m-%d")
            
            # Expiry date (3 years from issue or last replacement)
            base_date = datetime.strptime(last_replacement, "%Y-%m-%d") if last_replacement else issue_date
            expiry_date = (base_date + timedelta(days=1095)).strftime("%Y-%m-%d")
            
            booklet = {
                "id": i,
                "serial_number": f"BK-{current_year}-{str(i).zfill(6)}",
                "senior_id": senior["id"],
                "issue_date": issue_date.strftime("%Y-%m-%d"),
                "expiry_date": expiry_date,
                "replacements_count": replacements,
                "last_replacement_date": last_replacement,
                "is_active": 1 if senior["is_active"] == 1 else 0,
                "notes": None
            }
            
            booklets.append(booklet)
    
    return booklets

def generate_senior_ids(seniors, users):
    """Generate QR-coded ID cards"""
    ids = []
    current_year = datetime.now().year
    
    for i, senior in enumerate(seniors, 1):
        # Most seniors have IDs
        if random.random() < 0.98:
            issue_date = datetime.strptime(senior["registration_date"], "%Y-%m-%d")
            
            # Some have been replaced
            replacement_reason = None
            if random.random() < 0.1:
                replacement_reason = random.choice([
                    "Lost",
                    "Damaged",
                    "Information update",
                    "Expired"
                ])
            
            # Expiry date (5 years from issue)
            expiry_date = (issue_date + timedelta(days=1825)).strftime("%Y-%m-%d")
            
            senior_id = {
                "id": i,
                "senior_id": senior["id"],
                "qr_code": str(uuid.uuid4()),
                "issue_date": issue_date.strftime("%Y-%m-%d"),
                "expiry_date": expiry_date,
                "printed_by": random.choice([u["id"] for u in users]),
                "is_active": 1 if senior["is_active"] == 1 else 0,
                "replacement_reason": replacement_reason
            }
            
            ids.append(senior_id)
    
    return ids

def generate_anomaly_flags(seniors, users):
    """Generate AI-detected or manually flagged anomalies"""
    flags = []
    flag_id = 1
    
    # Create flags for about 10% of seniors
    flagged_seniors = random.sample(seniors, min(len(seniors) // 10, 50))
    
    for senior in flagged_seniors:
        risk_score = round(random.uniform(0.6, 0.95), 2)
        detected_by = "AI" if random.random() < 0.7 else random.choice([u["username"] for u in users])
        
        # Detection date (within last 6 months)
        days_ago = random.randint(1, 180)
        detection_date = datetime.now() - timedelta(days=days_ago)
        
        # Resolution status
        resolution_roll = random.random()
        if resolution_roll < 0.3:
            resolution = "verified_clean"
            reviewed_by = random.choice([u["id"] for u in users])
            review_date = detection_date + timedelta(days=random.randint(1, 30))
        elif resolution_roll < 0.6:
            resolution = "confirmed_fraud"
            reviewed_by = random.choice([u["id"] for u in users])
            review_date = detection_date + timedelta(days=random.randint(1, 30))
        else:
            resolution = "pending"
            reviewed_by = None
            review_date = None
        
        flag = {
            "id": flag_id,
            "senior_id": senior["id"],
            "flag_reason": random.choice(FLAG_REASONS),
            "risk_score": risk_score,
            "detected_by": detected_by,
            "detection_date": detection_date.strftime("%Y-%m-%d %H:%M:%S"),
            "reviewed_by": reviewed_by,
            "review_date": review_date.strftime("%Y-%m-%d %H:%M:%S") if review_date else None,
            "resolution": resolution,
            "resolution_notes": fake.sentence() if resolution != "pending" else None
        }
        
        flags.append(flag)
        flag_id += 1
    
    return flags

def generate_audit_logs(users, seniors, count=200):
    """Generate audit log entries"""
    logs = []
    actions = ["CREATE", "UPDATE", "DELETE", "LOGIN", "LOGOUT", "PAYROLL_GENERATE", "ID_PRINT"]
    tables = ["senior_citizens", "pension_disbursements", "discount_booklets", "senior_ids", "users"]
    
    for i in range(1, count + 1):
        user = random.choice(users)
        action = random.choice(actions)
        
        days_ago = random.randint(0, 365)
        timestamp = datetime.now() - timedelta(days=days_ago, hours=random.randint(0, 23))
        
        table_name = random.choice(tables) if action in ["CREATE", "UPDATE", "DELETE"] else None
        record_id = random.randint(1, len(seniors)) if table_name else None
        
        log = {
            "id": i,
            "user_id": user["id"],
            "action": action,
            "table_name": table_name,
            "record_id": record_id,
            "old_values": json.dumps({"status": "pending"}) if action == "UPDATE" else None,
            "new_values": json.dumps({"status": "released"}) if action == "UPDATE" else None,
            "ip_address": f"192.168.1.{random.randint(1, 255)}",
            "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        logs.append(log)
    
    return logs

def generate_system_settings(users):
    """Generate system configuration settings"""
    settings = [
        {
            "key": "pension_amount",
            "value": "500.00",
            "description": "Default monthly pension amount per senior",
            "updated_at": "2026-01-01 08:00:00",
            "updated_by": 1
        },
        {
            "key": "current_quarter",
            "value": str((datetime.now().month - 1) // 3 + 1),
            "description": "Current quarter for payroll generation",
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "updated_by": 1
        },
        {
            "key": "current_year",
            "value": str(datetime.now().year),
            "description": "Current year",
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "updated_by": 1
        },
        {
            "key": "auto_anomaly_detection",
            "value": "true",
            "description": "Enable automatic AI anomaly scanning",
            "updated_at": "2026-01-01 08:00:00",
            "updated_by": 1
        },
        {
            "key": "system_name",
            "value": "CENTENARYO",
            "description": "System name displayed in UI",
            "updated_at": "2026-01-01 08:00:00",
            "updated_by": 1
        },
        {
            "key": "backup_retention_days",
            "value": "30",
            "description": "Number of days to keep database backups",
            "updated_at": "2026-01-01 08:00:00",
            "updated_by": 1
        }
    ]
    return settings

def insert_into_sqlite(data: dict, db_path: str = "data/centenaryo.db"):
    """Insert generated data into SQLite database"""
    import sqlite3
    
    print(f"\nInserting data into SQLite database: {db_path}")
    
    # Ensure data directory exists
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Clear existing data (in reverse order to respect foreign keys)
        cursor.execute("DELETE FROM audit_logs")
        cursor.execute("DELETE FROM anomaly_flags")
        cursor.execute("DELETE FROM senior_ids")
        cursor.execute("DELETE FROM discount_booklets")
        cursor.execute("DELETE FROM pension_disbursements")
        cursor.execute("DELETE FROM senior_citizens")
        cursor.execute("DELETE FROM system_settings")
        cursor.execute("DELETE FROM users")
        print("  Cleared existing data")
        
        # Insert users
        for user in data["users"]:
            cursor.execute("""
                INSERT INTO users (id, username, password_hash, full_name, role, is_active, created_at, last_login)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (user["id"], user["username"], user["password_hash"], user["full_name"], 
                  user["role"], user["is_active"], user["created_at"], user["last_login"]))
        print(f"  Inserted {len(data['users'])} users")
        
        # Insert senior citizens
        for senior in data["senior_citizens"]:
            cursor.execute("""
                INSERT INTO senior_citizens (id, unique_identifier, first_name, middle_name, last_name, 
                    suffix, birth_date, age, sex, address, barangay, city_municipality, contact_number,
                    is_indigent, vital_status, date_of_death, is_active, registration_date, last_updated, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (senior["id"], senior["unique_identifier"], senior["first_name"], senior["middle_name"],
                  senior["last_name"], senior["suffix"], senior["birth_date"], senior["age"], senior["sex"],
                  senior["address"], senior["barangay"], senior["city_municipality"], senior["contact_number"],
                  senior["is_indigent"], senior["vital_status"], senior["date_of_death"], senior["is_active"],
                  senior["registration_date"], senior["last_updated"], senior["notes"]))
        print(f"  Inserted {len(data['senior_citizens'])} senior citizens")
        
        # Insert pension disbursements
        for d in data["pension_disbursements"]:
            cursor.execute("""
                INSERT INTO pension_disbursements (id, senior_id, quarter, year, amount, 
                    disbursement_date, status, released_by, release_notes, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (d["id"], d["senior_id"], d["quarter"], d["year"], d["amount"],
                  d["disbursement_date"], d["status"], d["released_by"], d["release_notes"], d["created_at"]))
        print(f"  Inserted {len(data['pension_disbursements'])} pension disbursements")
        
        # Insert discount booklets
        for b in data["discount_booklets"]:
            cursor.execute("""
                INSERT INTO discount_booklets (id, serial_number, senior_id, issue_date, expiry_date,
                    replacements_count, last_replacement_date, is_active, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (b["id"], b["serial_number"], b["senior_id"], b["issue_date"], b["expiry_date"],
                  b["replacements_count"], b["last_replacement_date"], b["is_active"], b["notes"]))
        print(f"  Inserted {len(data['discount_booklets'])} discount booklets")
        
        # Insert senior IDs
        for sid in data["senior_ids"]:
            cursor.execute("""
                INSERT INTO senior_ids (id, senior_id, qr_code, issue_date, expiry_date,
                    printed_by, is_active, replacement_reason)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (sid["id"], sid["senior_id"], sid["qr_code"], sid["issue_date"], sid["expiry_date"],
                  sid["printed_by"], sid["is_active"], sid["replacement_reason"]))
        print(f"  Inserted {len(data['senior_ids'])} senior IDs")
        
        # Insert anomaly flags
        for flag in data["anomaly_flags"]:
            cursor.execute("""
                INSERT INTO anomaly_flags (id, senior_id, flag_reason, risk_score, detected_by,
                    detection_date, reviewed_by, review_date, resolution, resolution_notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (flag["id"], flag["senior_id"], flag["flag_reason"], flag["risk_score"],
                  flag["detected_by"], flag["detection_date"], flag["reviewed_by"], 
                  flag["review_date"], flag["resolution"], flag["resolution_notes"]))
        print(f"  Inserted {len(data['anomaly_flags'])} anomaly flags")
        
        # Insert audit logs
        for log in data["audit_logs"]:
            cursor.execute("""
                INSERT INTO audit_logs (id, user_id, action, table_name, record_id, old_values, new_values, ip_address, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (log["id"], log["user_id"], log["action"], log["table_name"], log["record_id"],
                  log["old_values"], log["new_values"], log["ip_address"], log["timestamp"]))
        print(f"  Inserted {len(data['audit_logs'])} audit logs")
        
        # Insert system settings
        for setting in data["system_settings"]:
            cursor.execute("""
                INSERT INTO system_settings (key, value, description, updated_at, updated_by)
                VALUES (?, ?, ?, ?, ?)
            """, (setting["key"], setting["value"], setting["description"], 
                  setting["updated_at"], setting["updated_by"]))
        print(f"  Inserted {len(data['system_settings'])} system settings")
        
        conn.commit()
        print("\n✓ Database insertion complete!")
        
    except sqlite3.Error as e:
        print(f"\n✗ Database error: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

def main():
    """Generate all mock data and save to JSON files and/or SQLite database"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate CENTENARYO mock data")
    parser.add_argument("--seniors", type=int, default=100, help="Number of seniors to generate")
    parser.add_argument("--output", type=str, default="frontend/data", help="Output directory for JSON files")
    parser.add_argument("--db", type=str, default="data/centenaryo.db", help="SQLite database path (set to empty to skip DB insertion)")
    args = parser.parse_args()
    
    print(f"Generating mock data for CENTENARYO...")
    print(f"Seniors to generate: {args.seniors}")
    
    # Ensure output directory exists
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate data in order (respecting foreign keys)
    print("Generating users...")
    users = generate_users()
    
    print(f"Generating {args.seniors} senior citizens...")
    seniors = generate_senior_citizens(args.seniors)
    
    print("Generating pension disbursements...")
    disbursements = generate_pension_disbursements(seniors, users)
    
    print("Generating discount booklets...")
    booklets = generate_discount_booklets(seniors)
    
    print("Generating senior IDs...")
    senior_ids = generate_senior_ids(seniors, users)
    
    print("Generating anomaly flags...")
    flags = generate_anomaly_flags(seniors, users)
    
    print("Generating audit logs...")
    logs = generate_audit_logs(users, seniors, count=min(args.seniors * 2, 500))
    
    print("Generating system settings...")
    settings = generate_system_settings(users)
    
    # Save to JSON files
    data = {
        "users": users,
        "senior_citizens": seniors,
        "pension_disbursements": disbursements,
        "discount_booklets": booklets,
        "senior_ids": senior_ids,
        "anomaly_flags": flags,
        "audit_logs": logs,
        "system_settings": settings
    }
    
    # Save combined file
    combined_file = output_dir / "mock_data.json"
    with open(combined_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    # Save individual files for each table
    for table_name, records in data.items():
        file_path = output_dir / f"{table_name}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=2, ensure_ascii=False)
        print(f"  - {table_name}: {len(records)} records -> {file_path}")
    
    print(f"\n✓ JSON files created!")
    print(f"  Combined file: {combined_file}")
    print(f"  Individual files in: {output_dir}/")
    
    # Insert into SQLite database if path provided
    if args.db:
        try:
            insert_into_sqlite(data, args.db)
        except Exception as e:
            print(f"\n⚠ Warning: Could not insert into database: {e}")
            print("   (JSON files were still created successfully)")
    
    # Print summary
    print("\nSummary:")
    for table_name, records in data.items():
        print(f"  {table_name}: {len(records)} records")

if __name__ == "__main__":
    main()