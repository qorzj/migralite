#!/usr/bin/env bash
docker-compose -f docker/testci/docker-compose.yml up -d --force-recreate

python -c "import time, os
t = time.time()
while time.time() - t < 300:
  ret = os.system('docker-compose -f docker/testci/docker-compose.yml logs mglite_mysql | grep port..3306.')
  if ret == 0:
    print('[OK] Database is ready.')
    exit(0)
  time.sleep(1)
else:
  print('[ERROR] Database is NOT ready!')
  exit(1)
"