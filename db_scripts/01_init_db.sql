drop database if exists MUSICFM;

create database MUSICFM;

use MUSICFM;

create table ARTIST (
    id int auto_increment,
    `name` varchar(255) not null,
    short_info varchar(800),

    primary key (id)
);

create table ALBUM (
    id int auto_increment,
    artist_id int,
    `name` varchar(350) not null,
    `type` varchar(16),
    release_date date not null,

    primary key (id),
    foreign key (artist_id) references ARTIST (id)
        on delete cascade
        on update cascade -- check validity
);

create table TRACK (
    id int auto_increment,
    `name` varchar(255) not null,
    length_sec float not null check (length_sec > 0),
    album_id int,

    primary key (id),
    foreign key (album_id) references ALBUM (id)
        on delete cascade
        on update cascade -- check validity
);

create table USER (
    id int auto_increment,
    nickname varchar(255) not null,
    email varchar(255) not null check(email like '_%@_%' and length(email) > 5),
    created_at datetime default now(),
    gender char(1) check(gender IN ('F', 'M', '') or gender is null) ,

    primary key (id),
    constraint unique_email unique (email)
);

create table USER_LIKE (
    user_id int,
    track_id int,

    primary key (user_id, track_id), -- a track cannot be liked twice
    foreign key (user_id) references `USER` (id)
        on delete cascade
        on update cascade, -- check validity
    foreign key (track_id) references TRACK (id)
        on delete cascade
        on update cascade -- check validity
);

create table RATE (
    user_id int,
    track_id int,
    rate smallint check (rate > 0 and rate <= 5),

    primary key (user_id, track_id), -- a track cannot be rated twice
    foreign key (user_id) references USER (id)
        on delete cascade
        on update cascade, -- check validity
    foreign key (track_id) references TRACK (id)
        on delete cascade
        on update cascade -- check validity
);


CREATE TABLE PLAYLIST (
    id INT AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    user_id INT,
    PRIMARY KEY (id),
    FOREIGN KEY (user_id) REFERENCES USER (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

create table CONTAIN (
    playlist_id int,
    track_id int,

    foreign key (playlist_id) references PLAYLIST (id)
        on delete cascade
        on update cascade, -- check validity
    foreign key (track_id) references TRACK (id)
        on delete cascade
        on update cascade -- check validity
);
