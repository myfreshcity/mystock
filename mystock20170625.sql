/*
 Navicat MySQL Data Transfer

 Source Server         : localhost
 Source Server Version : 50717
 Source Host           : localhost
 Source Database       : mystock

 Target Server Version : 50717
 File Encoding         : utf-8

 Date: 06/25/2017 09:50:18 AM
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
) ENGINE=InnoDB AUTO_INCREMENT=213 DEFAULT CHARSET=utf8;

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
--  Table structure for `hexun_finance_basic`
-- ----------------------------
DROP TABLE IF EXISTS `hexun_finance_basic`;
CREATE TABLE `hexun_finance_basic` (
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
--  Table structure for `my_stock_favor`
-- ----------------------------
DROP TABLE IF EXISTS `my_stock_favor`;
CREATE TABLE `my_stock_favor` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `code` varchar(255) DEFAULT NULL,
  `title` varchar(255) DEFAULT NULL COMMENT '题目',
  `url` varchar(255) DEFAULT NULL COMMENT '链接',
  `pub_date` date DEFAULT NULL COMMENT '发布时间',
  `src_type` varchar(50) NOT NULL COMMENT '来源类型',
  `created_time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=107 DEFAULT CHARSET=utf8 COMMENT='股票资讯收藏夹';

-- ----------------------------
--  Table structure for `my_stocks`
-- ----------------------------
DROP TABLE IF EXISTS `my_stocks`;
CREATE TABLE `my_stocks` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `code` varchar(255) DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  `market` char(2) DEFAULT NULL COMMENT '所在市场',
  `grow_cat` varchar(255) DEFAULT NULL COMMENT '成长类型',
  `tag` varchar(255) DEFAULT '' COMMENT '标签',
  `flag` int(4) DEFAULT '1' COMMENT '0-自选，1-备选',
  `in_price` decimal(10,2) DEFAULT '0.00' COMMENT '最近买入价',
  `in_date` date DEFAULT NULL COMMENT '最近买入时间',
  `user_id` int(11) DEFAULT NULL COMMENT '用户ID',
  `created_time` datetime DEFAULT NULL,
  `updated_time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `pk_my_stocks_code` (`code`) USING HASH
) ENGINE=MyISAM AUTO_INCREMENT=223 DEFAULT CHARSET=utf8;

-- ----------------------------
--  Table structure for `ostock_finance_data`
-- ----------------------------
DROP TABLE IF EXISTS `ostock_finance_data`;
CREATE TABLE `ostock_finance_data` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `code` varchar(255) DEFAULT NULL COMMENT '股票代码',
  `report_type` date DEFAULT NULL COMMENT '会计类型',
  `zyysr` decimal(20,0) DEFAULT NULL COMMENT '主营业务收入',
  `zyysr_qt` decimal(20,0) DEFAULT NULL COMMENT '单季主营业务收入',
  `zyysr_ttm` decimal(20,0) DEFAULT NULL COMMENT '连续四季度营业收入',
  `zyylr` decimal(20,0) DEFAULT NULL COMMENT '主营业务利润',
  `yylr` decimal(20,0) DEFAULT NULL COMMENT '营业利润',
  `yylr_qt` decimal(20,0) DEFAULT NULL COMMENT '单季度营业利润',
  `kjlr` decimal(20,0) DEFAULT NULL COMMENT '净利润(扣除非经常性损益后)',
  `jlr` decimal(20,0) DEFAULT NULL COMMENT '净利润',
  `jlr_qt` decimal(20,0) DEFAULT NULL COMMENT '单季度净利润',
  `jlr_ttm` decimal(20,0) DEFAULT NULL COMMENT '连续四季度净利润',
  `jyjxjl` decimal(20,0) DEFAULT NULL COMMENT '经营活动产生的现金流量净额',
  `jyjxjl_qt` decimal(20,0) DEFAULT NULL COMMENT '单季度经营现金流净额',
  `jyjxjl_ttm` decimal(20,0) DEFAULT NULL COMMENT '连续四季度经营现金流净额',
  `xjjze` decimal(20,0) DEFAULT '1' COMMENT '现金及现金等价物净增加额',
  `xjjze_qt` decimal(20,0) DEFAULT NULL COMMENT '单季度现金及现金等价物净增加额',
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
) ENGINE=MyISAM AUTO_INCREMENT=3404 DEFAULT CHARSET=utf8 COMMENT='财务数据（网易）';

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
) ENGINE=MyISAM AUTO_INCREMENT=61 DEFAULT CHARSET=utf8 COMMENT='相关股票';

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
--  Table structure for `stock_finance_data`
-- ----------------------------
DROP TABLE IF EXISTS `stock_finance_data`;
CREATE TABLE `stock_finance_data` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `code` varchar(255) DEFAULT NULL COMMENT '股票代码',
  `report_type` date DEFAULT NULL COMMENT '会计类型',
  `zyysr` decimal(20,0) DEFAULT NULL COMMENT '主营业务收入',
  `zyysr_qt` decimal(20,0) DEFAULT NULL COMMENT '单季主营业务收入',
  `zyysr_ttm` decimal(20,0) DEFAULT NULL COMMENT '连续四季度营业收入',
  `zyylr` decimal(20,0) DEFAULT NULL COMMENT '主营业务利润',
  `yylr` decimal(20,0) DEFAULT NULL COMMENT '营业利润',
  `yylr_qt` decimal(20,0) DEFAULT NULL COMMENT '单季度营业利润',
  `tzsy` decimal(20,0) DEFAULT NULL COMMENT '投资收益',
  `ywszje` decimal(20,0) DEFAULT NULL COMMENT '营业外收支净额',
  `lrze` decimal(20,0) DEFAULT NULL COMMENT '利润总额',
  `kf_jlr` decimal(20,0) DEFAULT NULL COMMENT '净利润(扣除非经常性损益后)',
  `jlr` decimal(20,0) DEFAULT NULL COMMENT '净利润',
  `jlr_qt` decimal(20,0) DEFAULT NULL COMMENT '单季度净利润',
  `jlr_ttm` decimal(20,0) DEFAULT NULL COMMENT '连续四季度净利润',
  `jlr_rate` decimal(10,2) DEFAULT '1.00' COMMENT '净利润增长率',
  `jyjxjl` decimal(20,0) DEFAULT NULL COMMENT '经营活动产生的现金流量净额',
  `jyjxjl_qt` decimal(20,0) DEFAULT NULL COMMENT '单季度经营现金流净额',
  `jyjxjl_ttm` decimal(20,0) DEFAULT NULL COMMENT '连续四季度经营现金流净额',
  `xjjze` decimal(20,0) DEFAULT '1' COMMENT '现金及现金等价物净增加额',
  `xjjze_qt` decimal(20,0) DEFAULT NULL COMMENT '单季度现金及现金等价物净增加额',
  `zzc` decimal(20,0) DEFAULT '1' COMMENT '总资产',
  `ldzc` decimal(20,0) DEFAULT '1' COMMENT '流动资产',
  `zfz` decimal(20,0) DEFAULT '1' COMMENT '总负债',
  `ldfz` decimal(20,0) DEFAULT '1' COMMENT '流动负债',
  `gdqy` decimal(20,0) DEFAULT '1' COMMENT '股东权益不含少数股东权益',
  `roe` decimal(10,2) DEFAULT '1.00' COMMENT '净资产收益率（摊薄)(%)',
  `created_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=2669 DEFAULT CHARSET=utf8 COMMENT='财务数据（网易）';

-- ----------------------------
--  Table structure for `stock_holder`
-- ----------------------------
DROP TABLE IF EXISTS `stock_holder`;
CREATE TABLE `stock_holder` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `code` varchar(10) DEFAULT NULL COMMENT '股票代码',
  `rank` smallint(5) DEFAULT NULL COMMENT '持股排名',
  `holder_name` varchar(255) DEFAULT NULL COMMENT '股东名称',
  `holder_code` varchar(255) DEFAULT NULL COMMENT '股东代码',
  `amount` decimal(20,0) DEFAULT NULL COMMENT '数量',
  `rate` decimal(10,2) DEFAULT NULL COMMENT '比例',
  `holder_type` varchar(100) DEFAULT NULL COMMENT '股东机构类型',
  `holder_parent` varchar(255) DEFAULT NULL COMMENT '股东母机构',
  `holder_nature` varchar(100) DEFAULT NULL COMMENT '股本类型',
  `report_date` date DEFAULT NULL COMMENT '报告日期',
  `created_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=1019824 DEFAULT CHARSET=utf8 COMMENT='流通股东表（雪球）';

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
) ENGINE=MyISAM AUTO_INCREMENT=11179 DEFAULT CHARSET=utf8 COMMENT='机构流通股东汇总表（雪球，统计最近一期的持股情况）';

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
) ENGINE=MyISAM AUTO_INCREMENT=25483 DEFAULT CHARSET=utf8 COMMENT='行情数据（网易）';

-- ----------------------------
--  Table structure for `xueqiu_finance_asset`
-- ----------------------------
DROP TABLE IF EXISTS `xueqiu_finance_asset`;
CREATE TABLE `xueqiu_finance_asset` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `code` varchar(255) DEFAULT NULL COMMENT '股票代码',
  `report_type` date DEFAULT NULL COMMENT '会计类型',
  `ldzc_hbzj` decimal(20,0) DEFAULT NULL COMMENT '货币资金',
  `ldzc_jyxjrzc` decimal(20,0) DEFAULT NULL COMMENT '交易性金融资产',
  `ldzc_yspj` decimal(20,0) DEFAULT NULL COMMENT '应收票据',
  `ldzc_yszk` decimal(20,0) DEFAULT NULL COMMENT '应收账款',
  `ldzc_yfkx` decimal(20,0) DEFAULT NULL COMMENT '预付款项',
  `ldzc_yslx` decimal(20,0) DEFAULT NULL COMMENT '应收利息',
  `ldzc_ysgl` decimal(20,0) DEFAULT NULL COMMENT '应收股利',
  `ldzc_o_ysk` decimal(20,0) DEFAULT NULL COMMENT '其他应收款',
  `ldzc_ch` decimal(20,0) DEFAULT NULL COMMENT '存货',
  `ldzc_o` decimal(20,0) DEFAULT NULL COMMENT '其他流动资产',
  `ldzc_all` decimal(20,0) DEFAULT NULL COMMENT '流动资产合计',
  `fld_jrzc` decimal(20,0) DEFAULT '1' COMMENT '可供出售金融资产',
  `fld_dqtz` decimal(20,0) DEFAULT '1' COMMENT '持有至到期投资',
  `fld_ysk` decimal(20,0) DEFAULT '1' COMMENT '长期应收款',
  `fld_gqtz` decimal(20,0) DEFAULT '1' COMMENT '长期股权投资',
  `fld_tzfdc` decimal(20,0) DEFAULT '1' COMMENT '投资性房地产',
  `fld_gdzc` decimal(20,0) DEFAULT NULL COMMENT '固定资产',
  `fld_zjgc` decimal(20,0) DEFAULT NULL COMMENT '在建工程',
  `fld_gcwz` decimal(20,0) DEFAULT NULL COMMENT '工程物资',
  `fld_gdzcql` decimal(20,0) DEFAULT NULL COMMENT '固定资产清理',
  `fld_wxzc` decimal(20,0) DEFAULT NULL COMMENT '无形资产',
  `fld_kfzc` decimal(20,0) DEFAULT NULL COMMENT '开发支出',
  `fld_sy` decimal(20,0) DEFAULT NULL COMMENT '商誉',
  `fld_cqtpfy` decimal(20,0) DEFAULT NULL COMMENT '长期待摊费用',
  `fld_dysds` decimal(20,0) DEFAULT NULL COMMENT '递延所得税资产',
  `fld_other` decimal(20,0) DEFAULT NULL COMMENT '其他非流动资产',
  `fld_all` decimal(20,0) DEFAULT NULL COMMENT '非流动资产合计',
  `zc_all` decimal(20,0) DEFAULT NULL COMMENT '资产总计',
  `ldfz_tqjk` decimal(20,0) DEFAULT NULL COMMENT '短期借款',
  `ldfz_yfpj` decimal(20,0) DEFAULT '1' COMMENT '应付票据',
  `ldfz_yfzk` decimal(20,0) DEFAULT '1' COMMENT '应付账款',
  `ldfz_yszk` decimal(20,0) DEFAULT '1' COMMENT '预收账款',
  `ldfz_zgxc` decimal(20,0) DEFAULT '1' COMMENT '应付职工薪酬',
  `ldfz_yjsf` decimal(20,0) DEFAULT '1' COMMENT '应交税费',
  `ldfz_yflx` decimal(20,0) DEFAULT '1' COMMENT '应付利息',
  `ldfz_yfgl` decimal(20,0) DEFAULT '1' COMMENT '应付股利',
  `ldfz_o_yfk` decimal(20,0) DEFAULT '1' COMMENT '其他应付款',
  `ldfz_ynfldfz` decimal(20,0) DEFAULT '1' COMMENT '一年内到期的非流动负债',
  `ldfz_other` decimal(20,0) DEFAULT '1' COMMENT '其他流动负债',
  `ldfz_all` decimal(20,0) DEFAULT NULL COMMENT '流动负债合计',
  `fz_cqjk` decimal(20,0) DEFAULT NULL COMMENT '长期借款',
  `fz_yfzq` decimal(20,0) DEFAULT NULL COMMENT '应付债券',
  `fz_cqyfk` decimal(20,0) DEFAULT NULL COMMENT '长期应付款',
  `fz_zxyfk` decimal(20,0) DEFAULT NULL COMMENT '专项应付款',
  `fz_yjffz` decimal(20,0) DEFAULT NULL COMMENT '预计非流动负债',
  `fz_dysy` decimal(20,0) DEFAULT NULL COMMENT '长期递延收益',
  `fz_dysdsfz` decimal(20,0) DEFAULT NULL COMMENT '递延所得税负债',
  `fz_other` decimal(20,0) DEFAULT NULL COMMENT '非流动负债合计',
  `fz_all` decimal(20,0) DEFAULT NULL COMMENT '负债合计',
  `gq_sszb` decimal(20,0) DEFAULT NULL COMMENT '实收资本(或股本)',
  `gd_zbgj` decimal(20,0) DEFAULT NULL COMMENT '资本公积',
  `gd_yygj` decimal(20,0) DEFAULT NULL COMMENT '盈余公积',
  `gd_wflr` decimal(20,0) DEFAULT NULL COMMENT '未分配利润',
  `gd_mqy` decimal(20,0) DEFAULT NULL COMMENT '归属于母公司股东权益合计',
  `gd_ssgd` decimal(20,0) DEFAULT NULL COMMENT '少数股东权益',
  `gd_all` decimal(20,0) DEFAULT NULL COMMENT '所有者权益(或股东权益)合计',
  `fz_gd_all` decimal(20,0) DEFAULT NULL COMMENT '负债和所有者权益',
  `created_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=2410 DEFAULT CHARSET=utf8 COMMENT='资产负债表数据（雪球）';

-- ----------------------------
--  Table structure for `xueqiu_finance_cash`
-- ----------------------------
DROP TABLE IF EXISTS `xueqiu_finance_cash`;
CREATE TABLE `xueqiu_finance_cash` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `code` varchar(255) DEFAULT NULL COMMENT '股票代码',
  `report_type` date DEFAULT NULL COMMENT '会计类型',
  `jy_in_splwxj` decimal(20,0) DEFAULT NULL COMMENT '销售商品、提供劳务收到的现金',
  `jy_in_sffh` decimal(20,0) DEFAULT NULL COMMENT '收到的税费返还',
  `jy_in_other` decimal(20,0) DEFAULT NULL COMMENT '收到的其他与经营活动有关的现金',
  `jy_in_all` decimal(20,0) DEFAULT NULL COMMENT '经营活动现金流入小计',
  `jy_out_splwxj` decimal(20,0) DEFAULT NULL COMMENT '购买商品、接受劳务支付的现金',
  `jy_out_gzfl` decimal(20,0) DEFAULT NULL COMMENT '支付给职工以及为职工支付的现金',
  `jy_out_sf` decimal(20,0) DEFAULT NULL COMMENT '支付的各项税费',
  `jy_out_other` decimal(20,0) DEFAULT NULL COMMENT '支付的其他与经营活动有关的现金',
  `jy_out_all` decimal(20,0) DEFAULT NULL COMMENT '经营活动现金流出小计',
  `jy_net` decimal(20,0) DEFAULT NULL COMMENT '经营活动产生的现金流量净额',
  `tz_in_tz` decimal(20,0) DEFAULT '1' COMMENT '收回投资所收到的现金',
  `tz_in_tzsy` decimal(20,0) DEFAULT '1' COMMENT '取得投资收益收到的现金',
  `tz_in_gdtz` decimal(20,0) DEFAULT '1' COMMENT '处置固定资产、无形资产和其他长期资产所回收的现金净额',
  `tz_in_zgs` decimal(20,0) DEFAULT '1' COMMENT '处置子公司及其他营业单位收到的现金净额',
  `tz_in_other` decimal(20,0) DEFAULT '1' COMMENT '收到的其他与投资活动有关的现金',
  `tz_in_all` decimal(20,0) DEFAULT '1' COMMENT '投资活动现金流入小计',
  `tz_out_gdtz` decimal(20,0) DEFAULT '1' COMMENT '购建固定资产、无形资产和其他长期资产所支付的现金',
  `tz_out_tz` decimal(20,0) DEFAULT '1' COMMENT '投资所支付的现金',
  `tz_out_zgs` decimal(20,0) DEFAULT '1' COMMENT '取得子公司及其他营业单位支付的现金净额  ',
  `tz_out_other` decimal(20,0) DEFAULT '1' COMMENT '支付的其他与投资活动有关的现金',
  `tz_out_all` decimal(20,0) DEFAULT '1' COMMENT '投资活动现金流出小计',
  `tz_net` decimal(20,0) DEFAULT '1' COMMENT '投资活动产生的现金流量净额',
  `cz_in_tz` decimal(20,0) DEFAULT '1' COMMENT '吸收投资收到的现金',
  `cz_in_zgstz` decimal(20,0) DEFAULT '1' COMMENT '其中：子公司吸收少数股东投资收到的现金',
  `cz_in_jk` decimal(20,0) DEFAULT '1' COMMENT '取得借款收到的现金',
  `cz_in_other` decimal(20,0) DEFAULT NULL COMMENT '收到其他与筹资活动有关的现金',
  `cz_in_all` decimal(20,0) DEFAULT NULL COMMENT '筹资活动现金流入小计',
  `cz_out_zw` decimal(20,0) DEFAULT NULL COMMENT '偿还债务支付的现金',
  `cz_out_lx` decimal(20,0) DEFAULT NULL COMMENT '分配股利、利润或偿付利息所支付的现金',
  `cz_out_zgslx` decimal(20,0) DEFAULT NULL COMMENT '其中：子公司支付给少数股东的股利，利润',
  `cz_out_other` decimal(20,0) DEFAULT NULL COMMENT '支付其他与筹资活动有关的现金',
  `cz_out_all` decimal(20,0) DEFAULT NULL COMMENT '筹资活动现金流出小计',
  `cz_net` decimal(20,0) DEFAULT NULL COMMENT '筹资活动产生的现金流量净',
  `lvbd` decimal(20,0) DEFAULT NULL COMMENT '汇率变动对现金及现金等价物的影响',
  `xj_net` decimal(20,0) DEFAULT NULL COMMENT '现金及现金等价物净增加额',
  `qc_xj_ye` decimal(20,0) DEFAULT NULL COMMENT '期初现金及现金等价物余额',
  `qm_xj_ye` decimal(20,0) DEFAULT NULL COMMENT '期末现金及现金等价物余额',
  `created_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=2401 DEFAULT CHARSET=utf8 COMMENT='现金流量表数据（雪球）';

-- ----------------------------
--  Table structure for `xueqiu_finance_income`
-- ----------------------------
DROP TABLE IF EXISTS `xueqiu_finance_income`;
CREATE TABLE `xueqiu_finance_income` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `code` varchar(255) NOT NULL DEFAULT '' COMMENT '股票代码',
  `report_type` date DEFAULT NULL COMMENT '会计类型',
  `in_all` decimal(20,0) DEFAULT NULL COMMENT '营业总收入',
  `in_yysr` decimal(20,0) DEFAULT NULL COMMENT '营业收入',
  `in_lx` decimal(20,0) DEFAULT NULL COMMENT '利息收入',
  `in_sxyj` decimal(20,0) DEFAULT NULL COMMENT '手续费及佣金收入',
  `out_all` decimal(20,0) DEFAULT NULL COMMENT '营业总成本',
  `out_yycb` decimal(20,0) DEFAULT NULL COMMENT '营业成本',
  `out_lx` decimal(20,0) DEFAULT NULL COMMENT '利息支出',
  `out_sxyj` decimal(20,0) DEFAULT NULL COMMENT '手续费及佣金支出',
  `out_yys` decimal(20,0) DEFAULT NULL COMMENT '营业税金及附加',
  `out_ss` decimal(20,0) DEFAULT NULL COMMENT '销售费用',
  `out_gl` decimal(20,0) DEFAULT '1' COMMENT '管理费用',
  `out_cw` decimal(20,0) DEFAULT '1' COMMENT '财务费用',
  `out_zcjz` decimal(20,0) DEFAULT '1' COMMENT '资产减值损失',
  `out_gyjz` decimal(20,0) DEFAULT '1' COMMENT '公允价值变动收益',
  `out_tzsy` decimal(20,0) DEFAULT '1' COMMENT '投资收益',
  `out_lh_tzsy` decimal(20,0) DEFAULT NULL COMMENT '其中:对联营企业和合营企业的投资收益',
  `lr_all` decimal(20,0) DEFAULT NULL COMMENT '营业利润',
  `lr_o_in` decimal(20,0) DEFAULT NULL COMMENT '营业外收入',
  `lr_o_out` decimal(20,0) DEFAULT NULL COMMENT '营业外支出',
  `lr_fldzccz` decimal(20,0) DEFAULT NULL COMMENT '非流动资产处置损失',
  `lr_total` decimal(20,0) DEFAULT NULL COMMENT '利润总额',
  `lr_sdfy` decimal(20,0) DEFAULT NULL COMMENT '所得税费用',
  `lr_net` decimal(20,0) DEFAULT NULL COMMENT '净利润',
  `lr_m_net` decimal(20,0) DEFAULT NULL COMMENT '归属于母公司净利润',
  `created_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=2436 DEFAULT CHARSET=utf8 COMMENT='利润表数据（雪球）';

-- ----------------------------
--  Table structure for `yahoo_trade_basic`
-- ----------------------------
DROP TABLE IF EXISTS `yahoo_trade_basic`;
CREATE TABLE `yahoo_trade_basic` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `code` varchar(255) DEFAULT NULL COMMENT '股票代码',
  `trade_date` date DEFAULT NULL COMMENT '交易日期',
  `close` decimal(10,2) DEFAULT NULL COMMENT '收盘价',
  `adj_close` decimal(10,2) DEFAULT NULL COMMENT '复权价',
  `volume` decimal(20,0) DEFAULT NULL COMMENT '交易量',
  `created_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=5215 DEFAULT CHARSET=utf8 COMMENT='基本行情指标（yahoo）';

SET FOREIGN_KEY_CHECKS = 1;
