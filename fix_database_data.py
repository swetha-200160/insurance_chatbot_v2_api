import psycopg2
import random
from datetime import datetime, timedelta
import json
import os
from dotenv import load_dotenv

_ = load_dotenv(override=True)

# Database connection
DB_CONFIG = {
    "host": os.getenv('POSTGRES_HOST'),
    "database": os.getenv('POSTGRES_DB'),
    "user": os.getenv('POSTGRES_USER'),
    "password": os.getenv('POSTGRES_PASSWORD')
}

# Match customer IDs to the test credentials
CUSTOMER_IDS = ["CUS000001", "CUS000002", "CUS000003", "CUS000004", "CUS000005"]

# UAE-specific realistic data
UAE_PATIENTS = [
    {"name": "Gibson", "emirates_id": "784-1985-4455667-1", "customer_id": "CUS000001"},
    {"name": "Fatima Al Shamsi", "emirates_id": "784-1990-3344556-2", "customer_id": "CUS000002"},
    {"name": "Ali Al Hammadi", "emirates_id": "784-1988-5566778-3", "customer_id": "CUS000003"},
    {"name": "Aisha Al Mazrouei", "emirates_id": "784-1992-6677889-4", "customer_id": "CUS000004"},
    {"name": "Khalid Al Qasemi", "emirates_id": "784-1983-7788990-5", "customer_id": "CUS000005"},
]

PROCEDURES = [
    {"code": "99213", "name": "Ingrown Toenail Excision", "cost_range": (800, 1200), "type": "Minor Outpatient"},
    {"code": "43235", "name": "Upper GI Endoscopy", "cost_range": (2500, 4000), "type": "Diagnostic"},
    {"code": "66984", "name": "Cataract Surgery (Phaco)", "cost_range": (8000, 12000), "type": "Surgical"},
    {"code": "93306", "name": "Echocardiogram", "cost_range": (1500, 2500), "type": "Diagnostic"},
    {"code": "36415", "name": "Incision & Drainage", "cost_range": (600, 1000), "type": "Minor Procedure"},
]

MEDICATIONS = [
    {"name": "Adalimumab (Humira)", "cost_per_unit": 6500, "condition": "Rheumatoid Arthritis", "type": "Biologic Injection"},
    {"name": "Etanercept (Enbrel)", "cost_per_unit": 5800, "condition": "Psoriatic Arthritis", "type": "Biologic Injection"},
    {"name": "Infliximab (Remicade)", "cost_per_unit": 7200, "condition": "Crohns Disease", "type": "Biologic Infusion"},
    {"name": "Omalizumab (Xolair)", "cost_per_unit": 3500, "condition": "Severe Asthma", "type": "Monoclonal Antibody"},
    {"name": "Rituximab (MabThera)", "cost_per_unit": 8500, "condition": "Rheumatoid Arthritis", "type": "Biologic Infusion"},
]

DENIAL_REASONS = {
    "MEDICAL_NECESSITY": "Does not meet medical necessity criteria per DHA/DOH guidelines",
    "EXPERIMENTAL": "Service considered experimental/investigational for this diagnosis",
    "ALTERNATIVE_AVAILABLE": "Cost-effective alternative available (per EML)",
    "FREQUENCY_EXCEEDED": "Benefit limit exceeded per policy year",
    "NOT_COVERED": "Service not covered under Essential Benefits Package",
    "PRIOR_AUTH_MISSING": "Required prior authorization not obtained timely"
}

def update_database():
    """Update existing records to use correct customer IDs"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        print("Updating database records with correct customer IDs...")

        # Get all existing records
        cursor.execute("SELECT request_id FROM preauthorizations ORDER BY created_at")
        records = cursor.fetchall()

        # Update each record with one of the valid customer IDs
        for idx, (request_id,) in enumerate(records):
            # Cycle through customer IDs
            customer_id = CUSTOMER_IDS[idx % len(CUSTOMER_IDS)]
            patient = UAE_PATIENTS[idx % len(UAE_PATIENTS)]

            # Update the record
            cursor.execute("""
                UPDATE preauthorizations
                SET customer_id = %s,
                    emirates_id = %s,
                    patient_name = %s
                WHERE request_id = %s
            """, (customer_id, patient["emirates_id"], patient["name"], request_id))

        conn.commit()

        # Verify the update
        cursor.execute("""
            SELECT customer_id, COUNT(*)
            FROM preauthorizations
            GROUP BY customer_id
            ORDER BY customer_id
        """)

        print("\n[SUCCESS] Database updated!")
        print("\nRecords per customer:")
        for customer_id, count in cursor.fetchall():
            print(f"  {customer_id}: {count} preauth requests")

        # Show sample data for CUS000002
        print("\n" + "="*70)
        print("Sample data for CUS000002:")
        print("="*70)
        cursor.execute("""
            SELECT request_id, patient_name, emirates_id, requested_service,
                   status, estimated_cost, requested_date
            FROM preauthorizations
            WHERE customer_id = 'CUS000002'
            ORDER BY requested_date DESC
            LIMIT 5
        """)

        for row in cursor.fetchall():
            print(f"""
Request ID: {row[0]}
Patient: {row[1]} (Emirates ID: {row[2]})
Service: {row[3]}
Status: {row[4]}
Estimated Cost: AED {row[5]:,.2f}
Requested Date: {row[6]}
---""")

        cursor.close()
        conn.close()

        print("\n[SUCCESS] You can now test with:")
        print("  Customer ID: CUS000002")
        print("  OTP: 12345")
        print("  Query: 'show my preauth requests'")

    except Exception as e:
        print(f"[ERROR] Error updating database: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()

if __name__ == "__main__":
    update_database()
