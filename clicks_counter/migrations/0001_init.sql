CREATE DATABASE statistics;
CREATE TABLE statistics.clicks (
    page_id INT,
    label VARCHAR(255),
    counter INT NOT NULL DEFAULT 0,
    PRIMARY KEY (page_id, label)
);

CREATE DATABASE test;
CREATE TABLE test.clicks (
    page_id INT,
    label VARCHAR(255),
    counter INT NOT NULL DEFAULT 0,
    PRIMARY KEY (page_id, label)
);
