UPDATE BookSource bs
JOIN (
    SELECT bs2.BookSourceID, b.BookID
    FROM BookSource bs2
    JOIN Book b
      ON bs2.ExternalTitle COLLATE utf8mb4_general_ci = b.TitleCZ COLLATE utf8mb4_general_ci
     AND bs2.ExternalAuthors COLLATE utf8mb4_general_ci = b.Author COLLATE utf8mb4_general_ci
    LIMIT 1000
) t
ON bs.BookSourceID = t.BookSourceID
SET bs.BookID = t.BookID;

-- mysql -u django_user -p divDB < update.sql
