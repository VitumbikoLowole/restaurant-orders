-- MySQL dump 10.13  Distrib 8.0.46, for Linux (x86_64)
--
-- Host: localhost    Database: restaurant_db
-- ------------------------------------------------------
-- Server version	8.0.46-0ubuntu0.24.04.3

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(150) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group`
--

LOCK TABLES `auth_group` WRITE;
/*!40000 ALTER TABLE `auth_group` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group_permissions`
--

DROP TABLE IF EXISTS `auth_group_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `group_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group_permissions`
--

LOCK TABLES `auth_group_permissions` WRITE;
/*!40000 ALTER TABLE `auth_group_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_permission` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `content_type_id` int NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=45 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_permission`
--

LOCK TABLES `auth_permission` WRITE;
/*!40000 ALTER TABLE `auth_permission` DISABLE KEYS */;
INSERT INTO `auth_permission` VALUES (1,'Can add log entry',1,'add_logentry'),(2,'Can change log entry',1,'change_logentry'),(3,'Can delete log entry',1,'delete_logentry'),(4,'Can view log entry',1,'view_logentry'),(5,'Can add permission',2,'add_permission'),(6,'Can change permission',2,'change_permission'),(7,'Can delete permission',2,'delete_permission'),(8,'Can view permission',2,'view_permission'),(9,'Can add group',3,'add_group'),(10,'Can change group',3,'change_group'),(11,'Can delete group',3,'delete_group'),(12,'Can view group',3,'view_group'),(13,'Can add user',4,'add_user'),(14,'Can change user',4,'change_user'),(15,'Can delete user',4,'delete_user'),(16,'Can view user',4,'view_user'),(17,'Can add content type',5,'add_contenttype'),(18,'Can change content type',5,'change_contenttype'),(19,'Can delete content type',5,'delete_contenttype'),(20,'Can view content type',5,'view_contenttype'),(21,'Can add session',6,'add_session'),(22,'Can change session',6,'change_session'),(23,'Can delete session',6,'delete_session'),(24,'Can view session',6,'view_session'),(25,'Can add customer',7,'add_customer'),(26,'Can change customer',7,'change_customer'),(27,'Can delete customer',7,'delete_customer'),(28,'Can view customer',7,'view_customer'),(29,'Can add menu category',8,'add_menucategory'),(30,'Can change menu category',8,'change_menucategory'),(31,'Can delete menu category',8,'delete_menucategory'),(32,'Can view menu category',8,'view_menucategory'),(33,'Can add menu item',9,'add_menuitem'),(34,'Can change menu item',9,'change_menuitem'),(35,'Can delete menu item',9,'delete_menuitem'),(36,'Can view menu item',9,'view_menuitem'),(37,'Can add order',10,'add_order'),(38,'Can change order',10,'change_order'),(39,'Can delete order',10,'delete_order'),(40,'Can view order',10,'view_order'),(41,'Can add order item',11,'add_orderitem'),(42,'Can change order item',11,'change_orderitem'),(43,'Can delete order item',11,'delete_orderitem'),(44,'Can view order item',11,'view_orderitem');
/*!40000 ALTER TABLE `auth_permission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user`
--

DROP TABLE IF EXISTS `auth_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_user` (
  `id` int NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(150) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user`
--

LOCK TABLES `auth_user` WRITE;
/*!40000 ALTER TABLE `auth_user` DISABLE KEYS */;
INSERT INTO `auth_user` VALUES (1,'pbkdf2_sha256$600000$egmjy3dRmcA6Pm6pYCRbOf$cv3yrkoNzeGVgKnAL3py60m/qhFWK3xURWPDVTzzZ4I=','2026-06-26 14:47:12.797649',0,'customer1','Customer1','','customer1@example.com',0,1,'2026-06-26 00:24:59.095605'),(2,'pbkdf2_sha256$600000$YVUnQhgjJC8oqESgPdpeIp$ylO7SpmhETt05Yq82WaZsRaBy6Q0HNEWdlQavBkSPHM=',NULL,0,'customer2','Customer2','','customer2@example.com',0,1,'2026-06-26 00:24:59.343232'),(3,'pbkdf2_sha256$600000$q9JYoZDFYFmwAqj77jJCL6$90bgM0niVq+hvzOKFb9h7ccwyQTyV6ijGi6sbukYUOM=',NULL,0,'customer3','Customer3','','customer3@example.com',0,1,'2026-06-26 00:24:59.529070'),(4,'pbkdf2_sha256$600000$a0QlvvhT0AcUsvf6jhD1Ku$dYi1asHlhds+Q/4JiRSlUX8OMn4bX86EUR4mciFAx40=',NULL,0,'customer4','Customer4','','customer4@example.com',0,1,'2026-06-26 00:24:59.708760'),(5,'pbkdf2_sha256$600000$TPSR6KdnTTi2iEqbFHIOZU$mjxC8kkPBTzyIbPdfMS9He2j1U3G0FPHJm+HhaNWo+0=',NULL,0,'customer5','Customer5','','customer5@example.com',0,1,'2026-06-26 00:24:59.892245'),(6,'pbkdf2_sha256$600000$qtsktGvA7grB2vpmaRIUA6$sG3Y4ntgbXnTOOGBXP9J44Nf0zhbJ0boZqlCyjCYC3c=',NULL,1,'admin','','','admin@example.com',1,1,'2026-06-26 00:25:00.315399');
/*!40000 ALTER TABLE `auth_user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user_groups`
--

DROP TABLE IF EXISTS `auth_user_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_user_groups` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `group_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_groups_user_id_group_id_94350c0c_uniq` (`user_id`,`group_id`),
  KEY `auth_user_groups_group_id_97559544_fk_auth_group_id` (`group_id`),
  CONSTRAINT `auth_user_groups_group_id_97559544_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `auth_user_groups_user_id_6a12ed8b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_groups`
--

LOCK TABLES `auth_user_groups` WRITE;
/*!40000 ALTER TABLE `auth_user_groups` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user_user_permissions`
--

DROP TABLE IF EXISTS `auth_user_user_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_user_user_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_user_permissions_user_id_permission_id_14a6b632_uniq` (`user_id`,`permission_id`),
  KEY `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_user_permissions`
--

LOCK TABLES `auth_user_user_permissions` WRITE;
/*!40000 ALTER TABLE `auth_user_user_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user_user_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_admin_log`
--

DROP TABLE IF EXISTS `django_admin_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_admin_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint unsigned NOT NULL,
  `change_message` longtext NOT NULL,
  `content_type_id` int DEFAULT NULL,
  `user_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_auth_user_id` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `django_admin_log_chk_1` CHECK ((`action_flag` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_admin_log`
--

LOCK TABLES `django_admin_log` WRITE;
/*!40000 ALTER TABLE `django_admin_log` DISABLE KEYS */;
/*!40000 ALTER TABLE `django_admin_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_content_type`
--

DROP TABLE IF EXISTS `django_content_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_content_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_content_type`
--

LOCK TABLES `django_content_type` WRITE;
/*!40000 ALTER TABLE `django_content_type` DISABLE KEYS */;
INSERT INTO `django_content_type` VALUES (1,'admin','logentry'),(3,'auth','group'),(2,'auth','permission'),(4,'auth','user'),(5,'contenttypes','contenttype'),(7,'menu','customer'),(8,'menu','menucategory'),(9,'menu','menuitem'),(10,'menu','order'),(11,'menu','orderitem'),(6,'sessions','session');
/*!40000 ALTER TABLE `django_content_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_migrations`
--

DROP TABLE IF EXISTS `django_migrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_migrations` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=20 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_migrations`
--

LOCK TABLES `django_migrations` WRITE;
/*!40000 ALTER TABLE `django_migrations` DISABLE KEYS */;
INSERT INTO `django_migrations` VALUES (1,'contenttypes','0001_initial','2026-06-26 00:23:22.976671'),(2,'auth','0001_initial','2026-06-26 00:23:23.681772'),(3,'admin','0001_initial','2026-06-26 00:23:23.843388'),(4,'admin','0002_logentry_remove_auto_add','2026-06-26 00:23:23.855799'),(5,'admin','0003_logentry_add_action_flag_choices','2026-06-26 00:23:23.869098'),(6,'contenttypes','0002_remove_content_type_name','2026-06-26 00:23:23.982293'),(7,'auth','0002_alter_permission_name_max_length','2026-06-26 00:23:24.045626'),(8,'auth','0003_alter_user_email_max_length','2026-06-26 00:23:24.072722'),(9,'auth','0004_alter_user_username_opts','2026-06-26 00:23:24.082398'),(10,'auth','0005_alter_user_last_login_null','2026-06-26 00:23:24.132572'),(11,'auth','0006_require_contenttypes_0002','2026-06-26 00:23:24.139821'),(12,'auth','0007_alter_validators_add_error_messages','2026-06-26 00:23:24.151091'),(13,'auth','0008_alter_user_username_max_length','2026-06-26 00:23:24.232534'),(14,'auth','0009_alter_user_last_name_max_length','2026-06-26 00:23:24.318582'),(15,'auth','0010_alter_group_name_max_length','2026-06-26 00:23:24.345422'),(16,'auth','0011_update_proxy_permissions','2026-06-26 00:23:24.361243'),(17,'auth','0012_alter_user_first_name_max_length','2026-06-26 00:23:24.436191'),(18,'menu','0001_initial','2026-06-26 00:23:24.934956'),(19,'sessions','0001_initial','2026-06-26 00:23:24.977846');
/*!40000 ALTER TABLE `django_migrations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_session`
--

DROP TABLE IF EXISTS `django_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_session`
--

LOCK TABLES `django_session` WRITE;
/*!40000 ALTER TABLE `django_session` DISABLE KEYS */;
INSERT INTO `django_session` VALUES ('zx9q84gqbtrk8egbqamsxtljr35voncb','.eJxVjDsOwjAQBe_iGlmOHWcJJT1nsPZnHECxFCcV4u4oUgpo38y8t0m4rSVtTZc0ibmYzpx-N0J-6rwDeeB8r5brvC4T2V2xB232VkVf18P9OyjYyl4T-0jC4BhpyJCBe3GaR9UQI4sncBA7RKVzcEOvI2X2vVAYIDJ48_kCJXM5HA:1wd7po:bWBiW8_SDi30_fPzyfQSrezGy1wTBuoXc77w4IN607U','2026-07-10 14:47:12.827695');
/*!40000 ALTER TABLE `django_session` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `menu_customer`
--

DROP TABLE IF EXISTS `menu_customer`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `menu_customer` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `phone` varchar(30) NOT NULL,
  `address` longtext NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `user_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`),
  CONSTRAINT `menu_customer_user_id_b051b178_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `menu_customer`
--

LOCK TABLES `menu_customer` WRITE;
/*!40000 ALTER TABLE `menu_customer` DISABLE KEYS */;
INSERT INTO `menu_customer` VALUES (1,'+250780000001','','2026-06-26 00:24:59.118997',1),(2,'+250780000002','','2026-06-26 00:24:59.343918',2),(3,'+250780000003','','2026-06-26 00:24:59.529757',3),(4,'+250780000004','','2026-06-26 00:24:59.709490',4),(5,'+250780000005','','2026-06-26 00:24:59.892833',5),(6,'','','2026-06-26 00:25:00.493232',6);
/*!40000 ALTER TABLE `menu_customer` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `menu_menucategory`
--

DROP TABLE IF EXISTS `menu_menucategory`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `menu_menucategory` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `description` longtext NOT NULL,
  `created_at` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `menu_menucategory`
--

LOCK TABLES `menu_menucategory` WRITE;
/*!40000 ALTER TABLE `menu_menucategory` DISABLE KEYS */;
INSERT INTO `menu_menucategory` VALUES (1,'Starters','Our selection of starters.','2026-06-26 00:24:58.994400'),(2,'Mains','Our selection of mains.','2026-06-26 00:24:59.023291'),(3,'Drinks','Our selection of drinks.','2026-06-26 00:24:59.055611'),(4,'Desserts','Our selection of desserts.','2026-06-26 00:24:59.077324');
/*!40000 ALTER TABLE `menu_menucategory` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `menu_menuitem`
--

DROP TABLE IF EXISTS `menu_menuitem`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `menu_menuitem` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(150) NOT NULL,
  `description` longtext NOT NULL,
  `price` decimal(8,2) NOT NULL,
  `photo` varchar(100) DEFAULT NULL,
  `is_available` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `category_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `menu_menuitem_category_id_name_db4faa81_uniq` (`category_id`,`name`),
  CONSTRAINT `menu_menuitem_category_id_af353a3b_fk_menu_menucategory_id` FOREIGN KEY (`category_id`) REFERENCES `menu_menucategory` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `menu_menuitem`
--

LOCK TABLES `menu_menuitem` WRITE;
/*!40000 ALTER TABLE `menu_menuitem` DISABLE KEYS */;
INSERT INTO `menu_menuitem` VALUES (1,'Spring Rolls','Delicious Spring Rolls.',3500.00,'menu_items/spring_rolls.jpg',1,'2026-06-26 00:24:59.002450',1),(2,'Garlic Bread','Delicious Garlic Bread.',2800.00,'menu_items/Garlic_Bread.jpg',1,'2026-06-26 00:24:59.011814',1),(3,'Soup of the Day','Delicious Soup of the Day.',4000.00,'menu_items/soup_of_the_day.jpg',1,'2026-06-26 00:24:59.018100',1),(4,'Margherita Pizza','Delicious Margherita Pizza.',9500.00,'menu_items/Pizza_margherita.jpg',1,'2026-06-26 00:24:59.028653',2),(5,'Grilled Chicken','Delicious Grilled Chicken.',11000.00,'menu_items/Grilled_Chicken.webp',1,'2026-06-26 00:24:59.035885',2),(6,'Beef Burger','Delicious Beef Burger.',8750.00,'menu_items/TheUltimateBurgerwBacon_RecipePic-2048x1126.jpg',1,'2026-06-26 00:24:59.043455',2),(7,'Veggie Pasta','Delicious Veggie Pasta.',8000.00,'menu_items/veggie_pasta.jpg',1,'2026-06-26 00:24:59.048388',2),(8,'Fresh Juice','Delicious Fresh Juice.',4500.00,'menu_items/fresh_juice.png',1,'2026-06-26 00:24:59.061495',3),(9,'Skol','Delicious Skol.',2000.00,'menu_items/MALTKEEPIT100.webp',1,'2026-06-26 00:24:59.067233',3),(10,'Mutzig','Delicious Mutzig.',2000.00,'menu_items/Mutzig.jpg',1,'2026-06-26 00:24:59.073136',3),(11,'Chocolate Cake','Delicious Chocolate Cake.',4200.00,'menu_items/Chocolate_cake.jpg',1,'2026-06-26 00:24:59.081735',4),(12,'Ice Cream','Delicious Ice Cream.',3000.00,'menu_items/ice-cream-1.jpg',1,'2026-06-26 00:24:59.087430',4);
/*!40000 ALTER TABLE `menu_menuitem` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `menu_order`
--

DROP TABLE IF EXISTS `menu_order`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `menu_order` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `status` varchar(10) NOT NULL,
  `total_price` decimal(10,2) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `customer_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `menu_order_customer_id_e42b363f_fk_menu_customer_id` (`customer_id`),
  CONSTRAINT `menu_order_customer_id_e42b363f_fk_menu_customer_id` FOREIGN KEY (`customer_id`) REFERENCES `menu_customer` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `menu_order`
--

LOCK TABLES `menu_order` WRITE;
/*!40000 ALTER TABLE `menu_order` DISABLE KEYS */;
INSERT INTO `menu_order` VALUES (1,'paid',38500.00,'2026-06-22 00:25:00.077170',1),(2,'paid',37500.00,'2026-06-23 00:25:00.106967',4),(3,'paid',15000.00,'2026-06-25 00:25:00.122639',3),(4,'paid',24500.00,'2026-06-24 00:25:00.140064',5),(5,'pending',13500.00,'2026-06-23 00:25:00.155655',3),(6,'pending',6200.00,'2026-06-25 00:25:00.167236',5),(7,'paid',36000.00,'2026-06-25 00:25:00.184329',3),(8,'paid',26000.00,'2026-06-22 00:25:00.197534',2),(9,'paid',41750.00,'2026-06-26 00:25:00.215260',3),(10,'paid',9000.00,'2026-06-24 00:25:00.232264',2),(11,'pending',9500.00,'2026-06-23 00:25:00.243273',4),(12,'paid',39500.00,'2026-06-23 00:25:00.255157',3),(13,'pending',5600.00,'2026-06-24 00:25:00.272514',2),(14,'pending',9600.00,'2026-06-22 00:25:00.284699',5),(15,'paid',23000.00,'2026-06-25 00:25:00.299468',5),(16,'paid',8000.00,'2026-06-26 14:47:36.624414',1);
/*!40000 ALTER TABLE `menu_order` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `menu_orderitem`
--

DROP TABLE IF EXISTS `menu_orderitem`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `menu_orderitem` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `quantity` int unsigned NOT NULL,
  `unit_price` decimal(8,2) NOT NULL,
  `menu_item_id` bigint NOT NULL,
  `order_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `menu_orderitem_order_id_menu_item_id_6c3a4609_uniq` (`order_id`,`menu_item_id`),
  KEY `menu_orderitem_menu_item_id_99cc5c4f_fk_menu_menuitem_id` (`menu_item_id`),
  CONSTRAINT `menu_orderitem_menu_item_id_99cc5c4f_fk_menu_menuitem_id` FOREIGN KEY (`menu_item_id`) REFERENCES `menu_menuitem` (`id`),
  CONSTRAINT `menu_orderitem_order_id_78f7348e_fk_menu_order_id` FOREIGN KEY (`order_id`) REFERENCES `menu_order` (`id`),
  CONSTRAINT `menu_orderitem_chk_1` CHECK ((`quantity` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=34 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `menu_orderitem`
--

LOCK TABLES `menu_orderitem` WRITE;
/*!40000 ALTER TABLE `menu_orderitem` DISABLE KEYS */;
INSERT INTO `menu_orderitem` VALUES (1,3,3500.00,1,1),(2,2,9500.00,4,1),(3,3,3000.00,12,1),(4,3,9500.00,4,2),(5,3,3000.00,12,2),(6,1,3000.00,12,3),(7,1,4000.00,3,3),(8,1,8000.00,7,3),(9,1,9500.00,4,4),(10,3,2000.00,10,4),(11,2,4500.00,8,4),(12,3,4500.00,8,5),(13,1,2000.00,10,6),(14,1,4200.00,11,6),(15,1,3000.00,12,7),(16,3,11000.00,5,7),(17,3,2000.00,10,8),(18,2,8000.00,7,8),(19,2,2000.00,9,8),(20,3,11000.00,5,9),(21,1,8750.00,6,9),(22,2,4500.00,8,10),(23,1,9500.00,4,11),(24,1,3500.00,1,12),(25,3,4000.00,3,12),(26,3,8000.00,7,12),(27,2,2800.00,2,13),(28,2,2000.00,9,14),(29,2,2800.00,2,14),(30,2,2000.00,9,15),(31,2,9500.00,4,15),(32,1,3500.00,1,16),(33,1,4500.00,8,16);
/*!40000 ALTER TABLE `menu_orderitem` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-06-26 18:35:56
