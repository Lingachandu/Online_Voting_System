import sqlite3
import os
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

def inspect():
    db_path = os.path.join(os.path.dirname(__file__), '..', 'db.sqlite3')
    if not os.path.exists(db_path):
        print(f"Error: db.sqlite3 not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("\n" + "="*80)
    print("🗳️  ONLINE VOTING DATABASE INSPECTION TOOL")
    print("="*80)

    # 1. Inspect Custom Users Table
    print("\n👥 1. REGISTERED USERS (authentication_customuser)")
    print("-"*95)
    print(f"{'ID':<4} | {'Phone Number':<12} | {'Role':<6} | {'State':<5} | {'Aadhaar Number':<14} | {'Verified':<8} | {'Face Image':<10}")
    print("-"*95)
    try:
        cursor.execute("SELECT id, phone_number, role, state, aadhaar_number, is_verified, face_image FROM authentication_customuser")
        rows = cursor.fetchall()
        for row in rows:
            state_val = row[3] if row[3] else "-"
            aadhaar_val = row[4] if row[4] else "-"
            verified_val = "Yes" if row[5] else "No"
            face_val = "[Captured]" if row[6] else "[None]"
            print(f"{row[0]:<4} | {row[1]:<12} | {row[2]:<6} | {state_val:<5} | {aadhaar_val:<14} | {verified_val:<8} | {face_val:<10}")
    except Exception as e:
        print(f"Error reading users: {e}")

    # 2. Inspect Elections
    print("\n🗳️ 2. ACTIVE ELECTIONS (elections_election)")
    print("-"*80)
    print(f"{'ID':<4} | {'Election Title':<30} | {'State':<5} | {'Active':<6}")
    print("-"*80)
    try:
        cursor.execute("SELECT id, title, state, is_active FROM elections_election")
        rows = cursor.fetchall()
        for row in rows:
            active_val = "Yes" if row[3] else "No"
            print(f"{row[0]:<4} | {row[1]:<30} | {row[2]:<5} | {active_val:<6}")
    except Exception as e:
        print(f"Error reading elections: {e}")

    # 3. Inspect Candidates
    print("\n👤 3. CANDIDATES / LEADERS (elections_candidate)")
    print("-"*80)
    print(f"{'ID':<4} | {'Candidate Name':<20} | {'Party Name':<20} | {'Symbol':<6} | {'Tally':<5}")
    print("-"*80)
    try:
        cursor.execute("SELECT id, name, party_affinity, party_symbol, votes_count FROM elections_candidate")
        rows = cursor.fetchall()
        for row in rows:
            print(f"{row[0]:<4} | {row[1]:<20} | {row[2]:<20} | {row[3]:<6} | {row[4]:<5}")
    except Exception as e:
        print(f"Error reading candidates: {e}")

    # 4. Inspect Audit Votes Trail
    print("\n📋 4. VOTER AUDIT TRAIL LOG (voting_vote)")
    print("-"*80)
    print(f"{'Vote ID':<7} | {'Voter ID':<8} | {'Voter Mobile':<12} | {'Voter Aadhaar':<13} | {'Chosen Leader':<20}")
    print("-"*80)
    try:
        cursor.execute("""
            SELECT v.id, u.id, u.phone_number, u.aadhaar_number, c.party_symbol, c.name, c.party_affinity 
            FROM voting_vote v
            JOIN authentication_customuser u ON v.voter_id = u.id
            JOIN elections_candidate c ON v.candidate_id = c.id
        """)
        rows = cursor.fetchall()
        for row in rows:
            aadhaar_val = row[3] if row[3] else "-"
            leader_str = f"{row[4]} {row[5]} ({row[6]})"
            print(f"{row[0]:<7} | {row[1]:<8} | {row[2]:<12} | {aadhaar_val:<13} | {leader_str:<20}")
    except Exception as e:
        print(f"Error reading audit logs: {e}")

    print("\n" + "="*80 + "\n")
    conn.close()

if __name__ == '__main__':
    inspect()
