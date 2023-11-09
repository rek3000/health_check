CREATE DATABASE IF NOT EXISTS logs_mps;
USE logs_mps;

CREATE TABLE Details (
	initTime DATETIME,
    idMachine VARCHAR(8),
    fault VARCHAR(255) NOT NULL,
    inlet VARCHAR(20),
    exhaust VARCHAR(20),
    firmware VARCHAR(20),
    image VARCHAR(8),
    vol_avail int,
    raid_stat bool,
    bonding VARCHAR(20),
    cpu_util int,
    load_avg float,
    load_vcpu int,
    load_avg_per float,
    mem_util int,
    swap_util int,
    primary key (initTime, idMachine)
);
