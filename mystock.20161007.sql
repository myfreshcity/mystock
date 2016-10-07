/*
 Navicat MySQL Data Transfer

 Source Server         : localhost
 Source Server Version : 50715
 Source Host           : localhost
 Source Database       : mystock

 Target Server Version : 50715
 File Encoding         : utf-8

 Date: 10/07/2016 18:43:55 PM
*/

SET NAMES utf8;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
--  Table structure for `comments`
-- ----------------------------
DROP TABLE IF EXISTS `comments`;
CREATE TABLE `comments` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `content` varchar(2000) DEFAULT NULL COMMENT '日志内容',
  `stock` varchar(255) DEFAULT NULL COMMENT '股票代码',
  `created_time` datetime DEFAULT NULL,
  `updated_time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=146 DEFAULT CHARSET=utf8;

-- ----------------------------
--  Table structure for `data_item`
-- ----------------------------
DROP TABLE IF EXISTS `data_item`;
CREATE TABLE `data_item` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL COMMENT '数据项目',
  `update_time` datetime DEFAULT NULL,
  `create_time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;

-- ----------------------------
--  Table structure for `my_stocks`
-- ----------------------------
DROP TABLE IF EXISTS `my_stocks`;
CREATE TABLE `my_stocks` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `code` varchar(255) DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  `market` char(2) DEFAULT NULL COMMENT '所在市场',
  `flag` int(4) DEFAULT '1' COMMENT '0-自选，1-备选',
  `in_price` decimal(10,2) DEFAULT '0.00' COMMENT '最近买入价',
  `in_date` date DEFAULT NULL COMMENT '最近买入时间',
  `created_time` datetime DEFAULT NULL,
  `updated_time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `pk_my_stocks_code` (`code`) USING HASH
) ENGINE=MyISAM AUTO_INCREMENT=149 DEFAULT CHARSET=utf8;

-- ----------------------------
--  Table structure for `relation_stocks`
-- ----------------------------
DROP TABLE IF EXISTS `relation_stocks`;
CREATE TABLE `relation_stocks` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `main_stock` varchar(20) NOT NULL DEFAULT '' COMMENT '主股票代码',
  `relation_stock` varchar(20) NOT NULL DEFAULT '' COMMENT '关联股票代码',
  `created_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=3 DEFAULT CHARSET=utf8 COMMENT='相关股票';

-- ----------------------------
--  Table structure for `stock_basic`
-- ----------------------------
DROP TABLE IF EXISTS `stock_basic`;
CREATE TABLE `stock_basic` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `code` varchar(10) DEFAULT NULL COMMENT '股票代码',
  `name` varchar(255) DEFAULT NULL COMMENT '股票简称',
  `zgb` decimal(20,0) DEFAULT NULL COMMENT '总股本',
  `ltgb` decimal(20,0) DEFAULT NULL COMMENT '流通股本',
  `launch_date` date DEFAULT NULL COMMENT '上市日期',
  `latest_report` date DEFAULT '1900-01-01' COMMENT '最近披露的报告',
  `grow_type` varchar(3) NOT NULL DEFAULT '' COMMENT '成长类型',
  `desc` varchar(500) DEFAULT NULL COMMENT '业务描述',
  `created_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `pk_stock_basic_code` (`code`) USING HASH
) ENGINE=MyISAM AUTO_INCREMENT=2878 DEFAULT CHARSET=utf8 COMMENT='股票基本信息（上交所／深交所）';

-- ----------------------------
--  Table structure for `stock_finance_basic`
-- ----------------------------
DROP TABLE IF EXISTS `stock_finance_basic`;
CREATE TABLE `stock_finance_basic` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `code` varchar(255) DEFAULT NULL COMMENT '股票代码',
  `report_type` varchar(255) DEFAULT NULL COMMENT '会计年度',
  `mgsy` decimal(10,2) DEFAULT NULL COMMENT '基本每股收益(元)',
  `mgsy_ttm` decimal(10,2) DEFAULT NULL,
  `mgjzc` decimal(10,2) DEFAULT NULL COMMENT '每股净资产(元)',
  `mgjyxjl` decimal(10,2) DEFAULT NULL COMMENT '每股经营活动产生的现金流量净额(元)',
  `mgjyxjl_ttm` decimal(10,2) DEFAULT NULL COMMENT '每股经营现金流TTM',
  `roe` decimal(10,2) DEFAULT NULL COMMENT '净资产收益率（摊薄)(%)',
  `yysr` decimal(20,2) DEFAULT NULL COMMENT '营业收入',
  `kjlr` decimal(20,2) DEFAULT NULL COMMENT '扣除非经常性损益后的净利润（元)',
  `jlr` decimal(20,2) DEFAULT NULL COMMENT '净利润（元)',
  `lrze` decimal(20,2) DEFAULT NULL COMMENT '利润总额(元)',
  `zzc` decimal(20,2) DEFAULT NULL COMMENT '总资产(元)',
  `gdqy` decimal(20,2) DEFAULT NULL COMMENT '股东权益（元)',
  `jyjxjl` decimal(20,2) DEFAULT NULL COMMENT '经营活动产生的现金流量净额(元)',
  `created_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=3555 DEFAULT CHARSET=utf8 COMMENT='基本财务指标（和讯）';

-- ----------------------------
--  Table structure for `stock_finance_data`
-- ----------------------------
DROP TABLE IF EXISTS `stock_finance_data`;
CREATE TABLE `stock_finance_data` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `code` varchar(255) DEFAULT NULL COMMENT '股票代码',
  `report_type` date DEFAULT NULL COMMENT '会计类型',
  `zyysr` decimal(20,0) DEFAULT NULL COMMENT '主营业务收入',
  `zyysr_ttm` decimal(20,0) DEFAULT NULL COMMENT '连续四季度营业收入',
  `zyylr` decimal(20,0) DEFAULT NULL COMMENT '主营业务利润',
  `yylr` decimal(20,0) DEFAULT NULL COMMENT '营业利润',
  `kjlr` decimal(20,0) DEFAULT NULL COMMENT '净利润(扣除非经常性损益后)',
  `jlr` decimal(20,0) DEFAULT NULL COMMENT '净利润',
  `jlr_ttm` decimal(20,0) DEFAULT NULL COMMENT '连续四季度净利润',
  `jyjxjl` decimal(20,0) DEFAULT NULL COMMENT '经营活动产生的现金流量净额',
  `jyjxjl_ttm` decimal(20,0) DEFAULT NULL COMMENT '连续四季度经营现金流净额',
  `xjjze` decimal(20,0) DEFAULT '1' COMMENT '现金及现金等价物净增加额',
  `zzc` decimal(20,0) DEFAULT '1' COMMENT '总资产',
  `ldzc` decimal(20,0) DEFAULT '1' COMMENT '流动资产',
  `zfz` decimal(20,0) DEFAULT '1' COMMENT '总负债',
  `ldfz` decimal(20,0) DEFAULT '1' COMMENT '流动负债',
  `gdqy` decimal(20,0) DEFAULT '1' COMMENT '股东权益不含少数股东权益',
  `roe` decimal(10,2) DEFAULT '1.00' COMMENT '净资产收益率（摊薄)(%)',
  `jlr_rate` decimal(10,2) DEFAULT '1.00' COMMENT '净利润增长率',
  `xjye` decimal(20,0) DEFAULT '1' COMMENT '期末现金及现金等价物余额',
  `yszk` decimal(20,0) DEFAULT '1' COMMENT '应收账款',
  `ch` decimal(20,0) DEFAULT '1' COMMENT '存货',
  `created_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=727 DEFAULT CHARSET=utf8 COMMENT='财务数据（网易）';

-- ----------------------------
--  Table structure for `stock_holder`
-- ----------------------------
DROP TABLE IF EXISTS `stock_holder`;
CREATE TABLE `stock_holder` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `code` varchar(10) DEFAULT NULL COMMENT '股票代码',
  `holder_name` varchar(255) DEFAULT NULL COMMENT '股东名称',
  `amount` decimal(20,0) DEFAULT NULL COMMENT '数量',
  `rate` decimal(10,2) DEFAULT NULL COMMENT '比例',
  `holder_type` varchar(100) DEFAULT NULL COMMENT '股东性质',
  `holder_parent` varchar(255) DEFAULT NULL COMMENT '股东母机构',
  `report_date` date DEFAULT NULL COMMENT '报告日期',
  `created_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=946137 DEFAULT CHARSET=utf8 COMMENT='流通股东表（新浪）';

-- ----------------------------
--  Table structure for `stock_holder_sum`
-- ----------------------------
DROP TABLE IF EXISTS `stock_holder_sum`;
CREATE TABLE `stock_holder_sum` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `code` varchar(10) DEFAULT NULL COMMENT '股票代码',
  `name` varchar(255) DEFAULT NULL COMMENT '股票名称',
  `count` int(20) DEFAULT NULL COMMENT '个数统计',
  `sum` decimal(10,2) DEFAULT NULL COMMENT '比例统计',
  `report_date` date DEFAULT NULL COMMENT '报告日期',
  `created_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=2867 DEFAULT CHARSET=utf8 COMMENT='机构流通股东汇总表（新浪，统计最近一期的持股情况）';

-- ----------------------------
--  Table structure for `stock_trade_basic`
-- ----------------------------
DROP TABLE IF EXISTS `stock_trade_basic`;
CREATE TABLE `stock_trade_basic` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `code` varchar(255) DEFAULT NULL COMMENT '股票代码',
  `trade_date` date DEFAULT NULL COMMENT '交易日期',
  `close` decimal(10,2) DEFAULT NULL COMMENT '收盘价',
  `adj_close` decimal(10,2) DEFAULT NULL COMMENT '复权价',
  `volume` decimal(20,0) DEFAULT NULL COMMENT '交易量',
  `created_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=5215 DEFAULT CHARSET=utf8 COMMENT='基本行情指标（yahoo）';

-- ----------------------------
--  Table structure for `stock_trade_data`
-- ----------------------------
DROP TABLE IF EXISTS `stock_trade_data`;
CREATE TABLE `stock_trade_data` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `code` varchar(255) DEFAULT NULL COMMENT '股票代码',
  `trade_date` date DEFAULT NULL COMMENT '交易日期',
  `close` decimal(10,2) DEFAULT NULL COMMENT '收盘价',
  `volume` decimal(20,0) DEFAULT NULL COMMENT '交易金额',
  `t_cap` decimal(20,0) DEFAULT NULL COMMENT '总市值',
  `m_cap` decimal(20,0) DEFAULT NULL COMMENT '流通市值',
  `created_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=54035 DEFAULT CHARSET=utf8 COMMENT='行情数据（网易）';

SET FOREIGN_KEY_CHECKS = 1;
