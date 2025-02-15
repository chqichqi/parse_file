
class Channels_Data:
    CHANNELS_NUM = 10
    channel_dic = {
        0x12: 'Ⅰ',
        0x32: 'Ⅱ',
        0x31: 'Ⅲ',
        0x50: 'V1',
        0x60: 'V2',
        0x70: 'V3',
        0x80: 'V4',
        0x90: 'V5',
        0xAA: 'aVR',
        0xAB: 'aVL',
        0xAC: 'aVF',
    }

    channel_to_num_dic = {
        0x12: '0',
        0x32: '1',
        0x31: '2',
        0x50: '3',
        0x60: '4',
        0x70: '5',
        0x80: '6',
        0x90: '7',
        0xAA: '8',
        0xAB: '9',
        0xAC: '10',
    }

    # 此变量是为了与算法本地跑的多通道ehr文件中最后一个通道数据进行匹配而添加的 20241120
    channel2_to_num_dic = {
        0x12: '1',
        0x32: '2',
        0x31: '3',
        # 0x50: '4',
        0x60: '4',
        0x70: '5',
        0x80: '6',
        0x90: '7',
        # 0xA0: '8',
        0xAA: '8',
        0xAB: '9',
        0xAC: '10',
    }

    rhythm_dic = {
        0: "(N",
        1: "(AFIB",
        2: "(VT",
        3: "(SVT",
        4:"(B",
        5:"(T",
        6:"(VSI",
        7:"(Q",
        8:"(SVTA",
        9:"(AFL",
        10:"(AT",
        11:"(BII",
        12:"(BIII"
    }

    d1, d2, d3, d4, d5, d6, d7, d8, d9, d10, d11 = [[] for i in range(11)]
    channels_data_dic = {
        0: d1,
        1: d2,
        2: d3,
        3: d4,
        4: d5,
        5: d6,
        6: d7,
        7: d8,
        8: d9,
        9: d10,
        10: d11,
    }
