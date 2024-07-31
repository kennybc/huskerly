

def register_org(org_name, creator_email):
    conn = connect_to_messages_database()
    cursor = conn.cursor()
    org_id = None
    try:
        cursor.execute(
            """
            INSERT INTO organizations (name, created_by_email, lead_admin_email)
            VALUES (%s, %s, %s)
            RETURNING id;
            """, (org_name, creator_email, creator_email))
        # need to add org_id to user table in cognito!!!!
        org_id = cursor.fetchone()[0]
        conn.commit()
        print(f"organization with id {org_id} created by user {creator_email}")
    except Exception as e:
        print(f"An error occurred: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()
    return org_id
