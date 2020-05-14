__all__ = ('database_url', )


# database configuration
username = 'checker'
password = '123456'
hostport = '127.0.0.1:5432'
database = 'project_2'
database_url = f'postgresql://{username}:{password}@{hostport}/{database}'
