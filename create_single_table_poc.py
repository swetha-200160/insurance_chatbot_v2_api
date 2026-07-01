

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

# UAE-specific realistic data
UAE_PATIENTS = [
    {"name": "Mohammed Al Ketbi", "emirates_id": "784-1985-4455667-1"},
    {"name": "Fatima Al Shamsi", "emirates_id": "784-1990-3344556-2"},
    {"name": "Ali Al Hammadi", "emirates_id": "784-1988-5566778-3"},
    {"name": "Aisha Al Mazrouei", "emirates_id": "784-1992-6677889-4"},
    {"name": "Khalid Al Qasemi", "emirates_id": "784-1983-7788990-5"},
    {"name": "Noora Al Naqbi", "emirates_id": "784-1995-8899001-6"},
    {"name": "Saeed Al Rashdi", "emirates_id": "784-1987-9900112-7"},
    {"name": "Mariam Al Hefeiti", "emirates_id": "784-1993-1122334-8"},
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

def create_table(conn):
    cursor = conn.cursor()
    cursor.execute("""
        DROP TABLE IF EXISTS preauthorizations;
        
        CREATE TABLE preauthorizations (
            request_id VARCHAR(50) PRIMARY KEY,
            customer_id VARCHAR(50) NOT NULL,
            emirates_id VARCHAR(50) NOT NULL,
            member_id VARCHAR(50) NOT NULL,
            policy_number VARCHAR(50) NOT NULL,
            patient_name VARCHAR(200) NOT NULL,
            patient_dob DATE NOT NULL,
            
            provider_id VARCHAR(50) NOT NULL,
            provider_name VARCHAR(200) NOT NULL,
            provider_license VARCHAR(50),
            
            payer_id VARCHAR(50) NOT NULL,
            payer_name VARCHAR(200) NOT NULL,
            
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
        
        CREATE INDEX idx_customer ON preauthorizations(customer_id);
        CREATE INDEX idx_status ON preauthorizations(status);
        CREATE INDEX idx_emirates ON preauthorizations(emirates_id);
    """)
    conn.commit()
    cursor.close()
    print("[SUCCESS] UAE Preauthorization table created")

def generate_data(num_records=100):
    data = []
    
    for i in range(num_records):
        # Generate IDs
        request_id = f"PA-UAE-{datetime.now().strftime('%Y%m')}-{str(i+1).zfill(4)}"
        customer_id = f"CUS{str(random.randint(1, 999999)).zfill(6)}"
        policy_number = f"POL-{random.randint(100000, 999999)}"
        member_id = f"INS-{random.randint(100000, 999999)}"
        
        # Patient info
        patient = random.choice(UAE_PATIENTS)
        patient_name = patient["name"]
        emirates_id = patient["emirates_id"]
        patient_dob = datetime.now() - timedelta(days=random.randint(25*365, 65*365))
        
        # Provider
        provider_id = f"PROV{str(random.randint(1, 99999)).zfill(5)}"
        provider_name = f"Dr. {fake.name()} - {fake.city()} Medical Center"
        provider_license = f"DH-{random.randint(10000, 99999)}"
        
        # Payer
        payers = [("DAMAN", "Daman Insurance"), ("AXAGULF", "AXA Gulf"), ("MEDNET", "Mednet UAE")]
        payer_id, payer_name = random.choice(payers)
        
        # Request type
        is_medication = random.random() > 0.6  # 40% medication, 60% procedure
        
        if is_medication:
            request_type = "MEDICATION"
            med = random.choice(MEDICATIONS)
            procedure_details = None
            medication_details = {
                "drug_name": med["name"],
                "dosage": f"{random.randint(20, 50)}mg",
                "frequency": "Weekly" if "Humira" in med["name"] or "Enbrel" in med["name"] else "Monthly",
                "duration_weeks": random.choice([4, 8, 12, 24]),
                "condition": med["condition"],
                "type": med["type"]
            }
            requested_service = f"Specialized Medication Authorization - {med['type']}"
            estimated_cost = med["cost_per_unit"] * medication_details["duration_weeks"]
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
            requested_service = f"Outpatient Procedure - {proc['type']}"
            estimated_cost = random.randint(*proc["cost_range"])
        
        # Status
        status = random.choices(
            ["PENDING", "APPROVED", "DENIED", "PARTIALLY_APPROVED"],
            weights=[30, 45, 15, 10]
        )[0]
        
        # Decision details
        status_reason = None
        approved_cost = None
        approval_number = None
        
        if status == "APPROVED":
            approved_cost = estimated_cost
            approval_number = f"APR-{random.randint(100000, 999999)}"
        elif status == "DENIED":
            status_reason = random.choice(list(DENIAL_REASONS.values()))
            approved_cost = 0
        elif status == "PARTIALLY_APPROVED":
            approved_cost = round(estimated_cost * random.uniform(0.4, 0.7), 2)
            approval_number = f"APR-{random.randint(100000, 999999)}"
            status_reason = "Limited approval per policy guidelines"
        
        decision_date = None
        if status != "PENDING":
            decision_date = datetime.now() - timedelta(days=random.randint(3, 45))
        
        data.append({
            'request_id': request_id,
            'customer_id': customer_id,
            'emirates_id': emirates_id,
            'member_id': member_id,
            'policy_number': policy_number,
            'patient_name': patient_name,
            'patient_dob': patient_dob,
            'provider_id': provider_id,
            'provider_name': provider_name,
            'provider_license': provider_license,
            'payer_id': payer_id,
            'payer_name': payer_name,
            'request_type': request_type,
            'urgency': random.choices(["ROUTINE", "URGENT"], weights=[80, 20])[0],
            'requested_service': requested_service,
            'procedure_details': json.dumps(procedure_details) if procedure_details else None,
            'medication_details': json.dumps(medication_details) if medication_details else None,
            'clinical_justification': fake.paragraph(nb_sentences=5),
            'estimated_cost': estimated_cost,
            'approved_cost': approved_cost,
            'status': status,
            'status_reason': status_reason,
            'approval_number': approval_number,
            'requested_date': datetime.now() - timedelta(days=random.randint(7, 90)),
            'decision_date': decision_date,
        })
    
    return data

def insert_data(conn, data):
    cursor = conn.cursor()
    
    for record in data:
        cursor.execute("""
            INSERT INTO preauthorizations 
            (request_id, customer_id, emirates_id, member_id, policy_number, patient_name,
             patient_dob, provider_id, provider_name, provider_license, payer_id, payer_name,
             request_type, urgency, requested_service, procedure_details, medication_details,
             clinical_justification, estimated_cost, approved_cost, status, status_reason,
             approval_number, requested_date, decision_date)
            VALUES (%(request_id)s, %(customer_id)s, %(emirates_id)s, %(member_id)s,
                    %(policy_number)s, %(patient_name)s, %(patient_dob)s, %(provider_id)s,
                    %(provider_name)s, %(provider_license)s, %(payer_id)s, %(payer_name)s,
                    %(request_type)s, %(urgency)s, %(requested_service)s, %(procedure_details)s,
                    %(medication_details)s, %(clinical_justification)s, %(estimated_cost)s,
                    %(approved_cost)s, %(status)s, %(status_reason)s, %(approval_number)s,
                    %(requested_date)s, %(decision_date)s)
        """, record)
    
    conn.commit()
    cursor.close()
    print(f"[SUCCESS] Inserted {len(data)} UAE preauthorization records")

def run_demo_queries(conn):
    cursor = conn.cursor()
    
    print("\n" + "="*70)
    print("UAE PREAUTHORIZATION POC - SAMPLE DATA")
    print("="*70)
    
    # Sample pending requests
    cursor.execute("""
        SELECT request_id, patient_name, emirates_id, requested_service,
               status, estimated_cost, payer_name
        FROM preauthorizations
        WHERE status = 'PENDING'
        LIMIT 3
    """)
    print("\n1. PENDING REQUESTS (Your Format):")
    for row in cursor.fetchall():
        print(f"""
   Request#: {row[0]}
   Patient: {row[1]} (Emirates ID: {row[2]})
   Service: {row[3]}
   Payer: {row[6]}
   Cost: AED {row[5]:,.2f}
   Status: {row[4]}
   """)
    
    # Denied with reasons
    cursor.execute("""
        SELECT request_id, patient_name, status_reason, approved_cost
        FROM preauthorizations
        WHERE status = 'DENIED'
        LIMIT 3
    """)
    print("\n2. DENIED REQUESTS WITH REASONS:")
    for row in cursor.fetchall():
        print(f"   {row[0]} | {row[1][:20]:<20} | AED {row[3]:>8,.2f} | {row[2][:50]}...")
    
    cursor.close()

def main():
    try:
        # Connect
        print("Connecting to PostgreSQL...")
        conn = psycopg2.connect(**DB_CONFIG)
        
        # Create table
        create_table(conn)
        
        # Generate and insert data
        data = generate_data(num_records=100)
        insert_data(conn, data)
        
        # Run demo queries
        run_demo_queries(conn)
        
        # Final stats
        cursor = conn.cursor()
        cursor.execute("SELECT status, COUNT(*) FROM preauthorizations GROUP BY status")
        stats = cursor.fetchall()
        print("\n3. FINAL STATUS DISTRIBUTION:")
        for status, count in stats:
            print(f"   {status:<15} {count:>3} records")
        cursor.close()
        
        conn.close()
        print("\n[SUCCESS] UAE Preauthorization POC Database ready!")

    except Exception as e:
        print(f"[ERROR] Error: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()

if __name__ == "__main__":
    fake = __import__('faker').Faker()  # Lazy import to avoid dependency issues
    main()