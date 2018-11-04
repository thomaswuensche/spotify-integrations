CREATE TABLE `pylonen` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL,
  `artist` varchar(255) DEFAULT NULL,
  `champ` varchar(255) DEFAULT NULL,
  `added_at` varchar(255) DEFAULT NULL,
  `added_time` varchar(255) DEFAULT NULL,
  `explicit` tinyint(1) DEFAULT NULL,
  `release_date` varchar(255) DEFAULT NULL,
  `release_date_precision` varchar(255) DEFAULT NULL,
  `duration` int(11) DEFAULT NULL,
  `popularity` int(3) DEFAULT NULL,
  `danceability` float DEFAULT NULL,
  `energy` float DEFAULT NULL,
  `valence` float DEFAULT NULL,
  `tempo` float DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=101 DEFAULT CHARSET=utf8;

DELETE FROM pylonen;

ALTER TABLE pylonen
AUTO_INCREMENT = 1;
