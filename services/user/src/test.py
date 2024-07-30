from core.user import get_all_users_from_userpool
from utils.connect import run_sql_file

# print(get_all_users_from_userpool("us-east-2_Q3EBmTsTd"))

# arn:aws:sts::058264409130:assumed-role/AWSReservedSSO_AdminAccess_809e87bef64b1be7/tietje.n

print(run_sql_file("db/invitesdb.sql"))
