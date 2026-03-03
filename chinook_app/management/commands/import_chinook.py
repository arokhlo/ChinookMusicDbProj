import sqlite3
import os
from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    help = 'Import Chinook database tables for SQLite'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting Chinook database setup for SQLite...'))
        
        db_path = settings.DATABASES['default']['NAME']
        self.stdout.write(f"Database path: {db_path}")
        
        # Connect to SQLite database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create Artist table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS "Artist" (
                "ArtistId" INTEGER PRIMARY KEY AUTOINCREMENT,
                "Name" VARCHAR(120) NOT NULL
            );
        """)
        self.stdout.write(self.style.SUCCESS('✓ Artist table created'))
        
        # Create Album table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS "Album" (
                "AlbumId" INTEGER PRIMARY KEY AUTOINCREMENT,
                "Title" VARCHAR(160) NOT NULL,
                "ArtistId" INTEGER NOT NULL,
                FOREIGN KEY ("ArtistId") REFERENCES "Artist"("ArtistId") ON DELETE CASCADE
            );
        """)
        self.stdout.write(self.style.SUCCESS('✓ Album table created'))
        
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
        self.stdout.write(self.style.SUCCESS('✓ Track table created'))
        
        # Check if tables have data
        cursor.execute("SELECT COUNT(*) FROM \"Artist\"")
        artist_count = cursor.fetchone()[0]
        
        if artist_count == 0:
            self.stdout.write("Inserting sample data...")
            
            # Insert artists
            artists = [
                (1, 'AC/DC'), (2, 'Accept'), (3, 'Aerosmith'),
                (4, 'Alanis Morissette'), (5, 'Alice In Chains'),
                (6, 'Antônio Carlos Jobim'), (7, 'Apocalyptica'),
                (8, 'Audioslave'), (9, 'BackBeat'), (10, 'Billy Cobham')
            ]
            
            for artist_id, name in artists:
                cursor.execute(
                    "INSERT OR IGNORE INTO \"Artist\" (\"ArtistId\", \"Name\") VALUES (?, ?)",
                    [artist_id, name]
                )
            
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
            
            self.stdout.write(self.style.SUCCESS('✓ Sample data inserted'))
        
        conn.commit()
        conn.close()
        
        self.stdout.write(self.style.SUCCESS('✅ Chinook database setup completed!'))