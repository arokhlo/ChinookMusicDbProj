# create_chinook_tables.py
import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chinook_project.settings')
django.setup()

def create_chinook_tables():
    print("Creating Chinook database tables...")
    
    with connection.cursor() as cursor:
        # Create Artist table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS "Artist" (
                "ArtistId" INTEGER PRIMARY KEY AUTOINCREMENT,
                "Name" VARCHAR(120) NOT NULL
            );
        """)
        print("✓ Artist table created")
        
        # Create Album table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS "Album" (
                "AlbumId" INTEGER PRIMARY KEY AUTOINCREMENT,
                "Title" VARCHAR(160) NOT NULL,
                "ArtistId" INTEGER NOT NULL,
                FOREIGN KEY ("ArtistId") REFERENCES "Artist"("ArtistId") ON DELETE CASCADE
            );
        """)
        print("✓ Album table created")
        
        # Create Track table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS "Track" (
                "TrackId" INTEGER PRIMARY KEY AUTOINCREMENT,
                "Name" VARCHAR(200) NOT NULL,
                "AlbumId" INTEGER,
                "MediaTypeId" INTEGER NOT NULL,
                "GenreId" INTEGER,
                "Composer" VARCHAR(220),
                "Milliseconds" INTEGER NOT NULL,
                "Bytes" INTEGER,
                "UnitPrice" DECIMAL(10,2) NOT NULL,
                FOREIGN KEY ("AlbumId") REFERENCES "Album"("AlbumId") ON DELETE CASCADE
            );
        """)
        print("✓ Track table created")
        
        # Insert sample data
        print("\nInserting sample data...")
        
        # Insert artists
        artists = [
            (1, 'AC/DC'),
            (2, 'Accept'),
            (3, 'Aerosmith'),
            (4, 'Alanis Morissette'),
            (5, 'Alice In Chains'),
            (6, 'Antônio Carlos Jobim'),
            (7, 'Apocalyptica'),
            (8, 'Audioslave'),
            (9, 'BackBeat'),
            (10, 'Billy Cobham')
        ]
        
        for artist_id, name in artists:
            cursor.execute(
                "INSERT OR IGNORE INTO \"Artist\" (\"ArtistId\", \"Name\") VALUES (?, ?)",
                [artist_id, name]
            )
        print(f"✓ {len(artists)} artists inserted")
        
        # Insert albums
        albums = [
            (1, 'For Those About To Rock We Salute You', 1),
            (2, 'Balls to the Wall', 2),
            (3, 'Restless and Wild', 2),
            (4, 'Let There Be Rock', 1),
            (5, 'Big Ones', 3),
            (6, 'Jagged Little Pill', 4),
            (7, 'Facelift', 5),
            (8, 'Warner 25 Anos', 6),
            (9, 'Plays Metallica By Four Cellos', 7),
            (10, 'Audioslave', 8)
        ]
        
        for album_id, title, artist_id in albums:
            cursor.execute(
                "INSERT OR IGNORE INTO \"Album\" (\"AlbumId\", \"Title\", \"ArtistId\") VALUES (?, ?, ?)",
                [album_id, title, artist_id]
            )
        print(f"✓ {len(albums)} albums inserted")
        
        # Insert tracks
        tracks = [
            (1, 'For Those About To Rock (We Salute You)', 1, 1, 1, 'Angus Young, Malcolm Young, Brian Johnson', 343719, 11170334, 0.99),
            (2, 'Balls to the Wall', 2, 2, 1, None, 342562, 5510424, 0.99),
            (3, 'Fast As a Shark', 3, 3, 1, 'F. Baltes, S. Kaufman, U. Dirkscneider & W. Hoffmann', 230619, 3990994, 0.99),
            (4, 'Restless and Wild', 3, 3, 1, 'F. Baltes, R.A. Smith-Diesel, S. Kaufman, U. Dirkscneider & W. Hoffmann', 252051, 4331779, 0.99),
            (5, 'Princess of the Dawn', 3, 3, 1, 'Deaffy & R.A. Smith-Diesel', 375418, 6290521, 0.99),
            (6, 'Put The Finger On You', 1, 1, 1, 'Angus Young, Malcolm Young, Brian Johnson', 205662, 6713451, 0.99),
            (7, 'Lets Get It Up', 1, 1, 1, 'Angus Young, Malcolm Young, Brian Johnson', 233926, 7636561, 0.99),
            (8, 'Inject The Venom', 1, 1, 1, 'Angus Young, Malcolm Young, Brian Johnson', 210834, 6852860, 0.99),
            (9, 'Snowballed', 1, 1, 1, 'Angus Young, Malcolm Young, Brian Johnson', 203102, 6599424, 0.99),
            (10, 'Evil Walks', 1, 1, 1, 'Angus Young, Malcolm Young, Brian Johnson', 263497, 8611245, 0.99)
        ]
        
        for track in tracks:
            cursor.execute(
                """INSERT OR IGNORE INTO "Track" 
                ("TrackId", "Name", "AlbumId", "MediaTypeId", "GenreId", "Composer", "Milliseconds", "Bytes", "UnitPrice") 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                track
            )
        print(f"✓ {len(tracks)} tracks inserted")
    
    print("\n✅ Chinook database setup completed successfully!")

if __name__ == "__main__":
    create_chinook_tables()