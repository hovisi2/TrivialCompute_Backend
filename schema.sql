CREATE DATABASE IF NOT EXISTS trivial_compute CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE trivial_compute;

DROP TABLE IF EXISTS questions;

CREATE TABLE questions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    category VARCHAR(50) NOT NULL,
    question TEXT NOT NULL,
    answer VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_category (category),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB;

INSERT INTO questions (category, question, answer) VALUES
('Science', 'What is the chemical symbol for gold?', 'Au'),
('Science', 'What planet is known as the Red Planet?', 'Mars'),
('Science', 'What gas do plants absorb from the atmosphere?', 'Carbon dioxide'),
('Science', 'What is the hardest natural substance on Earth?', 'Diamond'),

('Math', 'What is 12 × 8?', '96'),
('Math', 'What is the square root of 144?', '12'),
('Math', 'What is 15% of 200?', '30'),
('Math', 'What is the value of π (pi) to 2 decimal places?', '3.14'),

('English', 'Who wrote "Romeo and Juliet"?', 'William Shakespeare'),
('English', 'What is the past tense of "run"?', 'ran'),
('English', 'What is a group of lions called?', 'A pride'),
('English', 'Which word means "fear of spiders"?', 'Arachnophobia'),

('History', 'In what year did World War II end?', '1945'),
('History', 'Who was the first President of the United States?', 'George Washington'),
('History', 'What year did the Titanic sink?', '1912'),
('History', 'Which ancient wonder was located in Alexandria?', 'Lighthouse of Alexandria');

-- Display sample data
SELECT 'Database setup complete!' as status;
SELECT category, COUNT(*) as question_count FROM questions GROUP BY category ORDER BY category;