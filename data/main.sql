create table admin (
    id serial not null constraint admins_pkey primary key,
    name varchar(30) not null constraint name_key unique,
    password varchar(100) not null
);

create table seat_type (
    id serial not null constraint carriages_pkey primary key,
    name varchar(20) not null constraint stations_seat_name_key unique,
    basic_price double precision not null
);

create table capacity (
    train_number varchar(20) not null,
    carriage_index integer not null,
    seat_type integer not null constraint seat_type_carriages_fkey references seat_type,
    seat_num integer not null,
    constraint capacity_pkey1 primary key (train_number, carriage_index)
);

create table city (
    id serial not null constraint city_pkey primary key,
    name varchar(30) not null constraint cities_city_name_key unique,
    province varchar(30) not null
);

create table station (
    id serial not null constraint stations_pkey primary key,
    name varchar(30) not null constraint stations_station_name_key unique,
    city_id integer constraint stations_city_id_fkey references city
);

create table journey (
    id serial not null constraint journeys_pkey primary key,
    train_number varchar(20) not null,
    station_index integer not null,
    station_id integer not null constraint journeys_station_id_fkey references station,
    arrive_time time,
    depart_time time,
    arrive_day integer,
    depart_day integer,
    distance integer not null,
    constraint journeys_train_number_station_index_key unique (train_number, station_index)
);
create index station_id_index on journey (station_id, station_index, id);

create table "user" (
    id serial not null constraint user_pk primary key,
    name varchar(30) not null,
    phone_number char(11) not null,
    id_card_number char(18) not null,
    password varchar(100) not null
);
create unique index user_id_card_number_uindex on "user" (id_card_number);

create table "order" (
    id serial not null constraint orders_pkey primary key,
    status integer not null,
    price double precision not null,
    user_id integer not null constraint orders_person_fkey references "user",
    create_date timestamp default (CURRENT_TIMESTAMP + '08:00:00'::interval) not null,
    depart_journey integer not null constraint order_journey_id_fk references journey,
    arrive_journey integer not null constraint order_journey_id_fk_2 references journey,
    carriage_index integer not null,
    seat_num integer not null,
    depart_date date not null,
    train_number varchar(20) not null
);

create table ticket (
    id serial not null constraint tickets_pkey primary key,
    order_id integer not null constraint tickets_orders_fkey references "order",
    carriage_index integer not null,
    depart_journey integer not null constraint tickets_journeys_fkey1 references journey,
    arrive_journey integer not null constraint tickets_journeys_fkey2 references journey,
    depart_date date not null,
    seat_num integer not null,
    train_number varchar(20) not null
);

create table if not exists district (
    id serial not null constraint district_pkey primary key,
    code varchar not null,
    name varchar not null
);

create view database_storage as
SELECT (
    tables.table_schema::text || '.'::text) || tables.table_name::text,
    pg_size_pretty(pg_table_size(tables.table_name::character varying::regclass)) AS table_size,
    pg_size_pretty(pg_indexes_size(tables.table_name::character varying::regclass)) AS index_size,
    pg_size_pretty(pg_total_relation_size(tables.table_name::character varying::regclass)) AS total_relation_size,
    round(
        pg_total_relation_size(tables.table_name::character varying::regclass)::numeric /
            sum(pg_total_relation_size(tables.table_name::character varying::regclass)) OVER () * 100::numeric,
        1
    ) AS round
FROM information_schema.tables
WHERE tables.table_schema::name = CURRENT_SCHEMA
    AND tables.table_type::text = 'BASE TABLE'::text
ORDER BY (pg_total_relation_size(tables.table_name::character varying::regclass)) DESC;

create or replace function is_id_valid(code varchar)
returns bool as $body$
declare
    address_code char(6);
    birthday_code char(8);
    checksum_code char(1);
    weights integer[];
    map char(1)[];
    total integer;
begin
    -- 判断 code 长度是否合法等并赋值
    if (code !~ '^\d{17}[\dX]$') then
        return false;
    end if;
    address_code := substr(code, 1, 6);
    birthday_code := substr(code, 7, 8);
    checksum_code := substr(code, 18, 1);
    -- 判断 address_code 是否合法
    select count(*) from district as d where d.code = address_code limit 1 into total;
    if (total != 1) then
        return false;
    end if;
    -- 判断 birthday_code 是否合法
    begin
        if (birthday_code::date<'1900-01-01'::date or birthday_code::date>current_date) then
            return false;
        end if;
    exception
        when others then return false;
    end;
    -- 判断 checksum_code 是否合法
    weights := array[7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2];
    total := 0;
    for ith in 1 .. 17 loop
        total := total + weights[ith]*cast(substr(code, ith, 1) as integer);
    end loop;
    map := array['1', '0', 'X', '9', '8', '7', '6', '5', '4', '3', '2'];
    if (upper(checksum_code) != map[total%11+1]) then
        return false;
    end if;
    -- 返回值
    return true;
end;
$body$ language plpgsql;

create function order_function()
returns trigger language plpgsql
as $$
declare
    status order.status%type;
begin
    status := new.status;
    if status not in (1,2,3) then
        new.status := 3;
    end if;
    return new;
end;
$$;

create trigger order_trigger
before insert on "order"
for each row
    execute procedure order_function();
