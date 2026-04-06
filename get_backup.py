import csv
import logging
from dataclasses import dataclass

import pendulum
import requests
import os

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s.%(msecs)03d: %(name)s::%(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

BASE_URL = "https://api.raindrop.io/rest/v1"

CREATE_BACKUP_URL = f"{BASE_URL}/backup"
GET_BACKUP_LIST_URL = f"{BASE_URL}/backups"
DOWNLOAD_BACKUP_URL = f"{BASE_URL}/backup/" + "{id}.csv"

API_KEY = os.environ.get('RAINDROP_API_KEY')

headers = {
    "Authorization": f"Bearer {API_KEY}",
    'Content-Type': 'text/csv'
}


@dataclass
class BackupItem:
    id: str
    created_at: str
    processed: bool = False

    def hours_since_creation(self):
        return pendulum.parse(self.created_at).diff(pendulum.now()).in_hours()


def list_backups() -> BackupItem:
    response = requests.get(GET_BACKUP_LIST_URL, headers=headers)
    content = response.json()['items']

    history = []
    for item in content:
        history.append(BackupItem(item['_id'], item['created']))

    return sorted(history, key=lambda x: x.created_at, reverse=True)


def get_most_recent_new_backup():
    remote_backups = list_backups()

    with open('backups/local_backup_history.csv', 'r') as file:
        reader = csv.DictReader(file)
        local_backup_history = [row['id'] for row in reader]

    if not remote_backups:
        raise Exception('No backups found')

    most_recent_backup = remote_backups[0]

    most_recent_backup.processed = most_recent_backup.id in local_backup_history

    return most_recent_backup


def trigger_new_backup():
    response = requests.get(CREATE_BACKUP_URL, headers=headers)

    response.raise_for_status()

    if bool(response.json()['result']):
        logging.info('Backup creation triggered successfully. Will be downloaded on next run')
    else:
        raise Exception('Backup creation failed')


def mark_backup_as_processed(backup_id):
    with open('backups/local_backup_history.csv', 'a') as file:
        file.write(f'{backup_id},{pendulum.now().format("YYYY-MM-DD HH:mm")} \n')


def write_to_file(content):
    with open('backups/local_backup.csv', 'w') as file:
        file.write(content.decode('utf-8'))


def save_backup(backup: BackupItem):
    response = requests.get(DOWNLOAD_BACKUP_URL.format(id=backup.id), headers=headers)
    write_to_file(response.content)


def backup_remotely():
    pass


def main():
    backup = get_most_recent_new_backup()

    if not backup.processed:
        logging.info('Downloading backup')
        save_backup(backup)
        mark_backup_as_processed(backup.id)
        backup_remotely()
    else:
        logging.info('Latest backup already processed')

    if backup.hours_since_creation() >= 24:
        logging.info(f'Latest backup is {backup.hours_since_creation()} hours old. Creating new backup')
        trigger_new_backup()

    logging.info('Backup run complete')


if __name__ == '__main__':
    main()
