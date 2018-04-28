测试方法：直接运行`nosetests test`，在测试脚本里会自动运行docker的创建和停止

发布方法：
 * 在venv环境下运行 `python setup.py sdist upload`
 * 在`buildsys/docker_migralite`目录修改dockerfile的migralite版本，然后运行`docker-compose build; docker-compose push`
