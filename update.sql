UPDATE BookSource bs
JOIN Book b
  ON bs.ExternalTitle COLLATE utf8mb4_general_ci = b.TitleCZ COLLATE utf8mb4_general_ci
 AND bs.ExternalAuthors COLLATE utf8mb4_general_ci = b.Author COLLATE utf8mb4_general_ci
SET bs.BookID = b.BookID
WHERE bs.BookID IS NULL;
