import sqlite3
from collections import defaultdict
import xml.etree.ElementTree as ET
import feedparser
import requests
import os

# Directory to save downloaded episodes
download_directory = 'downloaded_podcasts'

# Ensure the download directory exists
if not os.path.exists(download_directory):
    os.makedirs(download_directory)

# Connect to your Podcast Addict database
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Retrieve the episodes you've listened to
query = """
SELECT episodes.name AS episode_name, episodes.guid AS episode_guid, episodes.podcast_id
FROM episodes
WHERE episodes.seen_status = 1;
"""
cursor.execute(query)
listened_episodes = cursor.fetchall()

# Retrieve podcast IDs and their RSS URLs
cursor.execute("SELECT _id, rssUrl FROM podcasts;")
podcast_data = cursor.fetchall()
podcast_dict = {podcast_id: rss_url for podcast_id, rss_url in podcast_data}

conn.close()

# Parse the OPML file
tree = ET.parse('podcasts.opml')
root = tree.getroot()

# Extract RSS feed URLs
opml_rss_urls = []
for outline in root.iter('outline'):
    rss_url = outline.get('xmlUrl')
    if rss_url:
        opml_rss_urls.append(rss_url)

# Create a set for faster lookup
opml_rss_set = set(opml_rss_urls)

# Prepare a list to hold episodes to download
episodes_to_download = []

for episode_name, episode_guid, podcast_id in listened_episodes:
    rss_url = podcast_dict.get(podcast_id)
    if rss_url and rss_url in opml_rss_set:
        episodes_to_download.append({
            'episode_name': episode_name,
            'episode_guid': episode_guid,
            'rss_url': rss_url
        })


# Group episodes by RSS feed URL
episodes_by_rss = defaultdict(list)
for episode in episodes_to_download:
    episodes_by_rss[episode['rss_url']].append(episode)

for rss_url, episodes in episodes_by_rss.items():
    # Parse the RSS feed
    feed = feedparser.parse(rss_url)
    podcast_title = feed.feed.title.replace('/', '_').replace('\\', '_')
    print(f"Processing podcast: {podcast_title}")

    # Create a directory for each podcast
    podcast_dir = os.path.join(download_directory, podcast_title)
    if not os.path.exists(podcast_dir):
        os.makedirs(podcast_dir)

    # Map episode GUIDs to the episodes you've listened to
    listened_guids = {ep['episode_guid']: ep for ep in episodes}

    # Iterate over episodes in the feed
    for entry in feed.entries:
        entry_guid = entry.get('guid', entry.get('id'))
        if not entry_guid:
            continue

        if entry_guid in listened_guids:
            episode_info = listened_guids[entry_guid]
            episode_name = episode_info['episode_name'].replace('/', '_').replace('\\', '_')

            # Find the audio link
            audio_url = None
            for link in entry.enclosures:
                if 'audio' in link.type or link.type.startswith('audio/'):
                    audio_url = link.href
                    break
            if not audio_url:
                print(f"No audio link found for episode: {episode_name}")
                continue

            # Define the filename
            file_extension = audio_url.split('.')[-1].split('?')[0]
            filename = f"{episode_name}.{file_extension}"
            file_path = os.path.join(podcast_dir, filename)

            # Check if the file already exists
            if os.path.exists(file_path):
                print(f"Episode already downloaded: {episode_name}")
                continue

            # Download the audio file
            print(f"Downloading: {episode_name}")
            try:
                response = requests.get(audio_url, stream=True)
                response.raise_for_status()
                with open(file_path, 'wb') as f:
                    for chunk in response.iter_content(1024):
                        f.write(chunk)
                print(f"Downloaded: {episode_name}")
            except requests.exceptions.RequestException as e:
                print(f"Failed to download {episode_name}: {e}")
