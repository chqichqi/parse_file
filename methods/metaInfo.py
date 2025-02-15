'''
小包序号:type=9
时长:type=10
导联状态:type=11
时间戳:type=13
佩戴状态:type=17
* ST 特征点位置 V1:type=23
    type
    version
    meta length
    data offset
    data length
    dataBits
    采样率
    放大倍数
    通道数
    导联顺序

导联序号
有些Meta中包含多个导联的顺序信息，所以要为12个导联编号，统一定义如下：
导联名称         导联编号            示例
I               0x12        const val CHANNEL_I: Byte = 0x12.toByte()
II              0x32        const val CHANNEL_II: Byte = 0x32.toByte()
III             0x31        const val CHANNEL_III: Byte = 0x31.toByte()
V1              0x50        const val CHANNEL_V1: Byte = 0x50.toByte()
V2              0x60        const val CHANNEL_V2: Byte = 0x60.toByte()
V3              0x70        const val CHANNEL_V3: Byte = 0x70.toByte()
V4              0x80        const val CHANNEL_V4: Byte = 0x80.toByte()
V5              0x90        const val CHANNEL_V5: Byte = 0x90.toByte()
V6              0xA0        const val CHANNEL_V6: Byte = 0xA0.toByte()
aVR             0xAA        const val CHANNEL_AVR: Byte = 0xAA.toByte()
aVL             0xAB        const val CHANNEL_AVL: Byte = 0xAB.toByte()
aVF             0xAC        const val CHANNEL_AVF: Byte = 0xAC.toByte()

PD量程&DAC偏置
编号    组合PD量程    组合DAC偏置     备注
0         4uA          0uA
1         4uA          8uA
2         4uA          16uA
3         4uA          24uA
4         8uA          0uA
5         8uA          8uA
6         8uA          16uA
7         8uA          24uA
8         16uA         0uA
9         16uA         8uA
10        16uA         16uA
11        16uA         24uA
12        32uA         0uA
13        32uA         8uA
14        32uA         16uA
15        32uA         24uA

电流范围
电流范围设置为四档，（0~3）。每档的范围值在不同设备上有不同的定义，需要通过配置文件来指定。
编号         范围值           备注
0           0~32mA
1           0~64mA
2           0~96mA
3           0~128mA


BHR V0:type=8;length=10(不包含 type, version 和 meta length 在内)  采样率:4字节
BHR V1:type=8;length=10(不包含 type, version 和 meta length 在内)  采样率:4字节
EHR V0:type=12;length=10(不包含 type, version 和 meta length 在内)  采样率:4字节
EHR V1:type=12;length=10(不包含 type, version 和 meta length 在内)  采样率:4字节

呼吸率（呼吸算法的结果）:type=27;length=14(不包含 type, version 和 meta length 在内) 采样率:4,初始结果毫秒数:2,之后每次计算毫秒数:2bytes
呼吸滤波 V1:type=26; length=10 采样率:4字节
呼吸阻抗 V1:type=20;  length=10; 采样率:4字节

PPG红光：type=3; length=13 采样率:4;电流:1;放大倍数:2bytes

PPG绿光V0:type=2; length=13 采样率:4;电流:1;放大倍数:2bytes
PPG绿光V1:type=2; length=13  采样率:4;PD量程&DAC偏置设置:1;电流范围设置:1;电流步进设置:1bytes

ECG V0:type=1; length=25 采样率：4；放大倍数：2；通道数：1；导联顺序：12bytes
ECG V1:type=1; length=13 采样率：4；放大倍数：2；导联序号：1bytes

ppg-HR结果文件:type=25;length=14(不包含 type, version 和 meta length 在内);firstSegPoints:4, seqSegPoints:4bytes
GRN:type=15;length=10  采样率：4bytes

ST 滤波文件 V1:type=24;length=29 采样率：4；放大倍数：2；通道数：1；导联顺序：12bytes
多导联ECG V0：type=29; length=25 采样率：4；放大倍数：2；通道数：1；导联顺序：12bytes
多导联ECG滤波后数据:type=30;length=25 采样率：4；放大倍数：2；通道数：1；导联顺序：12bytes

ECG滤波后数据 V0:type=16;length=25 采样率：4；放大倍数：2；通道数：1；导联顺序：12bytes
ECG滤波后数据 V1:type=16;length=13 采样率：4；放大倍数：2；导联序号：1bytes

气压:type=28; length=10 采样率：4bytes
计步数据:type=7; length=7 Step type：1bytes(0---总步数 1---步数增量)
地磁:type=6; length=10 采样率：4bytes
角速度:type=5; length=10 采样率：4bytes
加速度:type=4; length=10 采样率：4bytes

版本信息：type=19; length=149, text: 141bytes
标记类型：type=18; length=7; triggerType: 1Bytes

'''
meta_info_item_dic = {}
ext_meta_info_dic = {}

base_meta_info_dic = {
    'type': 2,
    'version': 2,
    'meta length': 2,
    'data offset': 2,
    'data length': 2,
    'dataBits': 2,
}

small_data_dic = {
    'ecg': {},
    'ppg绿光': {},
    'ppg红光': {},
    '加速度': {},
    '角速度': {},
    '地磁': {},
    '计步数据': {},
    'bhr': {0: {'R间期': 2, '波形质量&房颤标识': 1, '全局序号': 4},
            1: {'R间期': 2, '波形质量&房颤标识': 1, '全局序号': 4, 'af置信度': 1}},
    '小包序号': {},
    '时长': {},
    '导联状态': {},
    'ehr': {0: {'有效段标志': 1, 'R位置': 4, '心拍相关疾病': 1, '节律相关疾病': 1},
            1: {'有效段标志': 1, 'R位置': 4, '心拍相关疾病': 1, '节律相关疾病': 1, 'r置信度': 1, 'af置信度': 1, 'pvc置信度': 1}},
    '时间戳': {},
    'grn': {},
    'ecg滤波后数据': {},
    '佩戴状态': {},
    '标记类型': {},
    '版本信息': {},
    '呼吸阻抗': {},
    'st 特征点位置': {},
    'st 滤波文件': {},
    'ppg-hr结果文件': {},
    '呼吸滤波': {},
    '呼吸率（呼吸算法的结果）': {},
    '气压': {},
    '多导联ecg': {},
    '多导联ecg滤波后数据': {},
    'anystrmetainfo': {},
    '多导联ehr': {0: {'有效段标志': 1, 'R位置': 4, '心拍相关疾病': 1, '节律相关疾病': 1},
               1: {'有效段标志': 1, 'R位置': 4, '心拍相关疾病': 1, '节律相关疾病': 1, '通道数': 1, 'r置信度': 1, 'af置信度': 1, 'pvc置信度': 1},
               2: {'有效段标志': 1, 'R位置': 4, '心拍相关疾病': 1, '节律相关疾病': 1, 'r置信度': 1, 'af置信度': 1, 'pvc置信度': 1, '通道数': 1}}
}


file_Protocol_dic = {
    'old': {
        'enc_loc':[107, 1],
        'file_end_loc':[110, 4],
        'user_id_loc':[10, 32],
        'device_num_loc':[42, 13],
    },
    'new': {
        'enc_loc':[74, 1],
        'user_id_loc':[10, 32],
        'device_num_loc':[42, 13],
        'file_b_time_loc':[55, 8],
        'file_e_time_loc':[63, 8],
        'meta_info_loc':[78, 2],
    },
}

BeatsDisType = {
	'N': '正常',
	'V': 'PVC',
	'/': '起搏心拍',
	'F': '融合波',
	'L': '左束支',
	'R': '右束支',
	'!': '心室扑动波',
	'Q': '未标注',
    'A': '房早',
    'r': 'RonT室早',
}

RhythmDisType = {
	0: "(N--正常",
	1: "(AFIB--房颤",
	2: "(VT--室速",
	3: "(SVT--短阵室速",
	4: "(B--二联律",
	5: "(T--三联律",
	6: "(VSI--极短联律间期",
	7: "(Q--未标注",
	8: "(SVTA--室上性心动过速开始",
    9: "(AFL--房扑开始",
    10: "(AT--房性心动过速",
    11: "(BII--2度心脏阻滞开始",
    12:  "(BIII--3度心脏阻滞开始",
}

# 统计参数设置变量
setting_item_dic = {}
# 解析进度条
progress_val = 0
# 统计信息
sum_info_list = []
# 解析异常
err_info_list = []
# PPG固定采样率
PPG_FFS = 25.6
# 支持的文件类型
file_types_dic = {}
# 支持的设备类型
device_type_dic = {}