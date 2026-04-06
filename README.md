# raindrop-tools

Script to back up your [Raindrop.io](https://raindrop.io) bookmarks to CSV.

Checks the Raindrop API for the most recent backup, downloads it if it's new, and triggers a fresh backup if the latest one is more than 24 hours old.

## Usage

```bash
export RAINDROP_API_KEY=your_api_key
python get_backup.py
```

Backups land in `backups/local_backup.csv`. A history file tracks what's already been downloaded so it doesn't re-fetch.

## Getting an API key

Go to [Raindrop.io App Management](https://app.raindrop.io/settings/integrations) → Create new app → Generate test token.
