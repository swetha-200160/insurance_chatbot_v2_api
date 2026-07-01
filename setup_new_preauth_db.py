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

# Policy numbers matching authentication
POLICIES = [
    {"policy_number": "POL-776620", "patient_name": "Maria Santos", "emirates_id": "784-1985-6677889-2", "member_id": "INS-992214"},
    {"policy_number": "POL-445521", "patient_name": "Fatima Al Shamsi", "emirates_id": "784-1990-3344556-2", "member_id": "INS-445521"},
    {"policy_number": "POL-667788", "patient_name": "Ali Al Hammadi", "emirates_id": "784-1988-5566778-3", "member_id": "INS-667788"},
    {"policy_number": "POL-889900", "patient_name": "Aisha Al Mazrouei", "emirates_id": "784-1992-6677889-4", "member_id": "INS-889900"},
    {"policy_number": "POL-112233", "patient_name": "Khalid Al Qasemi", "emirates_id": "784-1983-7788990-5", "member_id": "INS-112233"},
]

MEDICATIONS = [
    {"name": "Adalimumab (Humira)", "cost": 6500, "condition": "Rheumatoid Arthritis", "type": "Biologic Injection"},
    {"name": "Etanercept (Enbrel)", "cost": 5800, "condition": "Psoriatic Arthritis", "type": "Biologic Injection"},
    {"name": "Infliximab (Remicade)", "cost": 7200, "condition": "Crohns Disease", "type": "Biologic Infusion"},
    {"name": "Omalizumab (Xolair)", "cost": 3500, "condition": "Severe Asthma", "type": "Monoclonal Antibody"},
    {"name": "Rituximab (MabThera)", "cost": 8500, "condition": "Rheumatoid Arthritis", "type": "Biologic Infusion"},
]

PROCEDURES = [
    {"code": "99213", "name": "Ingrown Toenail Excision", "cost_range": (800, 1200), "type": "Minor Outpatient"},
    {"code": "43235", "name": "Upper GI Endoscopy", "cost_range": (2500, 4000), "type": "Diagnostic"},
    {"code": "66984", "name": "Cataract Surgery", "cost_range": (8000, 12000), "type": "Surgical"},
    {"code": "93306", "name": "Echocardiogram", "cost_range": (1500, 2500), "type": "Diagnostic"},
]

DENIAL_REASONS = [
    "Does not meet medical necessity criteria per DHA/DOH guidelines",
    "Service considered experimental/investigational for this diagnosis",
    "Cost-effective alternative available",
    "Benefit limit exceeded per policy year",
]

def create_table(conn):
    cursor = conn.cursor()

    # Drop and recreate table
    cursor.execute("""
        DROP TABLE IF EXISTS preauthorizations CASCADE;

        CREATE TABLE preauthorizations (
            request_id VARCHAR(50) PRIMARY KEY,
            policy_number VARCHAR(50) NOT NULL,
            emirates_id VARCHAR(50) NOT NULL,
            member_id VARCHAR(50) NOT NULL,
            patient_name VARCHAR(200) NOT NULL,
            patient_dob DATE,

            provider_id VARCHAR(50),
            provider_name VARCHAR(200),
            provider_license VARCHAR(50),

            payer_id VARCHAR(50),
            payer_name VARCHAR(200),

            request_type VARCHAR(50) NOT NULL,
            urgency VARCHAR(20) DEFAULT 'ROUTINE',

            requested_service TEXT NOT NULL,
            procedure_details JSON,
            medication_details JSON,

            clinical_justification TEXT,

            estimated_cost DECIMAL(10,2),
            approved_cost DECIMAL(10,2),

            status VARCHAR(50) NOT NULL,
            status_reason TEXT,
            approval_number VARCHAR(100),

            requested_date DATE NOT NULL,
            decision_date DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE INDEX idx_policy ON preauthorizations(policy_number);
        CREATE INDEX idx_status ON preauthorizations(status);
        CREATE INDEX idx_emirates ON preauthorizations(emirates_id);
    """)
    conn.commit()
    cursor.close()
    print("[SUCCESS] Preauthorization table created with policy_number")

def generate_data(num_records=100):
    """Generate realistic preauthorization data"""
    data = []
    request_counter = 1

    for i in range(num_records):
        # Cycle through policies
        policy = POLICIES[i % len(POLICIES)]

        # Generate request ID
        request_id = f"PA-{datetime.now().strftime('%Y%m')}-{str(request_counter).zfill(4)}"
        request_counter += 1

        # Patient info from policy
        policy_number = policy["policy_number"]
        patient_name = policy["patient_name"]
        emirates_id = policy["emirates_id"]
        member_id = policy["member_id"]
        patient_dob = datetime.now() - timedelta(days=random.randint(25*365, 65*365))

        # Provider info
        provider_id = f"PROV{str(random.randint(1, 99999)).zfill(5)}"
        provider_name = f"Dubai Medical Center - Dr. Ahmed"
        provider_license = f"DH-{random.randint(10000, 99999)}"

        # Payer
        payers = [("DAMAN", "Daman Insurance"), ("AXAGULF", "AXA Gulf"), ("MEDNET", "Mednet UAE")]
        payer_id, payer_name = random.choice(payers)

        # 60% medication, 40% procedure
        is_medication = random.random() > 0.4

        if is_medication:
            request_type = "MEDICATION"
            med = random.choice(MEDICATIONS)

            medication_details = {
                "drug_name": med["name"],
                "dosage": f"{random.randint(20, 50)}mg",
                "frequency": "Weekly" if "Humira" in med["name"] or "Enbrel" in med["name"] else "Monthly",
                "duration_weeks": random.choice([4, 8, 12, 24]),
                "condition": med["condition"],
                "type": med["type"]
            }
            procedure_details = None
            requested_service = f"Biologic Medication Authorization - {med['type']}"
            estimated_cost = med["cost"]

            # Clinical justification for medication
            clinical_justification = f"Patient has persistent {med['condition']} with insufficient response to multiple DMARDs. Biologic therapy recommended as per treatment guidelines."

        else:
            request_type = "PROCEDURE"
            proc = random.choice(PROCEDURES)

            procedure_details = {
                "procedure_code": proc["code"],
                "procedure_name": proc["name"],
                "type": proc["type"],
                "site": random.choice(["Outpatient", "Day Surgery", "Clinic"]),
                "anesthesia": random.choice(["Local", "General", "Conscious Sedation"])
            }
            medication_details = None
            requested_service = f"{proc['type']} Procedure - {proc['name']}"
            estimated_cost = random.randint(*proc["cost_range"])

            # Clinical justification for procedure
            clinical_justification = f"Medically necessary procedure for patient condition. Clinical assessment supports the need for {proc['name']}."

        # Status distribution
        status = random.choices(
            ["PENDING", "APPROVED", "DENIED", "PARTIALLY_APPROVED"],
            weights=[35, 45, 12, 8]
        )[0]

        # Decision details
        status_reason = None
        approved_cost = None
        approval_number = None
        decision_date = None

        if status == "APPROVED":
            approved_cost = estimated_cost
            approval_number = f"APR-{random.randint(100000, 999999)}"
            decision_date = datetime.now() - timedelta(days=random.randint(1, 14))
        elif status == "DENIED":
            status_reason = random.choice(DENIAL_REASONS)
            approved_cost = 0
            decision_date = datetime.now() - timedelta(days=random.randint(1, 14))
        elif status == "PARTIALLY_APPROVED":
            approved_cost = round(estimated_cost * random.uniform(0.5, 0.8), 2)
            approval_number = f"APR-{random.randint(100000, 999999)}"
            status_reason = "Partial approval per policy guidelines - coverage limited"
            decision_date = datetime.now() - timedelta(days=random.randint(1, 14))

        # Requested date
        requested_date = datetime.now() - timedelta(days=random.randint(1, 60))

        data.append({
            'request_id': request_id,
            'policy_number': policy_number,
            'emirates_id': emirates_id,
            'member_id': member_id,
            'patient_name': patient_name,
            'patient_dob': patient_dob,
            'provider_id': provider_id,
            'provider_name': provider_name,
            'provider_license': provider_license,
            'payer_id': payer_id,
            'payer_name': payer_name,
            'request_type': request_type,
            'urgency': random.choices(["ROUTINE", "URGENT"], weights=[85, 15])[0],
            'requested_service': requested_service,
            'procedure_details': json.dumps(procedure_details) if procedure_details else None,
            'medication_details': json.dumps(medication_details) if medication_details else None,
            'clinical_justification': clinical_justification,
            'estimated_cost': estimated_cost,
            'approved_cost': approved_cost,
            'status': status,
            'status_reason': status_reason,
            'approval_number': approval_number,
            'requested_date': requested_date,
            'decision_date': decision_date,
        })

    return data

def insert_data(conn, data):
    cursor = conn.cursor()

    for record in data:
        cursor.execute("""
            INSERT INTO preauthorizations
            (request_id, policy_number, emirates_id, member_id, patient_name, patient_dob,
             provider_id, provider_name, provider_license, payer_id, payer_name,
             request_type, urgency, requested_service, procedure_details, medication_details,
             clinical_justification, estimated_cost, approved_cost, status, status_reason,
             approval_number, requested_date, decision_date)
            VALUES (%(request_id)s, %(policy_number)s, %(emirates_id)s, %(member_id)s,
                    %(patient_name)s, %(patient_dob)s, %(provider_id)s, %(provider_name)s,
                    %(provider_license)s, %(payer_id)s, %(payer_name)s, %(request_type)s,
                    %(urgency)s, %(requested_service)s, %(procedure_details)s,
                    %(medication_details)s, %(clinical_justification)s, %(estimated_cost)s,
                    %(approved_cost)s, %(status)s, %(status_reason)s, %(approval_number)s,
                    %(requested_date)s, %(decision_date)s)
        """, record)

    conn.commit()
    cursor.close()
    print(f"[SUCCESS] Inserted {len(data)} preauthorization records")

def show_sample_data(conn):
    cursor = conn.cursor()

    print("\n" + "="*80)
    print("SAMPLE DATA - Policy POL-776620 (Maria Santos)")
    print("="*80)

    cursor.execute("""
        SELECT request_id, patient_name, emirates_id, requested_service,
               status, estimated_cost, approved_cost, requested_date
        FROM preauthorizations
        WHERE policy_number = 'POL-776620'
        ORDER BY requested_date DESC
        LIMIT 5
    """)

    print("\nYour Preauthorization Requests:")
    for row in cursor.fetchall():
        approved_cost_str = f"{row[6]:,.2f}" if row[6] is not None else "0.00"
        print(f"""
Request ID: {row[0]}
Patient: {row[1]}
Emirates ID: {row[2]}
Service: {row[3]}
Status: {row[4]}
Estimated Cost: AED {row[5]:,.2f}
Approved Cost: AED {approved_cost_str}
Requested Date: {row[7]}
---""")

    # Status distribution
    cursor.execute("""
        SELECT status, COUNT(*)
        FROM preauthorizations
        WHERE policy_number = 'POL-776620'
        GROUP BY status
    """)

    print("\nStatus Summary for POL-776620:")
    for status, count in cursor.fetchall():
        print(f"  {status}: {count} requests")

    cursor.close()

def main():
    try:
        print("Connecting to PostgreSQL...")
        conn = psycopg2.connect(**DB_CONFIG)

        # Create table
        create_table(conn)

        # Generate and insert data
        data = generate_data(num_records=100)
        insert_data(conn, data)

        # Show sample data
        show_sample_data(conn)

        # Final stats
        cursor = conn.cursor()
        cursor.execute("SELECT status, COUNT(*) FROM preauthorizations GROUP BY status ORDER BY status")
        print("\n" + "="*80)
        print("OVERALL STATUS DISTRIBUTION:")
        print("="*80)
        for status, count in cursor.fetchall():
            print(f"  {status:<20} {count:>3} records")
        cursor.close()

        conn.close()

        print("\n[SUCCESS] Database setup complete!")
        print("\nTest Credentials:")
        print("  Policy Number: POL-776620")
        print("  OTP: 12345")
        print("\nSample Queries After Login:")
        print("  - Show my preauth status")
        print("  - What's my latest request")
        print("  - Show approved requests")
        print("  - Show medication preauths")

    except Exception as e:
        print(f"[ERROR] Error: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()

if __name__ == "__main__":
    main()
