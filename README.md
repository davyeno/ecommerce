# personal_web

Pull new update after develop on local
 git pull origin

To check docker logs
 docker-compose -f docker-compose-deploy.yml logs

To apply new change on local developemnt to build
 docker-compose -f docker-compose-deploy.yml build app 

Command to rebuild without affecting volume
    # Replace container with new version without bring out the volume or swipe the dependency
 docker-compose -f docker-compose-deploy.yml up --no-deps -d app

Command to create superuser
 docker-compose -f docker-compose-deploy.yml run --rm app sh -c "python manage.py createsuperuser"

docker-compose run --rm app sh -c "python manage.py createsuperuser"

 docker-compose down --rmi all -v
