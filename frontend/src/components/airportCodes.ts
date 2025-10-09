/**
 * 中国机场三字码/四字码数据
 * 数据来源：民航局标准数据
 */

export interface Airport {
  region: string      // 服务地区
  iata: string        // 三字码
  icao: string        // 四字码
  name: string        // 中文名称
  english: string     // 英文名称
  city: string        // 所属城市
}

export const airports: Airport[] = [
  // 北京市
  { region: '北京市', city: '北京', iata: 'NAY', icao: 'ZBNY', name: '北京南苑机场', english: 'NANYUAN' },
  { region: '北京市', city: '北京', iata: 'PEK', icao: 'ZBAA', name: '北京首都国际机场', english: 'BEIJING' },
  { region: '北京市', city: '北京', iata: 'PKX', icao: 'ZBAD', name: '北京大兴国际机场', english: 'DAXING' },
  
  // 天津市
  { region: '天津市', city: '天津', iata: 'TSN', icao: 'ZBTJ', name: '天津滨海国际机场', english: 'TIANJIN' },
  
  // 河北省
  { region: '河北省', city: '张家口', iata: 'ZQZ', icao: 'ZBZJ', name: '张家口宁远机场', english: 'ZHANGJIAKOU' },
  { region: '河北省', city: '邯郸', iata: 'HDG', icao: 'ZBHD', name: '邯郸机场', english: 'HANDAN' },
  { region: '河北省', city: '秦皇岛', iata: 'SHP', icao: 'ZBSH', name: '秦皇岛山海关机场', english: 'QINHUANGDAO' },
  { region: '河北省', city: '唐山', iata: 'TVS', icao: 'ZBTS', name: '唐山三女河机场', english: 'TANGSHAN' },
  { region: '河北省', city: '石家庄', iata: 'SJW', icao: 'ZBSJ', name: '石家庄正定国际机场', english: 'SHIJIAZHUANG' },
  
  // 山西省
  { region: '山西省', city: '太原', iata: 'TYN', icao: 'ZBYN', name: '太原武宿国际机场', english: 'TAIYUAN' },
  { region: '山西省', city: '大同', iata: 'DAT', icao: 'ZBDT', name: '大同云冈机场', english: 'DATONG' },
  { region: '山西省', city: '运城', iata: 'YCU', icao: 'ZBYC', name: '运城机场', english: 'YUNCHENG' },
  { region: '山西省', city: '长治', iata: 'CIH', icao: 'ZBCZ', name: '长治王村机场', english: 'CHANGZHI' },
  
  // 上海市
  { region: '上海市', city: '上海', iata: 'SHA', icao: 'ZSSS', name: '上海虹桥国际机场', english: 'HONGQIAO' },
  { region: '上海市', city: '上海', iata: 'PVG', icao: 'ZSPD', name: '上海浦东国际机场', english: 'PUDONG' },
  
  // 江苏省
  { region: '江苏省', city: '南京', iata: 'NKG', icao: 'ZSNJ', name: '南京禄口国际机场', english: 'NANJING' },
  { region: '江苏省', city: '无锡', iata: 'WUX', icao: 'ZSWX', name: '苏南硕放国际机场', english: 'WUXI' },
  { region: '江苏省', city: '常州', iata: 'CZX', icao: 'ZSCG', name: '常州奔牛机场', english: 'CHANGZHOU' },
  { region: '江苏省', city: '徐州', iata: 'XUZ', icao: 'ZSXZ', name: '徐州观音机场', english: 'XUZHOU' },
  { region: '江苏省', city: '扬州', iata: 'YTY', icao: 'ZSYA', name: '扬州泰州机场', english: 'YANGZHOU' },
  { region: '江苏省', city: '南通', iata: 'NTG', icao: 'ZSNT', name: '南通兴东机场', english: 'NANTONG' },
  { region: '江苏省', city: '盐城', iata: 'YNZ', icao: 'ZSYN', name: '盐城南洋机场', english: 'YANCHENG' },
  { region: '江苏省', city: '连云港', iata: 'LYG', icao: 'ZSLG', name: '连云港白塔埠机场', english: 'LIANYUNGANG' },
  
  // 浙江省
  { region: '浙江省', city: '杭州', iata: 'HGH', icao: 'ZSHC', name: '杭州萧山国际机场', english: 'HANGZHOU' },
  { region: '浙江省', city: '宁波', iata: 'NGB', icao: 'ZSNB', name: '宁波栎社国际机场', english: 'NINGBO' },
  { region: '浙江省', city: '温州', iata: 'WNZ', icao: 'ZSWZ', name: '温州龙湾国际机场', english: 'WENZHOU' },
  { region: '浙江省', city: '台州', iata: 'HYN', icao: 'ZSLQ', name: '台州路桥机场', english: 'TAIZHOU' },
  { region: '浙江省', city: '舟山', iata: 'HSN', icao: 'ZSZS', name: '舟山普陀山机场', english: 'ZHOUSHAN' },
  
  // 安徽省
  { region: '安徽省', city: '合肥', iata: 'HFE', icao: 'ZSOF', name: '合肥新桥国际机场', english: 'HEFEI' },
  { region: '安徽省', city: '黄山', iata: 'TXN', icao: 'ZSTX', name: '黄山屯溪机场', english: 'HUANGSHAN' },
  { region: '安徽省', city: '阜阳', iata: 'FUG', icao: 'ZSFY', name: '阜阳西关机场', english: 'FUYANG' },
  
  // 福建省
  { region: '福建省', city: '福州', iata: 'FOC', icao: 'ZSFZ', name: '福州长乐国际机场', english: 'FUZHOU' },
  { region: '福建省', city: '厦门', iata: 'XMN', icao: 'ZSAM', name: '厦门高崎国际机场', english: 'XIAMEN' },
  { region: '福建省', city: '泉州', iata: 'JJN', icao: 'ZSQZ', name: '泉州晋江机场', english: 'QUANZHOU' },
  { region: '福建省', city: '南平', iata: 'WUS', icao: 'ZSWY', name: '武夷山机场', english: 'WUYISHAN' },
  
  // 江西省
  { region: '江西省', city: '南昌', iata: 'KHN', icao: 'ZSCN', name: '南昌昌北国际机场', english: 'NANCHANG' },
  { region: '江西省', city: '赣州', iata: 'KOW', icao: 'ZSGZ', name: '赣州黄金机场', english: 'GANZHOU' },
  { region: '江西省', city: '景德镇', iata: 'JDZ', icao: 'ZSJD', name: '景德镇罗家机场', english: 'JINGDEZHEN' },
  { region: '江西省', city: '九江', iata: 'JIU', icao: 'ZSJJ', name: '九江庐山机场', english: 'JIUJIANG' },
  
  // 山东省
  { region: '山东省', city: '济南', iata: 'TNA', icao: 'ZSJN', name: '济南遥墙国际机场', english: 'JINAN' },
  { region: '山东省', city: '青岛', iata: 'TAO', icao: 'ZSQD', name: '青岛流亭国际机场', english: 'QINGDAO' },
  { region: '山东省', city: '烟台', iata: 'YNT', icao: 'ZSYT', name: '烟台莱山国际机场', english: 'YANTAI' },
  { region: '山东省', city: '威海', iata: 'WEH', icao: 'ZSWH', name: '威海国际机场', english: 'WEIHAI' },
  { region: '山东省', city: '临沂', iata: 'LYI', icao: 'ZSLY', name: '临沂沭埠岭机场', english: 'LINYI' },
  { region: '山东省', city: '潍坊', iata: 'WEF', icao: 'ZSWF', name: '潍坊机场', english: 'WEIFANG' },
  
  // 河南省
  { region: '河南省', city: '郑州', iata: 'CGO', icao: 'ZHCC', name: '郑州新郑国际机场', english: 'ZHENGZHOU' },
  { region: '河南省', city: '洛阳', iata: 'LYA', icao: 'ZHLY', name: '洛阳北郊机场', english: 'LUOYANG' },
  { region: '河南省', city: '南阳', iata: 'NNY', icao: 'ZHNY', name: '南阳姜营机场', english: 'NANYANG' },
  
  // 湖北省
  { region: '湖北省', city: '武汉', iata: 'WUH', icao: 'ZHHH', name: '武汉天河国际机场', english: 'WUHAN' },
  { region: '湖北省', city: '宜昌', iata: 'YIH', icao: 'ZHYC', name: '宜昌三峡机场', english: 'YICHANG' },
  { region: '湖北省', city: '恩施', iata: 'ENH', icao: 'ZHES', name: '恩施许家坪机场', english: 'ENSHI' },
  { region: '湖北省', city: '襄阳', iata: 'XFN', icao: 'ZHXF', name: '襄阳刘集机场', english: 'XIANGYANG' },
  
  // 湖南省
  { region: '湖南省', city: '长沙', iata: 'CSX', icao: 'ZGHA', name: '长沙黄花国际机场', english: 'CHANGSHA' },
  { region: '湖南省', city: '张家界', iata: 'DYG', icao: 'ZGDY', name: '张家界荷花国际机场', english: 'ZHANGJIAJIE' },
  { region: '湖南省', city: '常德', iata: 'CGD', icao: 'ZGCD', name: '常德桃花源机场', english: 'CHANGDE' },
  { region: '湖南省', city: '永州', iata: 'LLF', icao: 'ZGLG', name: '永州零陵机场', english: 'YONGZHOU' },
  
  // 广东省
  { region: '广东省', city: '广州', iata: 'CAN', icao: 'ZGGG', name: '广州白云国际机场', english: 'GUANGZHOU' },
  { region: '广东省', city: '深圳', iata: 'SZX', icao: 'ZGSZ', name: '深圳宝安国际机场', english: 'SHENZHEN' },
  { region: '广东省', city: '珠海', iata: 'ZUH', icao: 'ZGSD', name: '珠海金湾机场', english: 'ZHUHAI' },
  { region: '广东省', city: '揭阳', iata: 'SWA', icao: 'ZGOW', name: '揭阳潮汕机场', english: 'JIEYANG' },
  { region: '广东省', city: '湛江', iata: 'ZHA', icao: 'ZGZJ', name: '湛江机场', english: 'ZHANJIANG' },
  { region: '广东省', city: '惠州', iata: 'HUZ', icao: 'ZGHZ', name: '惠州机场', english: 'HUIZHOU' },
  { region: '广东省', city: '佛山', iata: 'FUO', icao: 'ZGFS', name: '佛山机场', english: 'FOSHAN' },
  
  // 广西壮族自治区
  { region: '广西壮族自治区', city: '南宁', iata: 'NNG', icao: 'ZGNN', name: '南宁吴圩国际机场', english: 'NANNING' },
  { region: '广西壮族自治区', city: '桂林', iata: 'KWL', icao: 'ZGKL', name: '桂林两江国际机场', english: 'GUILIN' },
  { region: '广西壮族自治区', city: '北海', iata: 'BHY', icao: 'ZGBH', name: '北海福成机场', english: 'BEIHAI' },
  { region: '广西壮族自治区', city: '柳州', iata: 'LZH', icao: 'ZGZH', name: '柳州白莲机场', english: 'LIUZHOU' },
  
  // 海南省
  { region: '海南省', city: '海口', iata: 'HAK', icao: 'ZJHK', name: '海口美兰国际机场', english: 'HAIKOU' },
  { region: '海南省', city: '三亚', iata: 'SYX', icao: 'ZJSY', name: '三亚凤凰国际机场', english: 'SANYA' },
  
  // 重庆市
  { region: '重庆市', city: '重庆', iata: 'CKG', icao: 'ZUCK', name: '重庆江北国际机场', english: 'CHONGQING' },
  { region: '重庆市', city: '万州', iata: 'WXN', icao: 'ZUWX', name: '万州五桥机场', english: 'WANZHOU' },
  
  // 四川省
  { region: '四川省', city: '成都', iata: 'CTU', icao: 'ZUUU', name: '成都双流国际机场', english: 'CHENGDU' },
  { region: '四川省', city: '成都', iata: 'TFU', icao: 'ZUTF', name: '成都天府国际机场', english: 'TIANFU' },
  { region: '四川省', city: '绵阳', iata: 'MIG', icao: 'ZUMY', name: '绵阳南郊机场', english: 'MIANYANG' },
  { region: '四川省', city: '九寨沟', iata: 'JZH', icao: 'ZUJZ', name: '九寨黄龙机场', english: 'JIUZHAIGOU' },
  { region: '四川省', city: '西昌', iata: 'XIC', icao: 'ZUXC', name: '西昌青山机场', english: 'XICHANG' },
  
  // 贵州省
  { region: '贵州省', city: '贵阳', iata: 'KWE', icao: 'ZUGY', name: '贵阳龙洞堡国际机场', english: 'GUIYANG' },
  { region: '贵州省', city: '遵义', iata: 'ZYI', icao: 'ZUZY', name: '遵义新舟机场', english: 'ZUNYI' },
  { region: '贵州省', city: '铜仁', iata: 'TEN', icao: 'ZUTR', name: '铜仁凤凰机场', english: 'TONGREN' },
  
  // 云南省
  { region: '云南省', city: '昆明', iata: 'KMG', icao: 'ZPPP', name: '昆明长水国际机场', english: 'KUNMING' },
  { region: '云南省', city: '丽江', iata: 'LJG', icao: 'ZPLJ', name: '丽江三义机场', english: 'LIJIANG' },
  { region: '云南省', city: '大理', iata: 'DLU', icao: 'ZPDL', name: '大理机场', english: 'DALIXIAGUAN' },
  { region: '云南省', city: '西双版纳', iata: 'JHG', icao: 'ZPJH', name: '西双版纳嘎洒国际机场', english: 'JINGHONG' },
  { region: '云南省', city: '迪庆', iata: 'DIG', icao: 'ZPDQ', name: '迪庆香格里拉机场', english: 'DIQING' },
  
  // 西藏自治区
  { region: '西藏自治区', city: '拉萨', iata: 'LXA', icao: 'ZULS', name: '拉萨贡嘎机场', english: 'LHASA' },
  { region: '西藏自治区', city: '昌都', iata: 'BPX', icao: 'ZUBD', name: '昌都邦达机场', english: 'CHAMDO' },
  { region: '西藏自治区', city: '林芝', iata: 'LZY', icao: 'ZUNZ', name: '林芝米林机场', english: 'NYINGCHI' },
  
  // 陕西省
  { region: '陕西省', city: '西安', iata: 'XIY', icao: 'ZLXY', name: '西安咸阳国际机场', english: 'XIAN' },
  { region: '陕西省', city: '榆林', iata: 'UYN', icao: 'ZLYL', name: '榆林榆阳机场', english: 'YULIN' },
  { region: '陕西省', city: '延安', iata: 'ENY', icao: 'ZLYA', name: '延安二十里堡机场', english: 'YANAN' },
  { region: '陕西省', city: '汉中', iata: 'HZG', icao: 'ZLHZ', name: '汉中西关机场', english: 'HANZHONG' },
  
  // 甘肃省
  { region: '甘肃省', city: '兰州', iata: 'LHW', icao: 'ZLLL', name: '兰州中川机场', english: 'LANZHOU' },
  { region: '甘肃省', city: '敦煌', iata: 'DNH', icao: 'ZLDH', name: '敦煌机场', english: 'DUNHUANG' },
  { region: '甘肃省', city: '嘉峪关', iata: 'JGN', icao: 'ZLJQ', name: '嘉峪关机场', english: 'JIAYUGUAN' },
  { region: '甘肃省', city: '张掖', iata: 'YZY', icao: 'ZLZY', name: '张掖甘州机场', english: 'ZHANGYE' },
  
  // 青海省
  { region: '青海省', city: '西宁', iata: 'XNN', icao: 'ZLXN', name: '西宁曹家堡机场', english: 'XINING' },
  { region: '青海省', city: '格尔木', iata: 'GOQ', icao: 'ZLGM', name: '格尔木机场', english: 'GOLMUD' },
  
  // 宁夏回族自治区
  { region: '宁夏回族自治区', city: '银川', iata: 'INC', icao: 'ZLIC', name: '银川河东国际机场', english: 'YINCHUAN' },
  { region: '宁夏回族自治区', city: '中卫', iata: 'ZHY', icao: 'ZLZW', name: '中卫沙坡头机场', english: 'ZHONGWEI' },
  { region: '宁夏回族自治区', city: '固原', iata: 'GYU', icao: 'ZLGY', name: '固原六盘山机场', english: 'GUYUAN' },
  
  // 新疆维吾尔自治区
  { region: '新疆维吾尔自治区', city: '乌鲁木齐', iata: 'URC', icao: 'ZWWW', name: '乌鲁木齐地窝堡国际机场', english: 'URUMQI' },
  { region: '新疆维吾尔自治区', city: '喀什', iata: 'KHG', icao: 'ZWSH', name: '喀什机场', english: 'KASHGAR' },
  { region: '新疆维吾尔自治区', city: '伊宁', iata: 'YIN', icao: 'ZWYN', name: '伊宁机场', english: 'YINING' },
  { region: '新疆维吾尔自治区', city: '阿克苏', iata: 'AKU', icao: 'ZWAK', name: '阿克苏机场', english: 'AKSU' },
  { region: '新疆维吾尔自治区', city: '库尔勒', iata: 'KRL', icao: 'ZWKL', name: '库尔勒机场', english: 'KORLA' },
  { region: '新疆维吾尔自治区', city: '哈密', iata: 'HMI', icao: 'ZWHM', name: '哈密机场', english: 'HAMI' },
  
  // 东北三省
  { region: '辽宁省', city: '沈阳', iata: 'SHE', icao: 'ZYTX', name: '沈阳桃仙国际机场', english: 'SHENYANG' },
  { region: '辽宁省', city: '大连', iata: 'DLC', icao: 'ZYTL', name: '大连周水子国际机场', english: 'DALIAN' },
  { region: '辽宁省', city: '丹东', iata: 'DDG', icao: 'ZYDD', name: '丹东浪头机场', english: 'DANDONG' },
  
  { region: '吉林省', city: '长春', iata: 'CGQ', icao: 'ZYCC', name: '长春龙嘉国际机场', english: 'CHANGCHUN' },
  { region: '吉林省', city: '延边', iata: 'YNJ', icao: 'ZYYJ', name: '延吉朝阳川机场', english: 'YANJI' },
  
  { region: '黑龙江省', city: '哈尔滨', iata: 'HRB', icao: 'ZYHB', name: '哈尔滨太平国际机场', english: 'HARBIN' },
  { region: '黑龙江省', city: '齐齐哈尔', iata: 'NDG', icao: 'ZYQQ', name: '齐齐哈尔三家子机场', english: 'QIQIHAER' },
  { region: '黑龙江省', city: '牡丹江', iata: 'MDG', icao: 'ZYMD', name: '牡丹江海浪机场', english: 'MUDANJIANG' },
  
  // 香港澳门台湾
  { region: '香港特别行政区', city: '香港', iata: 'HKG', icao: 'VHHH', name: '香港国际机场', english: 'HONG KONG' },
  { region: '澳门特别行政区', city: '澳门', iata: 'MFM', icao: 'VMMC', name: '澳门国际机场', english: 'MACAU' },
  { region: '台湾省', city: '台北', iata: 'TSA', icao: 'RCSS', name: '台北松山机场', english: 'TAIBEI' },
  { region: '台湾省', city: '桃园', iata: 'TPE', icao: 'RCTP', name: '桃园国际机场', english: 'TAOYUAN' },
  { region: '台湾省', city: '高雄', iata: 'KHH', icao: 'RCKH', name: '高雄国际机场', english: 'GAOXIONG' }
]

/**
 * 根据城市名搜索机场
 */
export function searchAirportsByCity(cityName: string): Airport[] {
  return airports.filter(airport => 
    airport.city.includes(cityName) || 
    airport.name.includes(cityName)
  )
}

/**
 * 根据机场名搜索
 */
export function searchAirportsByName(keyword: string): Airport[] {
  const lowerKeyword = keyword.toLowerCase()
  return airports.filter(airport => 
    airport.name.includes(keyword) ||
    airport.city.includes(keyword) ||
    airport.english.toLowerCase().includes(lowerKeyword) ||
    airport.iata.toLowerCase().includes(lowerKeyword)
  ).slice(0, 20)  // 最多返回20个
}

/**
 * 根据三字码获取机场
 */
export function getAirportByCode(iataCode: string): Airport | undefined {
  return airports.find(airport => airport.iata === iataCode.toUpperCase())
}

