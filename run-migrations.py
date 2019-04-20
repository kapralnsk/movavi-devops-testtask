import argparse
from datetime import datetime
import os
import shutil

def safe_system_call(command):
    """
    makes os.system() call,
    but raises exceptions on non-zero exit codes
    """
    result = os.system(command)
    if result: # non-zero exit code
        raise OSError()
    return result

class DBOps():
    def __init__(self, db_service_name='website_postgres-master'):
        self.db_container = safe_system_call('docker ps --format "{{.Names}}" --filter "name={}"'.format(db_service_name))
        self.db_name = self.exec_in_container("cat /run/secrets/postgres-user")

    def rollback_db(self, dump_name):
        self.exec_in_container('psql -U {db_name} {db_name} -c "drop owned by {db_name} cascade;"'.format(db_name=self.db_name))
        self.exec_in_container("psql -U {db_name} {db_name} < /var/lib/postgres/data/{dump_name}".format(db_name = self.db_name, dump_name=dump_name))
    
    def exec_in_container(self, command, container=None):
        container = self.db_container if not container else container
        return safe_system_call('"docker exec -t {container} /bin/bash -c "{command}"'.format(container=container, command=command))

    def cleanup(self, dump_name):
        shutil.move(
            "/var/lib/docker/volumes/website_postgres-data/{}".format(dump_name),
            "/tmp/{}".format(dump_name)
        )

    def migrate_db(self):
        timestamp = datetime.now().timestamp()
        dump_name = "{db_name}-{timestamp}.sql".format(db_name=self.db_name, timestamp=timestamp)
        self.exec_in_container("pg_dump -O -U \$(cat /run/secrets/postgres-user) \$(cat /run/secrets/postgres-user) > /var/lib/postgres/data/{}".format(dump_name))
        dashboard_container = safe_system_call('docker ps --format "{{.Names}}" --filter "name=web_dashboard"')
        try:
            self.exec_in_container("migrate", container=dashboard_container)
        except OSError:
            self.rollback_db(dump_name)
            raise Exception("migration ended with error")
        self.cleanup(dump_name)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--rollback-to', dest='rollback_to')
    db_ops = DBOps()
    args = parser.parse_args()
    if args.rollback_to:
        db_ops.rollback_db(args.rollback_to)
    else:
        db_ops.migrate_db()
