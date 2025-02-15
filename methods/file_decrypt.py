"""
@Author: chenqiang
@Date: 2023/6/13
@Desc: xinjikang encrypt File to Decrypt Dll call
"""
import os
from ctypes import cdll, c_char_p, c_int, c_char
from methods.tools import *


class File_decrypt(object):
    # 文件解密预留16字节供JNI空间使用
    DECRYPT_RESERVED = 16

    def __init__(self, dll_name, dll_path):
        # os.chdir(folder)
        folder = format_file_path(dll_path)
        self.dll = cdll.LoadLibrary(folder + dll_name)
        logging.info("decrypt dll version:" + str(self.get_dll_ver()))
        self.pack_list = []
        self.pack_info = {"pack_head": "",
                          "pack_data_len": 0,
                          "pack_data": ""
                          }

    def get_dll_ver(self):
        '''
        获取DLL版本
        :return:
        '''
        return self.dll.GetVer_c()

    def decrypt_pack_data(self, pack_data, idx):
        '''
        按大包数据进行解密
        :param pack_data:
        :return:
        '''
        logging.info(f"大包{idx}数据解密中...")
        mode = 1  # 1大包数据, 2全文件数据
        key = ""
        decrypt2 = 0
        lastPacket = 1
        packLength = len(pack_data)
        # 预留16个字节
        tmp = bytearray(self.DECRYPT_RESERVED)
        arr_data = bytearray(pack_data) + tmp
        c_char_array_type = c_char * len(arr_data)
        cc_array_data = c_char_array_type(*arr_data)
        ci_mode = (c_int)(mode)
        ci_packLen = (c_int)(packLength)
        cc_key = (c_char_p)(key.encode('utf-8'))
        ci_decrypt2 = (c_int)(decrypt2)
        ci_lastPacket = (c_int)(lastPacket)
        self.dll.XJK_Decrypt_c.argtypes = [c_int,
                                           c_char_array_type,
                                           c_int,
                                           c_char_p,
                                           c_int,
                                           c_int]
        self.dll.XJK_Decrypt_c.restypes = [c_int]
        result = self.dll.XJK_Decrypt_c(ci_mode,
                                        cc_array_data,
                                        ci_packLen,
                                        cc_key,
                                        ci_decrypt2,
                                        ci_lastPacket)
        logging.info(f'大包{idx}数据解密结束！其解密后包数据长度:{result}')
        return (bytearray(cc_array_data)[0:result])

    def save_decrypt_data_to_file(self, file_all_data, pack_info, path, type='old', mate_len=0):
        '''
        保存解密后的数据，并生成新的文件
        :param file_all_data:
        :param pack_info:
        :param path:
        :param save_file_name_prefix:
        :return:
        '''
        try:
            new_file = make_new_file_data(file_all_data, pack_info, type, mate_len)
            # 将文件路径中的文件夹目录和文件名取出来
            (file_path, file_name) = os.path.split(path)
            new_file_path = format_file_path(file_path)

            # 先修改原文件名,在后面加”_old“，前提是原文件名中不包含”_old"后缀
            if not str(file_name).__contains__('_old'):
                if not os.path.exists(new_file_path+file_name + '_old'):
                    os.rename(new_file_path+file_name, new_file_path+file_name + '_old')
            else:  # 如果包含，则新保存的文件名则要支掉“_old”后缀
                file_name = str(file_name).replace('_old', '')

            new_path_and_file = new_file_path + file_name
            with open(new_path_and_file, 'wb') as f:
                f.write(new_file)
                f.close()
            messagebox.showinfo('消息提示', f'保存解密后的文件[{new_path_and_file}]成功...')
            logging.info(f'保存解密后的文件[{new_path_and_file}]成功...')
            return True
        except Exception as e:
            logging.error(f"保存解密后的文件异常，原因为{e}...")
            return False

    def update_pack_info(self, decrypt_pack_data, pack_info):
        '''
        更新包数据为未加密数据
        :param decrypt_pack_data:
        :param pack_info:
        :return:
        '''
        try:
            # logging.info('缓存解密后的包数据...')
            pack_data_len = len(decrypt_pack_data)
            pack_info['pack_data_len'] = pack_data_len
            # 修改包头中的加密数据长度
            tmp = (pack_data_len).to_bytes(4, byteorder='big')
            pack_info['pack_head'] = pack_info['pack_head'][0: 16] + tmp
            pack_info['pack_data'] = bytes(bytearray(decrypt_pack_data)[0: pack_data_len])
        except Exception as e:
            logging.error("更新包数据异常..." + str(e))

    def decrypt_file_dir(self, file_path, save_file_name_prefix='py_'):
        '''
        按文件夹解密，其参数1为需要解密的文件路径，参数2表示：指定要保存解密后的文件名前缀（默认"py_"开头为前缀），想替换原文件传""即可
        :param file_path:
        :param save_file_name_prefix:
        :return:
        '''
        # 如果路径最后一个字符不是"/"或”\\"，就自动补全"/"或”\\"
        file_path2 = format_file_path(file_path)
        # 读取指定file_path路径下所有文件（包括子目录中的文件）
        encrypt_file_list = get_file_list(file_path2)
        ''' 
        encrypt_file_list列表数据格式如下：
        <class 'list'>: ['./xjk_file/', ['xjk_file2'], ['20230615184339.jkwbhr', '20230615184659.jkwbhr']]
        <class 'list'>: ['./xjk_file/xjk_file2', [], ['20230615023835.jkwppg', '20230615184339.jkwbhr']]
        列表元素[0]为当前文件目录，[1]为子文件目录，[2]当前文件目录下的所有文件列表
        '''
        if len(encrypt_file_list) == 0:
            logging.info("文件夹下没有任何文件或文件夹不存在...")
        else:
            for item in encrypt_file_list:
                tmp_path = item[0]
                # 如果路径最后一个字符不是"/"或”\\"，就自动补全"/"或”\\"
                new_path = format_file_path(tmp_path)
                logging.info("目录[" + tmp_path + "]下需要解密的文件列表:" + str(item[2]) + "...")
                for file_name in item[2]:
                    self.decrypt_one_file(new_path + file_name, save_file_name_prefix)
            return True

    def decrypt_one_file(self, file_name, save_file_name_prefix="py_"):
        '''
        按指定的文件进行解密
        :param file_name: 应包括目录路径
        :param save_file_name_prefix:
        :return:
        '''
        file_all_data = get_file_data(file_name)
        if (file_all_data != None):
            enc_flg = get_assign_data(file_all_data, 107, 108)
            if (enc_flg == None):
                logging.error("文件[" + file_name + "]数据存在非法...")
            elif (enc_flg == 0):
                logging.error("文件[" + file_name + "]未加密...")
                return None
            else:
                pack_loc_list = get_file_packLoc(file_all_data)
                if (len(pack_loc_list) > 0):
                    logging.info('当前解密[' + file_name + ']文件...')
                    i = 1
                    for loc in pack_loc_list:
                        pack_data = get_pack_data(file_all_data, loc, self.pack_info)
                        pack_decrypt_data = self.decrypt_pack_data(pack_data, i)
                        self.update_pack_info(pack_decrypt_data, self.pack_info)
                        self.pack_list.append(self.pack_info.copy())
                        i += 1
                    # 保存解密后的数据
                    self.save_decrypt_data_to_file(file_all_data,
                                                   self.pack_list,
                                                   file_name, save_file_name_prefix
                                                   )
                    # 清空已保存的解密文件包数据
                    self.pack_list.clear()
                    return True
                else:
                    logging.error("获取文件[" + file_name + "]包位置列表数据异常...")
                    return False
        else:
            logging.error("文件[" + file_name + "]中没有任何数据...")
            return False

    def decrypt_new_protocol_file(self, file_data, ty):
        try:
            mateInfo_loc_s, mateInfo_loc_e = get_data_loc('meta_info_loc', ty)
            mateInfo_length = hexToInt(bytesToHexString(file_data[mateInfo_loc_s:mateInfo_loc_e]))
            data_length = hexToInt(bytesToHexString(file_data[mateInfo_length + 80:mateInfo_length + 84]))
            all_pack_data = file_data[mateInfo_length + 84:mateInfo_length + 84 + data_length]
            index = 0
            pack_data_list = []
            idx = 1
            while data_length > 0:
                pack_info = {}
                # 解析包头信息:20bytes, 其中数据长度，取加密数据长度，不能取原始数据长度
                packData_len = hexToInt(bytesToHexString(all_pack_data[index + 16:index + 20]))
                pack_info['pack_head'] = all_pack_data[index:index + 20]
                index += 20
                data_length -= 20
                # 获得包体数据
                enc_pack_data = all_pack_data[index:index + packData_len]
                # 解密包数据
                decrypt_pack_data = self.decrypt_pack_data(enc_pack_data, idx)
                self.update_pack_info(decrypt_pack_data, pack_info)
                pack_data_list.append(pack_info.copy())
                pack_info.clear()
                index += packData_len
                data_length -= packData_len
                idx += 1
            logging.info('文件解密完成...')
            return pack_data_list, mateInfo_length
        except Exception as e:
            logging.error(f'文件解密出错啦！原因为{e}...')

    def encrypt_file_dir(self, file_path, save_file_name_prefix='py_'):
        '''
        按文件夹进行文件加密，暂未实现相关功能
        :param file_path:
        :param save_file_name_prefix:
        :return:
        '''
        logging.info('加密文件功能暂未实现...')
        pass


if __name__ == '__main__':
    folder = os.path.split(os.path.abspath(__file__))[0]
    dll_name = 'DataEncryptorDll.dll'
    dll_obj = File_decrypt(dll_name, folder)
    # 文件路径中是"\",应在前面加r（避免被转义）或者使用'\\'或'/'
    # 按文件夹进行解密文件,当前路径为"./"，默认保存解密之后的新文件名以'py_'前缀开头
    # dll_obj.decrypt_file_dir(r'E:\ppgfile', 'new_')
    # 按文件名进行单个文件解密
    dll_obj.decrypt_one_file(r"e:\ppg\20220829090401.jkwbhrex", 'new_dl_')
