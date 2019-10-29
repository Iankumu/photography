-- phpMyAdmin SQL Dump
-- version 4.9.0.1
-- https://www.phpmyadmin.net/
--
-- Host: localhost
-- Generation Time: Oct 29, 2019 at 07:18 AM
-- Server version: 10.3.16-MariaDB
-- PHP Version: 7.3.7

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `photography`
--

-- --------------------------------------------------------

--
-- Table structure for table `photos`
--

CREATE TABLE `photos` (
  `photoid` int(11) NOT NULL,
  `photo` varchar(255) NOT NULL,
  `photographerid` int(11) DEFAULT NULL,
  `date_posted` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `photos`
--

INSERT INTO `photos` (`photoid`, `photo`, `photographerid`, `date_posted`) VALUES
(1, 'index.jpeg', 18, '2019-10-15 20:06:28'),
(2, 'muzammil-soorma-ayV1mD3HGyg-unsplash.jpg', 18, '2019-10-15 20:07:27'),
(3, 'muzammil-soorma-ayV1mD3HGyg-unsplash.jpg', 16, '2019-10-16 09:17:19'),
(4, 'luis-rocha-cRqHwyVb9ts-unsplash.jpg', 16, '2019-10-16 09:18:07'),
(5, 'im.jpg', 18, '2019-10-16 16:42:07'),
(6, 'index.jpeg', 16, '2019-10-17 16:08:59'),
(7, 'ampersand-creative-co-pp_oXEb2H48-unsplash.jpg', 16, '2019-10-17 18:51:01'),
(8, 'snap.png', 16, '2019-10-17 19:29:13'),
(10, 'james-adams-HW2jyY7lmig-unsplash.jpg', 18, '2019-10-21 16:14:50'),
(11, 'hybrid-8F1YBgAGqgA-unsplash.jpg', 16, '2019-10-21 16:21:31'),
(12, 'photo.jpg', 16, '2019-10-24 15:30:11'),
(13, 'jude-beck-AMBT5zkVMV4-unsplash.jpg', 16, '2019-10-24 16:35:44'),
(14, 'wedding.jpg', 19, '2019-10-25 08:56:52');

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `UserID` int(10) NOT NULL,
  `FullName` varchar(100) NOT NULL,
  `UserName` varchar(30) NOT NULL,
  `Email` varchar(100) NOT NULL,
  `Date_Created` timestamp NOT NULL DEFAULT current_timestamp(),
  `Password` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`UserID`, `FullName`, `UserName`, `Email`, `Date_Created`, `Password`) VALUES
(16, 'Ian Kumu', '112449', 'ian.kumu@strathmore.edu', '2019-09-15 15:22:01', 'sha256$feVDGB6e$08d7a720bad32cd63d67b6e70b91dd604d3b044fc72c1f51a90e20c4bd4c6fd2'),
(18, 'Ian Kariuki', 'Ian01', 'ikariuki741@gmail.com', '2019-10-10 14:29:16', 'sha256$9TXpJAoB$9fd3fab88186574e8fac253d060cbfa6f44acfd125cf4695c2531995be793589'),
(19, 'Kevin', 'Kevin01', 'kevin@gmail.com', '2019-10-25 08:55:44', 'sha256$hVF2hOpT$c49c6095f81ddbe7371f1062cdcb959b77b6a4b511aa05633ecd92eab0d943b9');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `photos`
--
ALTER TABLE `photos`
  ADD PRIMARY KEY (`photoid`),
  ADD KEY `photographerid` (`photographerid`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`UserID`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `photos`
--
ALTER TABLE `photos`
  MODIFY `photoid` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=16;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `UserID` int(10) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=20;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `photos`
--
ALTER TABLE `photos`
  ADD CONSTRAINT `photos_ibfk_1` FOREIGN KEY (`photographerid`) REFERENCES `users` (`UserID`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
