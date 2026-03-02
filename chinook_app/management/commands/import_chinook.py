import os
import csv
from django.core.management.base import BaseCommand
from django.db import connection
from django.conf import settings
import dj_database_url

class Command(BaseCommand):
    help = 'Import Chinook database from CSV files or create tables'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting Chinook database setup...'))
        
        # Check if we're on Heroku with PostgreSQL
        database_url = os.environ.get('DATABASE_URL')
        
        if database_url and 'postgres' in database_url:
            self.stdout.write(self.style.SUCCESS('PostgreSQL detected, creating tables...'))
            self.create_postgres_tables()
        else:
            self.stdout.write(self.style.WARNING('SQLite detected, skipping table creation...'))
        
        self.stdout.write(self.style.SUCCESS('Chinook database setup completed!'))

    def create_postgres_tables(self):
        """Create Chinook tables in PostgreSQL"""
        with connection.cursor() as cursor:
            # Check if tables exist
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'Artist'
                );
            """)
            artist_table_exists = cursor.fetchone()[0]
            
            if not artist_table_exists:
                self.stdout.write(self.style.SUCCESS('Creating Artist table...'))
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS "Artist" (
                        "ArtistId" SERIAL PRIMARY KEY,
                        "Name" VARCHAR(120) NOT NULL
                    );
                """)
                
                self.stdout.write(self.style.SUCCESS('Creating Album table...'))
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS "Album" (
                        "AlbumId" SERIAL PRIMARY KEY,
                        "Title" VARCHAR(160) NOT NULL,
                        "ArtistId" INTEGER NOT NULL REFERENCES "Artist"("ArtistId") ON DELETE CASCADE
                    );
                """)
                
                self.stdout.write(self.style.SUCCESS('Creating Track table...'))
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS "Track" (
                        "TrackId" SERIAL PRIMARY KEY,
                        "Name" VARCHAR(200) NOT NULL,
                        "AlbumId" INTEGER REFERENCES "Album"("AlbumId") ON DELETE CASCADE,
                        "MediaTypeId" INTEGER NOT NULL,
                        "GenreId" INTEGER,
                        "Composer" VARCHAR(220),
                        "Milliseconds" INTEGER NOT NULL,
                        "Bytes" INTEGER,
                        "UnitPrice" DECIMAL(10,2) NOT NULL
                    );
                """)
                
                # Insert sample data if needed
                self.insert_sample_data(cursor)
            else:
                self.stdout.write(self.style.SUCCESS('Chinook tables already exist.'))

    def insert_sample_data(self, cursor):
        """Insert sample Chinook data"""
        self.stdout.write(self.style.SUCCESS('Inserting sample artists...'))
        artists = [
            (1, 'AC/DC'),
            (2, 'Accept'),
            (3, 'Aerosmith'),
            (4, 'Alanis Morissette'),
        ]
        for artist_id, name in artists:
            cursor.execute(
                'INSERT INTO "Artist" ("ArtistId", "Name") VALUES (%s, %s) ON CONFLICT DO NOTHING',
                [artist_id, name]
            )
        
        self.stdout.write(self.style.SUCCESS('Inserting sample albums...'))
        albums = [
            (1, 'For Those About To Rock We Salute You', 1),
            (2, 'Balls to the Wall', 2),
            (3, 'Restless and Wild', 2),
        ]
        for album_id, title, artist_id in albums:
            cursor.execute(
                'INSERT INTO "Album" ("AlbumId", "Title", "ArtistId") VALUES (%s, %s, %s) ON CONFLICT DO NOTHING',
                [album_id, title, artist_id]
            )
        
        self.stdout.write(self.style.SUCCESS('Inserting sample tracks...'))
        tracks = [
            (1, 'For Those About To Rock (We Salute You)', 1, 1, 1, 'Angus Young, Malcolm Young, Brian Johnson', 343719, 11170334, 0.99),
            (2, 'Balls to the Wall', 2, 2, 1, None, 342562, 5510424, 0.99),
            (3, 'Fast As a Shark', 3, 3, 1, 'F. Baltes, S. Kaufman, U. Dirkscneider & W. Hoffmann', 230619, 3990994, 0.99),
        ]
        for track_id, name, album_id, media_type_id, genre_id, composer, milliseconds, bytes, unit_price in tracks:
            cursor.execute(
                'INSERT INTO "Track" ("TrackId", "Name", "AlbumId", "MediaTypeId", "GenreId", "Composer", "Milliseconds", "Bytes", "UnitPrice") VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING',
                [track_id, name, album_id, media_type_id, genre_id, composer, milliseconds, bytes, unit_price]
            )
        
        self.stdout.write(self.style.SUCCESS('Sample data inserted successfully!'))