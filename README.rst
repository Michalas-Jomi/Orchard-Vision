==============
Orchard Vision
==============

Orchard Vision is a Django project to easier orientation in simple orchard. You'll need to catalog every tree in mobile app.

Quick start
-----------

1. Insert SECRET_KEY and GOOGLE_MAPS_API_KEY (You'll need a project on https://console.cloud.google.com/google/maps-apis/) in settings.py

2. Configure the database in settings.py

3. run ``python manage.py migrate`` to create models

4. Start the development server, configure mobile app and catalog trees

5. Visit http://127.0.0.1:8000/map to see cataloged trees on map