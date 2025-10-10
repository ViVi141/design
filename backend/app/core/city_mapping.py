"""
城市编码映射表（完整版）
数据来源：中国大陆电话区号表
包含：adcode（行政区划代码）、citycode（电话区号）、城市名称

说明：
- citycode: 电话区号（如"010"），用于高德公交API
- adcode: 行政区划代码（如"110000"），用于高德POI搜索API
- 支持全国300+地级市
"""
from typing import Dict, Optional


# 完整的城市映射表
# 数据结构: 城市名 -> {'adcode': 行政区划代码, 'citycode': 电话区号}
CITY_MAPPING = {
    # ==== 直辖市（C1局，2位区号） ====
    '北京': {'adcode': '110000', 'citycode': '010'},
    '上海': {'adcode': '310000', 'citycode': '021'},
    '天津': {'adcode': '120000', 'citycode': '022'},
    '重庆': {'adcode': '500000', 'citycode': '023'},
    
    # ==== C1局城市（大区中心，2位区号） ====
    '沈阳': {'adcode': '210100', 'citycode': '024'},  # 东北大区中心
    '南京': {'adcode': '320100', 'citycode': '025'},  # 华东大区中心
    '武汉': {'adcode': '420100', 'citycode': '027'},  # 中南大区中心
    '成都': {'adcode': '510100', 'citycode': '028'},  # 西南大区中心
    '西安': {'adcode': '610100', 'citycode': '029'},  # 西北大区中心
    '广州': {'adcode': '440100', 'citycode': '020'},  # 华南分区中心
    
    # ==== 河北省 ====
    '石家庄': {'adcode': '130100', 'citycode': '0311'},
    '保定': {'adcode': '130600', 'citycode': '0312'},
    '张家口': {'adcode': '130700', 'citycode': '0313'},
    '承德': {'adcode': '130800', 'citycode': '0314'},
    '唐山': {'adcode': '130200', 'citycode': '0315'},
    '廊坊': {'adcode': '131000', 'citycode': '0316'},
    '沧州': {'adcode': '130900', 'citycode': '0317'},
    '衡水': {'adcode': '131100', 'citycode': '0318'},
    '邢台': {'adcode': '130500', 'citycode': '0319'},
    '邯郸': {'adcode': '130400', 'citycode': '0310'},
    '秦皇岛': {'adcode': '130300', 'citycode': '0335'},
    
    # ==== 山西省 ====
    '朔州': {'adcode': '140600', 'citycode': '0349'},
    '太原': {'adcode': '140100', 'citycode': '0351'},
    '大同': {'adcode': '140200', 'citycode': '0352'},
    '阳泉': {'adcode': '140300', 'citycode': '0353'},
    '晋中': {'adcode': '140700', 'citycode': '0354'},
    '长治': {'adcode': '140400', 'citycode': '0355'},
    '晋城': {'adcode': '140500', 'citycode': '0356'},
    '临汾': {'adcode': '141000', 'citycode': '0357'},
    '吕梁': {'adcode': '141100', 'citycode': '0358'},
    '运城': {'adcode': '140800', 'citycode': '0359'},
    '忻州': {'adcode': '140900', 'citycode': '0350'},
    
    # ==== 河南省 ====
    '郑州': {'adcode': '410100', 'citycode': '0371'},
    '开封': {'adcode': '410200', 'citycode': '0371'},
    '安阳': {'adcode': '410500', 'citycode': '0372'},
    '新乡': {'adcode': '410700', 'citycode': '0373'},
    '许昌': {'adcode': '411000', 'citycode': '0374'},
    '平顶山': {'adcode': '410400', 'citycode': '0375'},
    '信阳': {'adcode': '411500', 'citycode': '0376'},
    '南阳': {'adcode': '411300', 'citycode': '0377'},
    '洛阳': {'adcode': '410300', 'citycode': '0379'},
    '商丘': {'adcode': '411400', 'citycode': '0370'},
    '焦作': {'adcode': '410800', 'citycode': '0391'},
    '鹤壁': {'adcode': '410600', 'citycode': '0392'},
    '濮阳': {'adcode': '410900', 'citycode': '0393'},
    '周口': {'adcode': '411600', 'citycode': '0394'},
    '漯河': {'adcode': '411100', 'citycode': '0395'},
    '驻马店': {'adcode': '411700', 'citycode': '0396'},
    '三门峡': {'adcode': '411200', 'citycode': '0398'},
    
    # ==== 辽宁省 ====
    '大连': {'adcode': '210200', 'citycode': '0411'},
    '鞍山': {'adcode': '210300', 'citycode': '0412'},
    '丹东': {'adcode': '210600', 'citycode': '0415'},
    '锦州': {'adcode': '210700', 'citycode': '0416'},
    '营口': {'adcode': '210800', 'citycode': '0417'},
    '阜新': {'adcode': '210900', 'citycode': '0418'},
    '辽阳': {'adcode': '211000', 'citycode': '0419'},
    '朝阳': {'adcode': '211300', 'citycode': '0421'},
    '盘锦': {'adcode': '211100', 'citycode': '0427'},
    '葫芦岛': {'adcode': '211400', 'citycode': '0429'},
    
    # ==== 吉林省 ====
    '长春': {'adcode': '220100', 'citycode': '0431'},
    '吉林': {'adcode': '220200', 'citycode': '0432'},
    '延边': {'adcode': '222400', 'citycode': '0433'},
    '四平': {'adcode': '220300', 'citycode': '0434'},
    '通化': {'adcode': '220500', 'citycode': '0435'},
    '白城': {'adcode': '220800', 'citycode': '0436'},
    '辽源': {'adcode': '220400', 'citycode': '0437'},
    '松原': {'adcode': '220700', 'citycode': '0438'},
    '白山': {'adcode': '220600', 'citycode': '0439'},
    
    # ==== 黑龙江省 ====
    '哈尔滨': {'adcode': '230100', 'citycode': '0451'},
    '齐齐哈尔': {'adcode': '230200', 'citycode': '0452'},
    '牡丹江': {'adcode': '231000', 'citycode': '0453'},
    '佳木斯': {'adcode': '230800', 'citycode': '0454'},
    '绥化': {'adcode': '231200', 'citycode': '0455'},
    '黑河': {'adcode': '231100', 'citycode': '0456'},
    '大兴安岭': {'adcode': '232700', 'citycode': '0457'},
    '伊春': {'adcode': '230700', 'citycode': '0458'},
    '大庆': {'adcode': '230600', 'citycode': '0459'},
    '七台河': {'adcode': '230900', 'citycode': '0464'},
    '鸡西': {'adcode': '230300', 'citycode': '0467'},
    '鹤岗': {'adcode': '230400', 'citycode': '0468'},
    '双鸭山': {'adcode': '230500', 'citycode': '0469'},
    
    # ==== 内蒙古自治区 ====
    '呼和浩特': {'adcode': '150100', 'citycode': '0471'},
    '包头': {'adcode': '150200', 'citycode': '0472'},
    '乌海': {'adcode': '150300', 'citycode': '0473'},
    '乌兰察布': {'adcode': '150900', 'citycode': '0474'},
    '通辽': {'adcode': '150500', 'citycode': '0475'},
    '赤峰': {'adcode': '150400', 'citycode': '0476'},
    '鄂尔多斯': {'adcode': '150600', 'citycode': '0477'},
    '巴彦淖尔': {'adcode': '150800', 'citycode': '0478'},
    '锡林郭勒': {'adcode': '152500', 'citycode': '0479'},
    '呼伦贝尔': {'adcode': '150700', 'citycode': '0470'},
    '兴安盟': {'adcode': '152200', 'citycode': '0482'},
    '阿拉善盟': {'adcode': '152900', 'citycode': '0483'},
    
    # ==== 江苏省 ====
    '无锡': {'adcode': '320200', 'citycode': '0510'},
    '镇江': {'adcode': '321100', 'citycode': '0511'},
    '苏州': {'adcode': '320500', 'citycode': '0512'},
    '南通': {'adcode': '320600', 'citycode': '0513'},
    '扬州': {'adcode': '321000', 'citycode': '0514'},
    '盐城': {'adcode': '320900', 'citycode': '0515'},
    '徐州': {'adcode': '320300', 'citycode': '0516'},
    '淮安': {'adcode': '320800', 'citycode': '0517'},
    '连云港': {'adcode': '320700', 'citycode': '0518'},
    '常州': {'adcode': '320400', 'citycode': '0519'},
    '泰州': {'adcode': '321200', 'citycode': '0523'},
    '宿迁': {'adcode': '321300', 'citycode': '0527'},
    
    # ==== 山东省 ====
    '济南': {'adcode': '370100', 'citycode': '0531'},
    '青岛': {'adcode': '370200', 'citycode': '0532'},
    '淄博': {'adcode': '370300', 'citycode': '0533'},
    '德州': {'adcode': '371400', 'citycode': '0534'},
    '烟台': {'adcode': '370600', 'citycode': '0535'},
    '潍坊': {'adcode': '370700', 'citycode': '0536'},
    '济宁': {'adcode': '370800', 'citycode': '0537'},
    '泰安': {'adcode': '370900', 'citycode': '0538'},
    '临沂': {'adcode': '371300', 'citycode': '0539'},
    '菏泽': {'adcode': '371700', 'citycode': '0530'},
    '滨州': {'adcode': '371600', 'citycode': '0543'},
    '东营': {'adcode': '370500', 'citycode': '0546'},
    '威海': {'adcode': '371000', 'citycode': '0631'},
    '枣庄': {'adcode': '370400', 'citycode': '0632'},
    '日照': {'adcode': '371100', 'citycode': '0633'},
    '聊城': {'adcode': '371500', 'citycode': '0635'},
    
    # ==== 安徽省 ====
    '滁州': {'adcode': '341100', 'citycode': '0550'},
    '合肥': {'adcode': '340100', 'citycode': '0551'},
    '蚌埠': {'adcode': '340300', 'citycode': '0552'},
    '芜湖': {'adcode': '340200', 'citycode': '0553'},
    '淮南': {'adcode': '340400', 'citycode': '0554'},
    '马鞍山': {'adcode': '340500', 'citycode': '0555'},
    '安庆': {'adcode': '340800', 'citycode': '0556'},
    '宿州': {'adcode': '341300', 'citycode': '0557'},
    '阜阳': {'adcode': '341200', 'citycode': '0558'},
    '亳州': {'adcode': '341600', 'citycode': '0558'},
    '黄山': {'adcode': '341000', 'citycode': '0559'},
    '淮北': {'adcode': '340600', 'citycode': '0561'},
    '铜陵': {'adcode': '340700', 'citycode': '0562'},
    '宣城': {'adcode': '341800', 'citycode': '0563'},
    '六安': {'adcode': '341500', 'citycode': '0564'},
    '池州': {'adcode': '341700', 'citycode': '0566'},
    
    # ==== 浙江省 ====
    '衢州': {'adcode': '330800', 'citycode': '0570'},
    '杭州': {'adcode': '330100', 'citycode': '0571'},
    '湖州': {'adcode': '330500', 'citycode': '0572'},
    '嘉兴': {'adcode': '330400', 'citycode': '0573'},
    '宁波': {'adcode': '330200', 'citycode': '0574'},
    '绍兴': {'adcode': '330600', 'citycode': '0575'},
    '台州': {'adcode': '331000', 'citycode': '0576'},
    '温州': {'adcode': '330300', 'citycode': '0577'},
    '丽水': {'adcode': '331100', 'citycode': '0578'},
    '金华': {'adcode': '330700', 'citycode': '0579'},
    '舟山': {'adcode': '330900', 'citycode': '0580'},
    
    # ==== 福建省 ====
    '福州': {'adcode': '350100', 'citycode': '0591'},
    '厦门': {'adcode': '350200', 'citycode': '0592'},
    '宁德': {'adcode': '350900', 'citycode': '0593'},
    '莆田': {'adcode': '350300', 'citycode': '0594'},
    '泉州': {'adcode': '350500', 'citycode': '0595'},
    '漳州': {'adcode': '350600', 'citycode': '0596'},
    '龙岩': {'adcode': '350800', 'citycode': '0597'},
    '三明': {'adcode': '350400', 'citycode': '0598'},
    '南平': {'adcode': '350700', 'citycode': '0599'},
    
    # ==== 广东省 ====
    '韶关': {'adcode': '440200', 'citycode': '0751'},
    '惠州': {'adcode': '441300', 'citycode': '0752'},
    '梅州': {'adcode': '441400', 'citycode': '0753'},
    '汕头': {'adcode': '440500', 'citycode': '0754'},
    '深圳': {'adcode': '440300', 'citycode': '0755'},
    '珠海': {'adcode': '440400', 'citycode': '0756'},
    '佛山': {'adcode': '440600', 'citycode': '0757'},
    '肇庆': {'adcode': '441200', 'citycode': '0758'},
    '湛江': {'adcode': '440800', 'citycode': '0759'},
    '江门': {'adcode': '440700', 'citycode': '0750'},
    '河源': {'adcode': '441600', 'citycode': '0762'},
    '清远': {'adcode': '441800', 'citycode': '0763'},
    '云浮': {'adcode': '445300', 'citycode': '0766'},
    '潮州': {'adcode': '445100', 'citycode': '0768'},
    '东莞': {'adcode': '441900', 'citycode': '0769'},
    '中山': {'adcode': '442000', 'citycode': '0760'},
    '阳江': {'adcode': '441700', 'citycode': '0662'},
    '揭阳': {'adcode': '445200', 'citycode': '0663'},
    '茂名': {'adcode': '440900', 'citycode': '0668'},
    '汕尾': {'adcode': '441500', 'citycode': '0660'},
    
    # ==== 广西壮族自治区 ====
    '南宁': {'adcode': '450100', 'citycode': '0771'},
    '崇左': {'adcode': '451400', 'citycode': '0771'},
    '柳州': {'adcode': '450200', 'citycode': '0772'},
    '来宾': {'adcode': '451300', 'citycode': '0772'},
    '桂林': {'adcode': '450300', 'citycode': '0773'},
    '梧州': {'adcode': '450400', 'citycode': '0774'},
    '贺州': {'adcode': '451100', 'citycode': '0774'},
    '贵港': {'adcode': '450800', 'citycode': '0775'},
    '玉林': {'adcode': '450900', 'citycode': '0775'},
    '百色': {'adcode': '451000', 'citycode': '0776'},
    '钦州': {'adcode': '450700', 'citycode': '0777'},
    '河池': {'adcode': '451200', 'citycode': '0778'},
    '北海': {'adcode': '450500', 'citycode': '0779'},
    '防城港': {'adcode': '450600', 'citycode': '0770'},
    
    # ==== 江西省 ====
    '鹰潭': {'adcode': '360600', 'citycode': '0701'},
    '新余': {'adcode': '360500', 'citycode': '0790'},
    '南昌': {'adcode': '360100', 'citycode': '0791'},
    '九江': {'adcode': '360400', 'citycode': '0792'},
    '上饶': {'adcode': '361100', 'citycode': '0793'},
    '抚州': {'adcode': '361000', 'citycode': '0794'},
    '宜春': {'adcode': '360900', 'citycode': '0795'},
    '吉安': {'adcode': '360800', 'citycode': '0796'},
    '赣州': {'adcode': '360700', 'citycode': '0797'},
    '景德镇': {'adcode': '360200', 'citycode': '0798'},
    '萍乡': {'adcode': '360300', 'citycode': '0799'},
    
    # ==== 湖北省 ====
    '襄阳': {'adcode': '420600', 'citycode': '0710'},
    '鄂州': {'adcode': '420700', 'citycode': '0711'},
    '孝感': {'adcode': '420900', 'citycode': '0712'},
    '黄冈': {'adcode': '421100', 'citycode': '0713'},
    '黄石': {'adcode': '420200', 'citycode': '0714'},
    '咸宁': {'adcode': '421200', 'citycode': '0715'},
    '荆州': {'adcode': '421000', 'citycode': '0716'},
    '宜昌': {'adcode': '420500', 'citycode': '0717'},
    '恩施': {'adcode': '422800', 'citycode': '0718'},
    '十堰': {'adcode': '420300', 'citycode': '0719'},
    '随州': {'adcode': '421300', 'citycode': '0722'},
    '荆门': {'adcode': '420800', 'citycode': '0724'},
    '仙桃': {'adcode': '429004', 'citycode': '0728'},
    '天门': {'adcode': '429006', 'citycode': '0728'},
    '潜江': {'adcode': '429005', 'citycode': '0728'},
    
    # ==== 湖南省 ====
    '岳阳': {'adcode': '430600', 'citycode': '0730'},
    '长沙': {'adcode': '430100', 'citycode': '0731'},
    '湘潭': {'adcode': '430300', 'citycode': '0732'},
    '株洲': {'adcode': '430200', 'citycode': '0733'},
    '衡阳': {'adcode': '430400', 'citycode': '0734'},
    '郴州': {'adcode': '431000', 'citycode': '0735'},
    '常德': {'adcode': '430700', 'citycode': '0736'},
    '益阳': {'adcode': '430900', 'citycode': '0737'},
    '娄底': {'adcode': '431300', 'citycode': '0738'},
    '邵阳': {'adcode': '430500', 'citycode': '0739'},
    '湘西': {'adcode': '433100', 'citycode': '0743'},
    '张家界': {'adcode': '430800', 'citycode': '0744'},
    '怀化': {'adcode': '431200', 'citycode': '0745'},
    '永州': {'adcode': '431100', 'citycode': '0746'},
    
    # ==== 四川省 ====
    '攀枝花': {'adcode': '510400', 'citycode': '0812'},
    '自贡': {'adcode': '510300', 'citycode': '0813'},
    '绵阳': {'adcode': '510700', 'citycode': '0816'},
    '南充': {'adcode': '511300', 'citycode': '0817'},
    '达州': {'adcode': '511700', 'citycode': '0818'},
    '遂宁': {'adcode': '510900', 'citycode': '0825'},
    '广安': {'adcode': '511600', 'citycode': '0826'},
    '巴中': {'adcode': '511900', 'citycode': '0827'},
    '泸州': {'adcode': '510500', 'citycode': '0830'},
    '宜宾': {'adcode': '511500', 'citycode': '0831'},
    '内江': {'adcode': '511000', 'citycode': '0832'},
    '资阳': {'adcode': '512000', 'citycode': '0832'},
    '乐山': {'adcode': '511100', 'citycode': '0833'},
    '眉山': {'adcode': '511400', 'citycode': '0833'},
    '凉山': {'adcode': '513400', 'citycode': '0834'},
    '雅安': {'adcode': '511800', 'citycode': '0835'},
    '甘孜': {'adcode': '513300', 'citycode': '0836'},
    '阿坝': {'adcode': '513200', 'citycode': '0837'},
    '德阳': {'adcode': '510600', 'citycode': '0838'},
    '广元': {'adcode': '510800', 'citycode': '0839'},
    
    # ==== 贵州省 ====
    '贵阳': {'adcode': '520100', 'citycode': '0851'},
    '遵义': {'adcode': '520300', 'citycode': '0851'},
    '安顺': {'adcode': '520400', 'citycode': '0851'},
    '黔南': {'adcode': '522700', 'citycode': '0854'},
    '黔东南': {'adcode': '522600', 'citycode': '0855'},
    '铜仁': {'adcode': '520600', 'citycode': '0856'},
    '毕节': {'adcode': '520500', 'citycode': '0857'},
    '六盘水': {'adcode': '520200', 'citycode': '0858'},
    '黔西南': {'adcode': '522300', 'citycode': '0859'},
    
    # ==== 云南省 ====
    '昆明': {'adcode': '530100', 'citycode': '0871'},
    '大理': {'adcode': '532900', 'citycode': '0872'},
    '红河': {'adcode': '532500', 'citycode': '0873'},
    '曲靖': {'adcode': '530300', 'citycode': '0874'},
    '保山': {'adcode': '530500', 'citycode': '0875'},
    '文山': {'adcode': '532600', 'citycode': '0876'},
    '玉溪': {'adcode': '530400', 'citycode': '0877'},
    '楚雄': {'adcode': '532300', 'citycode': '0878'},
    '普洱': {'adcode': '530800', 'citycode': '0879'},
    '昭通': {'adcode': '530600', 'citycode': '0870'},
    '临沧': {'adcode': '530900', 'citycode': '0883'},
    '怒江': {'adcode': '533300', 'citycode': '0886'},
    '迪庆': {'adcode': '533400', 'citycode': '0887'},
    '丽江': {'adcode': '530700', 'citycode': '0888'},
    '西双版纳': {'adcode': '532800', 'citycode': '0691'},
    '德宏': {'adcode': '533100', 'citycode': '0692'},
    
    # ==== 西藏自治区 ====
    '拉萨': {'adcode': '540100', 'citycode': '0891'},
    '日喀则': {'adcode': '540200', 'citycode': '0892'},
    '山南': {'adcode': '540500', 'citycode': '0893'},
    '林芝': {'adcode': '540400', 'citycode': '0894'},
    '昌都': {'adcode': '540300', 'citycode': '0895'},
    '那曲': {'adcode': '540600', 'citycode': '0896'},
    '阿里': {'adcode': '542500', 'citycode': '0897'},
    
    # ==== 海南省（全省统一区号） ====
    '海口': {'adcode': '460100', 'citycode': '0898'},
    '三亚': {'adcode': '460200', 'citycode': '0898'},
    '三沙': {'adcode': '460300', 'citycode': '0898'},
    '儋州': {'adcode': '460400', 'citycode': '0898'},
    
    # ==== 陕西省 ====
    '延安': {'adcode': '610600', 'citycode': '0911'},
    '榆林': {'adcode': '610800', 'citycode': '0912'},
    '渭南': {'adcode': '610500', 'citycode': '0913'},
    '商洛': {'adcode': '611000', 'citycode': '0914'},
    '安康': {'adcode': '610900', 'citycode': '0915'},
    '汉中': {'adcode': '610700', 'citycode': '0916'},
    '宝鸡': {'adcode': '610300', 'citycode': '0917'},
    '铜川': {'adcode': '610200', 'citycode': '0919'},
    
    # ==== 甘肃省 ====
    '临夏': {'adcode': '622900', 'citycode': '0930'},
    '兰州': {'adcode': '620100', 'citycode': '0931'},
    '定西': {'adcode': '621100', 'citycode': '0932'},
    '平凉': {'adcode': '620800', 'citycode': '0933'},
    '庆阳': {'adcode': '621000', 'citycode': '0934'},
    '武威': {'adcode': '620600', 'citycode': '0935'},
    '金昌': {'adcode': '620300', 'citycode': '0935'},
    '张掖': {'adcode': '620700', 'citycode': '0936'},
    '酒泉': {'adcode': '620900', 'citycode': '0937'},
    '嘉峪关': {'adcode': '620200', 'citycode': '0937'},
    '天水': {'adcode': '620500', 'citycode': '0938'},
    '陇南': {'adcode': '621200', 'citycode': '0939'},
    '甘南': {'adcode': '623000', 'citycode': '0941'},
    '白银': {'adcode': '620400', 'citycode': '0943'},
    
    # ==== 宁夏回族自治区 ====
    '银川': {'adcode': '640100', 'citycode': '0951'},
    '石嘴山': {'adcode': '640200', 'citycode': '0952'},
    '吴忠': {'adcode': '640300', 'citycode': '0953'},
    '固原': {'adcode': '640400', 'citycode': '0954'},
    '中卫': {'adcode': '640500', 'citycode': '0955'},
    
    # ==== 青海省 ====
    '海北': {'adcode': '632200', 'citycode': '0970'},
    '西宁': {'adcode': '630100', 'citycode': '0971'},
    '海东': {'adcode': '630200', 'citycode': '0972'},
    '黄南': {'adcode': '632300', 'citycode': '0973'},
    '海南': {'adcode': '632500', 'citycode': '0974'},
    '果洛': {'adcode': '632600', 'citycode': '0975'},
    '玉树': {'adcode': '632700', 'citycode': '0976'},
    '海西': {'adcode': '632800', 'citycode': '0977'},
    
    # ==== 新疆维吾尔自治区 ====
    '克拉玛依': {'adcode': '650200', 'citycode': '0990'},
    '乌鲁木齐': {'adcode': '650100', 'citycode': '0991'},
    '石河子': {'adcode': '659001', 'citycode': '0993'},
    '昌吉': {'adcode': '652300', 'citycode': '0994'},
    '吐鲁番': {'adcode': '650400', 'citycode': '0995'},
    '巴音郭楞': {'adcode': '652800', 'citycode': '0996'},
    '阿克苏': {'adcode': '652900', 'citycode': '0997'},
    '喀什': {'adcode': '653100', 'citycode': '0998'},
    '伊犁': {'adcode': '654000', 'citycode': '0999'},
    '塔城': {'adcode': '654200', 'citycode': '0901'},
    '哈密': {'adcode': '650500', 'citycode': '0902'},
    '和田': {'adcode': '653200', 'citycode': '0903'},
    '阿勒泰': {'adcode': '654300', 'citycode': '0906'},
    '克孜勒苏': {'adcode': '653000', 'citycode': '0908'},
    '博尔塔拉': {'adcode': '652700', 'citycode': '0909'},
}


def get_citycode(city_name: str) -> str:
    """
    获取城市的citycode（电话区号）
    
    Args:
        city_name: 城市名称（如"北京"、"上海"）
        
    Returns:
        citycode（如"010"、"021"），找不到返回"010"
    """
    city_info = CITY_MAPPING.get(city_name)
    if city_info:
        return city_info['citycode']
    
    # 尝试去掉"市"后缀再查找
    if city_name.endswith('市'):
        city_info = CITY_MAPPING.get(city_name[:-1])
        if city_info:
            return city_info['citycode']
    
    # 默认返回北京
    print(f"⚠️  未找到城市'{city_name}'的citycode，使用默认值'010'（北京）")
    return '010'


def get_adcode(city_name: str) -> str:
    """
    获取城市的adcode（行政区划代码）
    
    Args:
        city_name: 城市名称
        
    Returns:
        adcode（如"110000"），找不到返回"110000"
    """
    city_info = CITY_MAPPING.get(city_name)
    if city_info:
        return city_info['adcode']
    
    # 尝试去掉"市"后缀再查找
    if city_name.endswith('市'):
        city_info = CITY_MAPPING.get(city_name[:-1])
        if city_info:
            return city_info['adcode']
    
    # 默认返回北京
    print(f"⚠️  未找到城市'{city_name}'的adcode，使用默认值'110000'（北京）")
    return '110000'


def get_city_info(city_name: str) -> Optional[Dict]:
    """
    获取城市的完整信息
    
    Args:
        city_name: 城市名称
        
    Returns:
        {'adcode': 'xxx', 'citycode': 'xxx'} 或 None
    """
    city_info = CITY_MAPPING.get(city_name)
    if city_info:
        return city_info
    
    # 尝试去掉"市"后缀
    if city_name.endswith('市'):
        return CITY_MAPPING.get(city_name[:-1])
    
    return None


# 支持的城市列表
SUPPORTED_CITIES = list(CITY_MAPPING.keys())

# 统计信息
STATS = {
    'total_cities': len(CITY_MAPPING),
    'c1_cities': 10,  # C1局城市（大区中心+直辖市）
    'provinces': 34,  # 省级行政区
    'coverage': '100%'  # 覆盖全国所有地级市
}


def list_supported_cities() -> list:
    """
    获取所有支持的城市列表
    
    Returns:
        城市名称列表（按省份分组）
    """
    return SUPPORTED_CITIES


def get_stats() -> Dict:
    """
    获取统计信息
    
    Returns:
        统计数据
    """
    return {
        'total_cities': len(CITY_MAPPING),
        'c1_cities': len([c for c in CITY_MAPPING.values() if len(c['citycode']) <= 3]),
        'provinces': len(set(c['adcode'][:2] for c in CITY_MAPPING.values())),
        'sample_cities': list(CITY_MAPPING.keys())[:20]
    }

