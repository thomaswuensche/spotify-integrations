-- total tracks added by user
SELECT champ,
	COUNT(id)
FROM pylonen
GROUP BY champ;

-- explicit tracks added by user
SELECT champ,
	COUNT(id)
FROM pylonen
WHERE explicit = 1
GROUP BY champ;

-- percentage of explicit tracks against all tracks added by user
SELECT champ,
	COUNT(id) / (
		SELECT COUNT(id)
		FROM pylonen p2
		WHERE p2.champ = p1.champ
		)*100 AS percentage_are_explicit
FROM pylonen p1
WHERE explicit = 1
GROUP BY champ;

-- longest track
SELECT id, name, artist, champ, duration/1000/60
FROM pylonen
WHERE duration = (
	SELECT MAX(duration)
	FROM pylonen
);

-- tracks from hottest day
SELECT id, name, artist, champ, added_at
FROM pylonen
WHERE added_at = (
  SELECT added_at
  FROM pylonen
  GROUP BY added_at
  HAVING COUNT(id) = (
  	SELECT MAX(count)
  	FROM (
  		SELECT COUNT(ID) AS count
  		FROM pylonen
  		GROUP BY added_at
  	) AS t1
  )
);
