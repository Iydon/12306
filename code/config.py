__all__ = ('database_url', 'residence_time')


# database configuration
username = 'checker'
password = '123456'
hostport = '127.0.0.1:5432'
database = 'project_2'
database_url = f'postgresql://{username}:{password}@{hostport}/{database}'

# cache configuration
is_cached = True

# order and ticket configuration
residence_time = 30 * 60  # seconds
