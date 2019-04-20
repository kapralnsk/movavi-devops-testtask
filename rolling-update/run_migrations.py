import os
import sys

def rollback_db(dump_path):
    print("deleting everything from database")
    print("applying rollback dump")

def migrate_db():
    dump_path = print("creating postgres-master dump")
    migration = print("running migrations from dashboard")
    error = 0
    if not migration:
        rollback_db(dump_path)
        error= "migration ended with error"
    sys.exit(error)
