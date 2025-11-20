
-- Database Creation
CREATE DATABASE IF NOT EXISTS petadoptionsystem;
USE petadoptionsystem;

-- Tables
CREATE TABLE Pets (
    Pet_ID INT PRIMARY KEY AUTO_INCREMENT,
    Pet_Name VARCHAR(50),
    Breed VARCHAR(50),
    Age INT,
    Gender VARCHAR(10),
    Status VARCHAR(20) DEFAULT 'Available'
);

CREATE TABLE Adopters (
    Adopter_ID INT PRIMARY KEY AUTO_INCREMENT,
    Adopter_Name VARCHAR(50),
    Phone VARCHAR(15),
    City VARCHAR(50)
);

CREATE TABLE Adoption (
    Adoption_ID INT PRIMARY KEY AUTO_INCREMENT,
    Pet_ID INT,
    Adopter_ID INT,
    Adoption_Date DATE,
    FOREIGN KEY (Pet_ID) REFERENCES Pets(Pet_ID),
    FOREIGN KEY (Adopter_ID) REFERENCES Adopters(Adopter_ID)
);

-- Trigger
CREATE TRIGGER update_pet_status
AFTER INSERT ON Adoption
FOR EACH ROW
UPDATE Pets SET Status='Adopted' WHERE Pet_ID = NEW.Pet_ID;

-- Stored Procedure
CREATE PROCEDURE RegisterAdoption(IN p_pet_id INT, IN p_adopter_id INT)
BEGIN
    INSERT INTO Adoption (Pet_ID, Adopter_ID, Adoption_Date)
    VALUES (p_pet_id, p_adopter_id, CURDATE());
END;

-- Function
CREATE FUNCTION GetAvailablePets()
RETURNS INT
DETERMINISTIC
BEGIN
    DECLARE available_count INT;
    SELECT COUNT(*) INTO available_count FROM Pets WHERE Status='Available';
    RETURN available_count;
END;

-- View
CREATE VIEW AdoptedPets AS
SELECT p.Pet_Name, p.Breed, a.Adopter_Name, a.City, ad.Adoption_Date
FROM Pets p
JOIN Adoption ad ON p.Pet_ID = ad.Pet_ID
JOIN Adopters a ON ad.Adopter_ID = a.Adopter_ID;
