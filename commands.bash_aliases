# PUSH FROM LOCAL TO CLOUD:
gsutil -m rsync -r images gs://composer-explorer.appspot.com

# PULL FROM CLOUD TO LOCAL:
gsutil -m rsync -r gs://composer-explorer.appspot.com images

# UPLOAD COMPOSER WORKS
cd composerexplorer
source venv/bin/activate
python import_works.py

# CHANGE COMPOSER TO GENERAL SEARCH TYPE
UPDATE composer_list
SET general=1
WHERE name_short="Vaughan Williams";

# ADD VIEW TO COMPOSER
UPDATE composer_list SET view=18301940 WHERE name_short="Grieg";

#mySQL:
mysql --host=34.66.133.61 --user=remote -p composerexplorer

#SSH to compute engine:
ssh -i /home/shane/.ssh/composer-explorer-compute shane@35.226.82.174

#For getting Sha key of .apk
keytool -printcert -jarfile app-debug.apk