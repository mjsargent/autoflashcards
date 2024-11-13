import sqlite3
from collections import defaultdict

# Connect to the database
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Verify 'podcasts' table columns
cursor.execute("PRAGMA table_info(podcasts);")
podcasts_columns = cursor.fetchall()
print("Columns in 'podcasts' table:")
for col in podcasts_columns:
    print(f" - {col[1]} ({col[2]})")

# Verify 'episodes' table columns
cursor.execute("PRAGMA table_info(episodes);")
episodes_columns = cursor.fetchall()
print("\nColumns in 'episodes' table:")
for col in episodes_columns:
    print(f" - {col[1]} ({col[2]})")

# Adjust the query based on available columns and listening status indicator
query = """
SELECT podcasts.name AS podcast_name, episodes.name AS episode_name
FROM episodes
JOIN podcasts ON episodes.podcast_id = podcasts._id
WHERE episodes.seen_status = 1
ORDER BY podcasts.name;
"""

# Execute the query
cursor.execute(query)
results = cursor.fetchall()

# Process and display the results
podcast_episodes = defaultdict(list)
for podcast_name, episode_name in results:
    podcast_episodes[podcast_name].append(episode_name)

for podcast_name in sorted(podcast_episodes):
    print(f"\nPodcast: {podcast_name}")
    for episode_name in podcast_episodes[podcast_name]:
        print(f" - {episode_name}")

# Close the connection
conn.close()
