import threading
from threading import Thread
from tkinter import *
import tkinter as tk
# from ttkbootstrap import RIGHT, X, Y, HORIZONTAL, BOTTOM, Style
from tkinter.font import Font
from methods import tool_tip
from methods.tools import *
import os
from methods.file_decrypt import File_decrypt
import csv
from tkinter import ttk, filedialog
import logging
from configparser import ConfigParser
# import win32gui, win32con


def create_dialog_obj(width, height, title):
    dlg_obj = tk.Toplevel(window)
    dlg_obj.geometry(
        '%dx%d+%d+%d' % (width, height, int((s_width - width) / 2), int((s_height - height) / 2)))
    dlg_obj.title(title)
    return dlg_obj

def set_dialog_style(obj, parent_obj):
    # obj.overrideredirect(True)  # 隐藏窗体的标题栏，但会使整个窗口不可见
    # obj.wm_state('normal')      # 设置窗口状态为正常，即可见状态（但实际无效）
    obj.resizable(0, 0)  # 隐藏最小、最大化
    obj.transient(parent_obj)  # 设置为root的transient窗口，即模态窗口
    obj.grab_set()  # 设置为模态, 使其在不响应就无法结束该窗口


def validate_file(obj, file, txt='解析', ty='文件', file_type=None, file_type_list=None):
    if file == '':
        err = f'需要{txt}的{ty}不能为空，请重新输入或选择...'
        show_message(obj, '错误提示', err, 'err')
        return False
    elif not os.path.exists(file):
        err = f'目录或文件【{file}】不存在，请重新输入或选择...'
        show_message(obj, '错误提示', err, 'err')
        return False
    elif not(file_type_list is None and file_type is None):
        if len(file_type) == 0:
            msg = f'路径中未包含任何文件，请重新输入或选择...'
            show_message(obj, '错误提示', msg, 'err')
            return False
        elif not(file_type in file_type_list):
            msg = f'不支持的文件类型【.{file_type}】，'
            flg = True
            tmp = list(device_type_dic.values())
            tmp_list = tmp[0].split(',')
            for item in tmp_list:
                data_prefix = str(item).split('--')[1]
                if data_prefix in file_type:
                    tmp = file_type[0:3]
                    if tmp == data_prefix:
                        msg += '可以通过"首选项->文件类型配置"中添加该项后重试...'
                        flg = False
                        break
            if flg:
                msg += '请重新输入或选择...'
            show_message(obj, '错误提示', msg, 'err')
            return False
    return True

# 注册页面
def register_page():
    def do_register():
        register_username = dlg_entry_username.get()
        register_password = dlg_entry_password.get()
        # 验证数据是否合法
        if len(register_username) == 0 or len(register_password) == 0:
            err = '注册用户名或密码不能为空！'
            show_message(dialog, '错误提示', err, 'err')
        else:
            msg = '注册成功...'
            show_message(dialog, '消息提示', msg, 'info')
            dialog.destroy()

    dialog = create_dialog_obj(width, height, '用户注册')
    dlg_label_username = ttk.Label(dialog, text='用户名：')
    dlg_entry_username = ttk.Entry(dialog)
    dlg_label_password = ttk.Label(dialog, text=' 密 码 ：')
    dlg_entry_password = ttk.Entry(dialog, show='*')
    dlg_label_username.place(x=10, y=20, width=l_width, height=l_height)
    location = dlg_label_username.place_info()
    dlg_entry_username.place(x=int(location['width']), y=int(location["y"]))
    dlg_entry_username.focus()
    dlg_label_password.place(x=10, y=int(location['height']) + 20, width=l_width, height=l_height)
    dlg_entry_password.place(x=int(location['width']), y=int(location['y']) + int(location['height']))

    location = dlg_entry_password.place_info()
    dlg_btn_login = ttk.Button(dialog, text='注册', command=do_register, style='primary.TButton')
    dlg_btn_login.place(x=int(location['x']) + 100, y=int(location['height']) * 2.8, width=80)
    set_dialog_style(dialog, window)

def option_file():
    # path_ = filedialog.askopenfilenames(filetypes=(tuple(file_types_dic.items())))
    path_ = filedialog.askopenfilenames()
    if len(path_) == 0:  # 弹窗后点击了取消操作
        path_ = file_name.get()
    path.set(path_)

def parse_file():
    logging.info('解析数据开始...')
    file_name1 = disp_file_path(file_name)
    file_type = get_file_type(file_name1)
    if validate_file(window, file_name1, txt='解析', file_type=file_type, file_type_list=all_file_types):
        global pack_data_list
        global progress_val
        # 全局的变量，一定要记得清除上次使用之后的数据，否则可能会出现下次再使用时出现上次的数据
        if not(pack_data_list is None):
            pack_data_list.clear()
        if not(sum_info_list is None):
            sum_info_list.clear()
        if not(err_info_list is None):
            err_info_list.clear()
        progress_val += 5
        update_progress(progress_val)
        # 打开文件
        file_data = get_file_data(file_name1)
        if not (file_data is None):
            err = ''
            head_data_list = None
            metaInfo_length = 0
            meta_info_list = None
            pack_data_list = None
            if int(file_data[0]) < 10: # 旧协议
                err = '旧文件协议，暂不支持...'
                show_message(window, '消息提示', err, 'info')
                err_info_list.append(err)
            else:   # 新协议
                progress_val += 5
                update_progress(progress_val)
                head_data_list, encrypt_type, magicCode = parse_NewProtocol_head(file_data)
                if not (head_data_list is None):
                    metaInfo_length = hexToInt(bytesToHexString(file_data[78:80]))
                    meta_info_list, \
                    metaInfo_item_list, \
                    metaExtInfo_list = parse_MetaInfo(file_data[78:metaInfo_length + 80], magicCode)
                    if not (meta_info_list is None):
                        if encrypt_type != 0:  # 文件已加密，需解密后才能做后续解析
                            logging.info('文件已加密，开始解密数据...')
                            decrypt_pack_data_list, mateInfo_lenght = dll_obj.decrypt_new_protocol_file(file_data, 'new')
                            pack_data = bytearray()
                            for item in decrypt_pack_data_list:
                                pack_data += item['pack_head']
                                pack_data += item['pack_data']
                            data_length = len(pack_data)   # 数据长度，需要使用解密后的数据长度
                        else:  # 非加密文件
                            progress_val += 5
                            update_progress(progress_val)
                            data_length = hexToInt(bytesToHexString(file_data[metaInfo_length+80:metaInfo_length+84]))
                            pack_data = file_data[metaInfo_length+84:metaInfo_length+84+data_length]
                        pack_data_list = parse_PackData(pack_data, data_length, metaInfo_item_list, metaExtInfo_list)
                        if not (pack_data_list is None):
                            progress_val += 10
                            update_progress(progress_val)
                        else:
                            err = '解析包数据出错啦，即文件存在错误...'
                            show_message(window, '错误提示', err, 'err')
                    else:
                        err = '解析MetaInfo信息出错啦，即文件存在错误...'
                        show_message(window, '错误提示', err, 'err')
                else:
                    err = '解析文件头出错啦，即文件存在错误...'
                    show_message(window, '错误提示', err, 'err')
                if len(err) > 0 and not err in err_info_list:
                    err_info_list.append(err)
            fill_data_to_tree(head_data_list, metaInfo_length, meta_info_list, pack_data_list, sum_info_list,
                              err_info_list)


# 添加处理进度展示
def update_progress(v):
    if (v + 1) > 99:
        global progress_val
        progress_val = 1
        progress_bar['value'] = 1
    else:
        progress_bar['value'] = v + 1
    progress_window.update_idletasks()
    window.update()  # 确保窗口更新

def start_parse_file():
    global progress_bar
    global progress_val
    global progress_window
    progress_val = 1
    # 拦截关闭窗口操作，使窗口重新出现
    def close_window():
        progress_window.deiconify()

    try:
        progress_window = tk.Toplevel(window)
        progress_window.title('解析中，请等待...')
        center_window(progress_window, 300, 40)
        progress_bar = ttk.Progressbar(progress_window, length=300, mode='determinate')
        progress_bar.pack(pady=10)
        progress_bar['value'] = 0
        set_dialog_style(progress_window, window)
        # 拦截标题栏关闭按钮事件
        progress_window.protocol("WM_DELETE_WINDOW", close_window)
        parse_file()
        progress_bar.stop()
        progress_window.destroy()
    except Exception as e:
        progress_window.destroy()
        logging.error(f'出错啦，原因为：{e}')

def center_window(root, width, height):
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width / 2) - (width / 2)
    y = (screen_height / 2) - (height / 2)
    root.geometry('{}x{}+{}+{}'.format(width, height, int(x), int(y)))

# 展开全部treeView控件所有节点的功能
def open_treeView_node(obj, bFlg):
    for item in obj.get_children():
        obj.item(item, open=bFlg)
        window.update()

def decrypt_file_dlg():
    global decrypt_dialog
    def decrypt_file():
        enc_file_name = disp_file_path(dlg_file_name)
        file_type = get_file_type(enc_file_name)
        # 验证数据是否合法
        if validate_file(decrypt_dialog, enc_file_name, txt='解密', file_type=file_type, file_type_list=all_file_types):
            file_data = get_file_data(enc_file_name)
            if file_data is not None:
                encrypt_flg, ty = validate_fileIsEncrypt(file_data)
                if encrypt_flg != 0:  # 已加密
                    if ty == 'old':
                        dll_obj.decrypt_one_file(enc_file_name, 'new_')
                    elif ty == 'new':
                        logging.info(f'文件{enc_file_name}已加密，正在解密文件...')
                        pack_data_list, mateInfo_length = dll_obj.decrypt_new_protocol_file(file_data, ty)
                        logging.info(f'文件{enc_file_name}解密结束...')
                        # 保存解密后的数据
                        dll_obj.save_decrypt_data_to_file(file_data,
                                                          pack_data_list,
                                                          enc_file_name,
                                                          'new',
                                                          mateInfo_length)
                else:
                    err = f'文件{enc_file_name}文件未加密，不需要解密...'
                    show_message(decrypt_dialog, '错误提示', err, 'err')

    if decrypt_dialog is None or not (decrypt_dialog.winfo_exists()):
        decrypt_dialog = create_dialog_obj(600, 200, '文件解密')
        dlg_select_file = ttk.Label(decrypt_dialog, text='选择文件：')
        dlg_file_name = ttk.Entry(decrypt_dialog, textvariable=path)
        dlg_file_name.focus()
        dlg_select_file.place(x=10, y=5, width=70, height=35)
        location = dlg_select_file.place_info()
        dlg_file_name.place(x=int(location['width']), y=int(location["y"])+5, width=430)
        dlg_btn_select = ttk.Button(decrypt_dialog, text='选择', command=option_file, style='primary.TButton')
        dlg_file_name_location = dlg_file_name.place_info()
        dlg_btn_select.place(x=int(dlg_file_name_location['width']) + int(location['width']) + 7,
                         y=int(dlg_file_name_location["y"])-2)
        dlg_btn_decrypt = ttk.Button(decrypt_dialog, text='点击解密', command=decrypt_file, style='primary.TButton')
        dlg_btn_decrypt.place(x=int(600 / 2) - 70, y=int(location['height']) * 1.4, width=150, height=35)
        location = dlg_btn_decrypt.place_info()
        dlg_lable_tip = ttk.Label(decrypt_dialog, text=' 命名规则：',font=("微软雅黑", 11))
        dlg_lable_tip.place(x=10, y=int(location['y'])+50)
        dlg_lable_tip2 = ttk.Label(decrypt_dialog,
                                  text='        解密新文件将按原文件名保存，加密文件按原文件名+[_old]进行重命名...',
                                  font=("微软雅黑", 10))
        location = dlg_lable_tip.place_info()
        dlg_lable_tip2.place(x=10, y=int(location['y']) + 23)
        set_dialog_style(decrypt_dialog, window)


def validate_item(obj, id, num, time):
    if len(id)==0 and len(num)==0 and len(time)==0:
        err = '用户ID、设备编号、修改时间等三项不能均为空，请至少填写一项方能修改...'
        show_message(obj, '错误提示', err, 'err')
        return False
    if len(id)>0 and len(id)!=32:
        err = '用户ID长度不正确...'
        show_message(obj, '错误提示', err, 'err')
        return False
    if len(num)>0 and len(num)!=13:
        err = '设备编号长度不正确...'
        show_message(obj, '错误提示', err, 'err')
        return False
    if len(time)>0:
        if len(time)!=14:
            err = '时间长度不正确...'
            show_message(obj, '错误提示', err, 'err')
            return False
        if not str(time).isdigit():
            err = '时间数据存在非法，只能是数字...'
            show_message(obj, '错误提示', err, 'err')
            return False
        if not is_valid_date(time[0:8]):
            err = '修改数据中的日期存在非法，请检查...'
            show_message(obj, '错误提示', err, 'err')
            return False
        if not is_valid_time(time[8:]):
            err = '修改数据中的时间存在非法，请检查...'
            show_message(obj, '错误提示', err, 'err')
            return False
    return True


def modify_fileData_dlg():
    global modify_dlg
    def one_file_modify_data():
        file_name = disp_file_path(e_file_name)
        file_type = get_file_type(file_name)
        if validate_file(modify_dlg, file_name, txt='修改', file_type=file_type, file_type_list=all_file_types):
            user_id = str(e_user_id.get()).replace('\n', '')
            device_number = str(e_device_number.get()).replace('\n', '')
            file_time = str(e_file_time.get()).replace('\n', '')
            if validate_item(modify_dlg, user_id, device_number, file_time):
                file_name_list = [file_name]
                make_modify_data(modify_dlg,
                                 file_name_list,
                                 user_id,
                                 device_number,
                                 file_time,
                                 'one',
                                 dll_obj)


    def all_file_modify_data():
        file_name = disp_file_path(e_file_name)
        # 验证数据是否合法
        if validate_file(modify_dlg, file_name, txt='修改', ty='目录'):
            # 将从其他软件中复制过来的数据，包含看不见的'\n'时，直接替换为''后再处理 2024-12-11
            user_id = str(e_user_id.get()).replace('\n','')
            device_number = str(e_device_number.get()).replace('\n','')
            file_time = str(e_file_time.get()).replace('\n','')
            if validate_item(modify_dlg, user_id, device_number, file_time):
                (file_path, file_name) = os.path.split(file_name)
                temp_file_name_list = get_file_list(file_path)
                file_name_list = []
                for item in temp_file_name_list[0][2]:  # file_name_list1下面0个元素下的第二个元素才是文件名列表
                    file_type = get_file_type(item)
                    if file_type in all_file_types:
                        file_name_list.append(file_path+'/'+item)
                # 修改数据
                make_modify_data(modify_dlg,
                                 file_name_list,
                                 user_id,
                                 device_number,
                                 file_time,
                                 'all',
                                 dll_obj)
                msg = f'批量修改文件数据成功，所有新文件均按重命名规则进行重命名并保存完成...'
                show_message(modify_dlg, '消息提示', msg, 'info')


    if modify_dlg is None or not (modify_dlg.winfo_exists()):
        modify_dlg = create_dialog_obj(695, 380, '修改文件数据')
        l_select_file = ttk.Label(modify_dlg, text='选择文件：')
        l_select_file.place(x=10, y=4, width=70, height=35)
        e_file_name = ttk.Entry(modify_dlg, textvariable=path)
        e_file_name.focus()
        location = l_select_file.place_info()
        e_file_name.place(x=int(location['width']), y=int(location["y"])+7, width=535)
        l_btn_select = ttk.Button(modify_dlg, text=' 选择 ', command=option_file, style='primary.TButton')
        l_file_name_location = e_file_name.place_info()
        l_btn_select.place(x=int(l_file_name_location['width']) + int(location['width']) + 7,
                             y=int(l_file_name_location["y"])-2, width=75)
        l_user_id = ttk.Label(modify_dlg, text='用 户 ID：')
        e_user_id = ttk.Entry(modify_dlg)
        l_user_id_tip = ttk.Label(modify_dlg, text='长度：32位字符，非必填项；但另外两项未填则为必填项；')
        l_user_id.place(x=10, y=int(location["y"])+45, width=70, height=35)
        location = l_user_id.place_info()
        e_user_id.place(x=int(location['width']), y=int(location["y"])+5, width=300)
        location = e_user_id.place_info()
        l_user_id_tip.place(x=int(location['width'])+int(location['x'])+5, y=int(location["y"]))
        location = l_user_id.place_info()
        l_device_number = ttk.Label(modify_dlg, text='设备编号：')
        e_device_number = ttk.Entry(modify_dlg)
        l_device_number_tip = ttk.Label(modify_dlg, text='长度：13位字符，非必填项；但另外两项未填则为必填项；')
        l_device_number.place(x=10, y=int(location["y"])+45, width=70, height=35)
        location = l_device_number.place_info()
        e_device_number.place(x=int(location['width']), y=int(location["y"])+5, width=300)
        location = e_device_number.place_info()
        l_device_number_tip.place(x=int(location['width']) + int(location['x']) + 5, y=int(location["y"]))
        location = l_device_number.place_info()
        l_file_time = ttk.Label(modify_dlg, text='开始时间：')
        e_file_time = ttk.Entry(modify_dlg, )
        l_file_time_tip = ttk.Label(modify_dlg, text='14位数字，格式：YYYYMMDDhhmmss，非必填项；\n但另外两项未填则为必填项；')
        l_file_time.place(x=10, y=int(location["y"]) + 40, width=70, height=50)
        location = l_file_time.place_info()
        e_file_time.place(x=int(location['width']), y=int(location["y"])+13, width=300)
        location = e_file_time.place_info()
        l_file_time_tip.place(x=int(location['width'])+int(location['x'])+3, y=int(location["y"])-5)
        location = l_file_time.place_info()
        btn_modify_data = ttk.Button(modify_dlg, text='点击修改选择的当前文件', command=one_file_modify_data, style='primary.TButton')
        btn_modify_data.place(x=int(630 / 3.3) - 70, y=int(location['y']) +175, width=170, height=35)
        btn_modify_data = ttk.Button(modify_dlg, text='点击批量修改当前目录下所有文件', command=all_file_modify_data, style='primary.TButton')
        btn_modify_data.place(x=int(630 / 1.5) - 70, y=int(location['y']) + 175, width=230, height=35)
        label_tip = ttk.Label(modify_dlg, text='注意：'
                                               '\n      1）批量修改时：仅取输入修改的开始时间中"年月日"部分来修改文件，而原文件中的"时分秒"将保持不变；'
                                               '\n      2）批量修改时：不建议将多天的文件放在同一目录下进行修改，这可能会导致同一小时内多个文件数据叠加的情况；'
                                               '\n      3）批量修改时：不建议修改JKsense拼接后的文件！它有可能会是多天的数据，批量修改后可能造成数据叠加的情况；'
                                               '\n      4）新文件重命名规则：若修改了时间，则以修改的"开始时间"重命名；反之则不重命名，即按"原文件名"进行保存；'
                                               '\n      5）旧文件重命名规则：按原文件名添加后缀"_old"重命名进行保存。',
                                               style="Red.TLabel")
        loc2 = l_file_time.place_info()
        # 创建红色的标签样式
        style = ttk.Style(modify_dlg)
        style.configure("Red.TLabel", foreground="red")
        label_tip.place(x=int(loc2['x']), y=int(loc2['y'])+int(loc2['height'])-5, height=120)
        set_dialog_style(modify_dlg, window)

def data_metaInfo_settings_dlg():
    global metaInfo_settings_dlg
    def treeView1_node_selected(event):
        # 获取选中的节点和它的文本
        node = event.widget.selection()[0]
        t = event.widget.item(node, 'values')   # values为获得列值；text为获得节点名
        clear_treeView_data(treeView2)
        item, loc = add_default_metaInfo(0)
        treeView2_update(t[0], item, loc)
        open_treeView_node(treeView2, True)

    def treeView1_double_click(event):
        # 获取双击的节点
        item = treeView1.selection()[0]
        # 获取节点的文本
        text = treeView1.item(item, "values")

    def insert_dict(dictionary):
        txt = ''
        for k, v in dictionary.items():
            txt += ('              ' + str(k) + ':' + str(v) + '\n')
        return txt

    def insert_child_txt(obj, data_list):
        for i in range(6, len(data_list)):
            obj.insert('end', data_list[i]+'\n')

    def validate_data(ext_txt, ext_list):
        err = ""
        if len(ext_txt) > 0:  # 表示有数据才验证，反之则不需要验证
            for item in ext_list:
                if str(item) != '' and len(item) > 0:
                    if not (":" in item or "：" in item):
                        err = f'输入数据中必须包含“:”或“：”分隔符...'
                        break
                    else:
                        if "：" in item:
                            stmp_item = str(item).replace("：", ":")
                        else:
                            stmp_item = str(item)
                        item_list = str(stmp_item).split(':')
                        if not str(item_list[1]).isdigit():
                            err = f'输入数据中字段的长度不为数字...'
                            break
        return err

    def update_ext_meta_info(ext_list):
        # 重新加入新子节点数据
        j = 6
        tmp_dic = {}
        for item in ext_list:
            if item != '' and len(item) > 0:
                if "：" in item:
                    stmp_item = str(item).replace("：", ":")
                else:
                    stmp_item = str(item)
                item_list = str(stmp_item).split(':')
                tmp_dic[item_list[0]] = int(item_list[1])
                j += 1
        return tmp_dic

    def treeView2_double_click(event):
        cur_parent_item = None
        def save_apply():
            # '1.0'起始位置，'end-1c'结束位置
            ext_txt = text2.get('1.0', 'end-1c')
            ext_list = str(ext_txt).split('\n')
            # 首先验证数据的正确性
            err = validate_data(ext_txt, ext_list)
            if len(err) == 0:
                # 先删除扩展的所有数据
                i = 0
                del_flg = False
                for id, item in child_id.items():
                    if i > 5:
                        treeView2.delete(id)
                        del_flg = True
                    i += 1
                # 同时删除字典ext_meta_info_dic中的对应数据
                if del_flg:
                    del ext_meta_info_dic[option_item][int(code)]
                # 重新加入新子节点数据
                j = 6
                for item in ext_list:
                    if item != '' and len(item) > 0:
                        treeView2.insert(cur_parent_item, j, text=item)
                        j += 1
                # 更新ext_meta_info_dic中的对应数据
                tmp_dic = update_ext_meta_info(ext_list)
                if len(tmp_dic) > 0:
                    ext_meta_info_dic[option_item][int(code)] = tmp_dic.copy()
                tip_txt = '修改数据成功...'
                save_ini(metaInfo_modify_dlg, ini_fileName, tip_txt, False)
                show_message(metaInfo_modify_dlg, '保存提示', tip_txt, 'info')
                metaInfo_modify_dlg.destroy()
            else:
                show_message(metaInfo_modify_dlg, '错误提示', err, 'err')

        # 先缓存treeview1的当前选择项
        select_id = treeView1.selection()[0]
        view1_text = treeView1.item(select_id, 'values')
        option_item = view1_text[0]
        # 获取双击的节点
        clicked_item = event.widget.selection()[0]
        # 获得所有父项
        parent_items = treeView2.get_children('')
        if clicked_item in parent_items:
            parent_txt = treeView2.item(clicked_item, 'text')
            # 获取子节点
            children = event.widget.get_children(clicked_item)
            cur_parent_item = clicked_item
        else:
            parent_item = event.widget.parent(clicked_item)
            cur_parent_item = parent_item
            # 获取子节点
            children = event.widget.get_children(parent_item)
            parent_txt = event.widget.item(parent_item, 'text')
        # 获取子项的文本
        child_texts = []
        child_id = {}
        for child in children:
            txt = event.widget.item(child, "text")
            child_texts.append(txt)
            child_id[child] = txt
        metaInfo_modify_dlg = create_dialog_obj(300, 480, '编辑MetaDataInfo')
        # 创建红色的标签样式
        style = ttk.Style(metaInfo_modify_dlg)
        style.configure("Red.TLabel", foreground="red")
        code = str(parent_txt).split(':')[1]
        # 第一行标签和输入框
        label1 = ttk.Label(metaInfo_modify_dlg, text="     版本："+str(code))
        label1.place(x=5, y=5, width=80, height=25)
        loc = label1.place_info()
        # 第一个Text和上方的Label
        txt = insert_dict(base_meta_info_dic)
        label2 = ttk.Label(metaInfo_modify_dlg, text=f"MetaInfo Basic：\n{txt}", width=20)
        label2.place(x=int(loc['x']), y=int(loc['y'])+int(loc['height'])+5, width=150, height=120)
        # 第二个Text和上方的Label
        label3 = ttk.Label(metaInfo_modify_dlg, text="MetaInfo Extended：")
        loc2 = label2.place_info()
        label3.place(x=int(loc2['x']), y=int(loc2['y'])+int(loc2['height'])+10, width=150, height=25)
        text2 = tk.Text(metaInfo_modify_dlg)
        text2.grid_propagate(False)  # 禁止grid管理器的传播
        insert_child_txt(text2, child_texts)
        loc2 = label3.place_info()
        text2.place(x=int(loc['x'])+int(loc['width'])-20, y=int(loc2['y']) + int(loc2['height']) + 5)
        text2.config(width=30, height=13)
        label4 = ttk.Label(metaInfo_modify_dlg, text=f"注意：请严格按照《新文件协议》规定填写!", width=150, style="Red.TLabel")
        loc = text2.place_info()
        label4.place(x=int(loc['x'])-60, y=int(loc['y'])+180)
        save_btn = ttk.Button(metaInfo_modify_dlg, text="保存并应用", command=save_apply)
        save_btn.place(x=int(loc['x'])+130, y=int(loc['y'])+220)
        set_dialog_style(metaInfo_modify_dlg, metaInfo_settings_dlg)

    def treeView1_add():
        def save_apply():
            ty_key = e_type.get()
            if str(ty_key).isdigit():
                name_value = e_name.get()
                if not (ty_key in meta_info_item_dic):
                    count = len(meta_info_item_dic)+1
                    treeView1.insert('', 'end', text=f'item{count}', values=(ty_key, name_value))
                    meta_info_item_dic[ty_key] = name_value
                    ext_meta_info_dic[ty_key] = {}
                    # 新增MetaType时，也将其写入到small_data_dic
                    if not (name_value in small_data_dic):
                        small_data_dic[name_value] = {}
                    msg = '新增MetaType数据成功...'
                    save_ini(metaType_add_dlg, ini_fileName, msg, False)
                    metaType_add_dlg.destroy()
                    select_node(count-1)
                    on_tree_yview()
                else:
                    err = f'metaType类型：{ty_key}已存在...'
                    show_message(metaType_add_dlg, '错误提示', err, 'err')
            else:
                err = f'输入metaType类型：{ty_key}存在非法，只能是数字...'
                show_message(metaType_add_dlg, '错误提示', err, 'err')

        metaType_add_dlg = create_dialog_obj(260, 150, '新增MetaType')
        # 创建红色的标签样式
        style = ttk.Style(metaType_add_dlg)
        style.configure("Red.TLabel", foreground="red")
        label = ttk.Label(metaType_add_dlg, text='Type:')
        label.place(x=10, y=5, width=50, height=35)
        e_type = ttk.Entry(metaType_add_dlg)
        e_type.focus()
        loc = label.place_info()
        e_type.place(x=int(loc['x'])+int(loc['width']), y=int(loc["y"]) + 7, width=170)
        label2 = ttk.Label(metaType_add_dlg, text='Name:')
        loc = label.place_info()
        label2.place(x=10, y=int(loc['y'])+int(loc['height'])+5, width=50, height=35)
        e_name = ttk.Entry(metaType_add_dlg)
        loc = label2.place_info()
        e_name.place(x=int(loc['x']) + int(loc['width']), y=int(loc["y"]) + 7, width=170)
        label4 = ttk.Label(metaType_add_dlg, text=f"注意：请严格按照《新文件协议》规定填写!", width=150, style="Red.TLabel")
        label4.place(x=int(loc['x']), y=int(loc['y']) + int(loc['height']))
        save_btn = ttk.Button(metaType_add_dlg, text="保存并应用", command=save_apply)
        save_btn.place(x=int(230/2.4), y=int(loc['y'])+int(loc['height'])+30)
        set_dialog_style(metaType_add_dlg, metaInfo_settings_dlg)

    def treeView2_add():
        def save_apply():
            code_num = entry1.get()
            if str(code_num).isdigit():
                if not int(code_num) in ext_meta_info_dic[option_item]:
                    ext_txt = text2.get('1.0', 'end-1c')
                    ext_list = str(ext_txt).split('\n')
                    # 首先验证数据的正确性
                    err = validate_data(ext_txt, ext_list)
                    if len(err) == 0:
                        tmp_dic = update_ext_meta_info(ext_list)
                        if len(tmp_dic) > 0:
                            ext_meta_info_dic[option_item][int(code_num)] = tmp_dic.copy()
                            node = treeView1.selection()[0]
                            t = treeView1.item(node, 'values')  # values为获得列值；text为获得节点名
                            clear_treeView_data(treeView2)
                            item, loc = add_default_metaInfo(0)
                            treeView2_update(t[0], item, loc)
                            open_treeView_node(treeView2, True)
                            msg = '新增MetaDataInfo数据成功...'
                            save_ini(metaInfo_add_dlg, ini_fileName, msg, False)
                            show_message(metaInfo_add_dlg, '新增提示', msg, 'info')
                            metaInfo_add_dlg.destroy()
                        else:
                            err = '不能只添加基础MetaInfo信息...'
                            show_message(metaInfo_add_dlg, '错误提示', err, 'err')
                    else:
                        show_message(metaInfo_add_dlg, '错误提示', err, 'err')
                else:
                    err = f'输入的Version：{code_num}已存在...'
                    show_message(metaInfo_add_dlg, '错误提示', err, 'err')
            else:
                err = f'输入Version：{code_num}存在非法，只能是数字...'
                show_message(metaInfo_add_dlg, '错误提示', err, 'err')

        # 先缓存treeview1的当前选择项
        select_id = treeView1.selection()[0]
        view1_text = treeView1.item(select_id, 'values')
        option_item = view1_text[0]
        metaInfo_add_dlg = create_dialog_obj(300, 480, '新增MetaDataInfo')
        # 创建红色的标签样式
        style = ttk.Style(metaInfo_add_dlg)
        style.configure("Red.TLabel", foreground="red")
        # 第一行标签和输入框
        label1 = ttk.Label(metaInfo_add_dlg, text="     版本：")
        label1.place(x=5, y=5, width=60, height=25)
        entry1 = ttk.Entry(metaInfo_add_dlg)
        loc = label1.place_info()
        entry1.place(x=int(loc['x']) + int(loc['width']), y=int(loc['y']))
        entry1.focus_set()
        # 第一个Text和上方的Label
        txt = insert_dict(base_meta_info_dic)
        label2 = ttk.Label(metaInfo_add_dlg, text=f"MetaInfo Basic：\n{txt}", width=20)
        label2.place(x=int(loc['x']), y=int(loc['y']) + int(loc['height']) + 5, width=150, height=120)
        # 第二个Text和上方的Label
        label3 = ttk.Label(metaInfo_add_dlg, text="MetaInfo Extended：")
        loc2 = label2.place_info()
        label3.place(x=int(loc2['x']), y=int(loc2['y']) + int(loc2['height']) + 10, width=150, height=25)
        text2 = tk.Text(metaInfo_add_dlg)
        text2.grid_propagate(False)  # 禁止grid管理器的传播
        loc2 = label3.place_info()
        text2.place(x=int(loc['x']) + int(loc['width']), y=int(loc2['y']) + int(loc2['height']) + 5)
        text2.config(width=30, height=13)
        label4 = ttk.Label(metaInfo_add_dlg, text=f"注意：请严格按照《新文件协议》规定填写!", width=150, style="Red.TLabel")
        loc = text2.place_info()
        label4.place(x=int(loc['x'])-60, y=int(loc['y'])+180)
        save_btn = ttk.Button(metaInfo_add_dlg, text="保存并应用", command=save_apply)
        loc = text2.place_info()
        save_btn.place(x=int(loc['x']) + 130, y=int(loc['y']) + 220)
        set_dialog_style(metaInfo_add_dlg, metaInfo_settings_dlg)

    def treeView1_update():
        j = 1
        for k, v in meta_info_item_dic.items():
            treeView1.insert('', 'end', text=f'item{j}', values=(k, v))
            j += 1

    def add_default_metaInfo(idx):
        item = treeView2.insert("", 'end', text=f'版本:{idx}')
        j = 1
        for kk, vv in base_meta_info_dic.items():
            treeView2.insert(item, j, text=f'{kk}:{vv}')
            j += 1
        return item, j

    def select_node(idx):
        # 获取treeview中的所有项（节点）
        items = treeView1.get_children()
        if items:
            # 选中节点
            treeView1.selection_set(items[idx])

    def treeView2_update(key, item, loc):
        item1 = item
        loc1 = loc
        # 更新treeView的内容
        for k, v in ext_meta_info_dic.items():
            if k == key:
                if len(v) > 0:
                    last_key = 0
                    for k1, v1 in v.items():
                        if str(k1).isdigit():    # k1不是数字则表示，其V1并不是字典了，而是单个数据
                            if k1 != last_key and int(k1) > 0:
                                item, loc = add_default_metaInfo(k1)
                            else:
                                item = item1
                                loc = loc1
                            for k2, v2 in v1.items():
                                treeView2.insert(item, loc, text=f'{k2}:{v2}')
                                loc += 1
                            last_key = k1
                        else:
                            treeView2.insert(item, loc, text=f'{k1}:{v1}')
                break

    def on_tree_yview(*args):
        # 获取滚动条的当前位置
        pos = treeView1.yview()
        # 获取Treeview的所有项
        items = treeView1.get_children()
        # 获取最后一个可见项
        last_visible_item = treeView1.get_children()[len(items) - 1]
        # 如果最后一个可见项是滚动条滑动后的第一个项
        # if treeView1.compare(last_visible_item, ">=", items[0]):
            # 则选择最后一个可见项
        treeView1.see(last_visible_item)
            # 进行其他操作
            # do_something_with(last_visible_item)

    if metaInfo_settings_dlg is None or not (metaInfo_settings_dlg.winfo_exists()):
        metaInfo_settings_dlg = create_dialog_obj(530, 410, 'MetaInfo配置')
        # 创建并排的treeView
        treeView1 = ttk.Treeview(metaInfo_settings_dlg, height=15, columns=("Type", "Name"), show="headings")
        treeView1.column("Type", width=50, anchor='center')
        treeView1.column("Name", width=200)
        # 设置列的表头显示
        treeView1.heading("Type", text="Type")
        treeView1.heading("Name", text="Name")
        treeView2 = ttk.Treeview(metaInfo_settings_dlg, height=15)
        # 创建一个列，并且不显示表头
        treeView2["columns"] = ("one")
        treeView2.column("one", width=20, anchor="center")  # 设置宽度为200
        treeView2['show'] = 'tree'  # 隐藏表头
        # 创建滚动条
        scrollbar1 = ttk.Scrollbar(metaInfo_settings_dlg, orient=tk.VERTICAL, command=treeView1.yview)
        scrollbar2 = ttk.Scrollbar(metaInfo_settings_dlg, orient=tk.VERTICAL, command=treeView2.yview)
        treeView1.configure(yscrollcommand=scrollbar1.set)
        treeView2.configure(yscrollcommand=scrollbar2.set)
        # 添加标签
        label1 = ttk.Label(metaInfo_settings_dlg, text="Meta Type", font=("微软雅黑", 11))
        label2 = ttk.Label(metaInfo_settings_dlg, text="Meta Data Info", font=("微软雅黑", 11))
        # 添加按钮
        add_btn = ttk.Button(metaInfo_settings_dlg, text="新增", command=treeView1_add)
        add_btn2 = ttk.Button(metaInfo_settings_dlg, text="新增", command=treeView2_add)
        # 布局组件
        label1.grid(row=0, column=0, padx=5, pady=5)
        treeView1.grid(row=1, column=0, rowspan=5, padx=5, pady=5, sticky=tk.N + tk.S + tk.E)
        scrollbar1.grid(row=1, column=1, rowspan=5, padx=0.1, pady=5, sticky=tk.N + tk.S + tk.E)
        label2.grid(row=0, column=2, padx=5, pady=5)
        treeView2.grid(row=1, column=2, rowspan=5, padx=5, pady=5, sticky=tk.N + tk.S + tk.E)
        scrollbar2.grid(row=1, column=3, rowspan=5, padx=0.1, pady=5, sticky=tk.N + tk.S + tk.E)
        add_btn.grid(row=6, column=0, columnspan=2, padx=5, pady=5, sticky=tk.N)
        add_btn2.grid(row=6, column=1, columnspan=2, padx=5, pady=5, sticky=tk.N)
        treeView1_update()  # 初始化列表框内容
        treeView1.bind('<<TreeviewSelect>>', treeView1_node_selected)
        # 绑定双击事件
        treeView1.bind("<Double-1>", treeView1_double_click)
        # 绑定事件，在treeview完成数据加载后选中第一个节点
        # treeView1.bind('<<TreeviewOpen>>', select_first_node)
        treeView2.bind("<Double-1>", treeView2_double_click)
        select_node(0)
        # # 绑定滚动条事件
        set_dialog_style(metaInfo_settings_dlg, window)

def save_ini(obj, file_name, tip_txt, show_msg_flg=False):
    config = ConfigParser()
    # 保存
    config['meta_info_item_dic'] = meta_info_item_dic.copy()
    config['ext_meta_info_dic'] = ext_meta_info_dic.copy()
    config['small_data_dic'] = small_data_dic.copy()
    config['setting_item_dic'] = setting_item_dic.copy()
    config['device_types'] = device_type_dic.copy()
    config['file_types'] = file_types_dic.copy()
    with open(file_name, 'w', encoding='utf-8') as configfile:
        config.write(configfile)
        if show_msg_flg:
            show_message(obj, '保存提示', tip_txt, 'info')

def data_stats_settings_dlg():
    global stats_settings_dlg
    def save_apply_data():
        if validate_data():
            ehr_af_conf = e_ehr_af_confidence_per.get()
            heart_fast = e_heart_fast.get()
            heart_slow = e_heart_slow.get()
            bhr_af_confidence_per = e_bhr_af_confidence_per.get()
            bhr_af_eff_per = e_bhr_af_eff_per.get()
            ppg_ffs = e_ppg_ffs.get()
            ppg_af_slice = e_ppg_af_slice.get()

            setting_item_dic['ecg_af'] = int(ehr_af_conf)
            setting_item_dic['heart_fast'] = int(heart_fast)
            setting_item_dic['heart_slow'] = int(heart_slow)
            setting_item_dic['ppg_conf'] = int(bhr_af_confidence_per)
            setting_item_dic['ppg_eff_per'] = int(bhr_af_eff_per)
            setting_item_dic['ppg_ffs'] = float(ppg_ffs)
            # setting_item_dic['ecg_af_slice'] = ecg_af_slice
            setting_item_dic['ppg_af_slice'] = int(ppg_af_slice)
            save_ini(stats_settings_dlg, ini_fileName, '保存数据成功...', True)

    def validate_data():
        ehr_af_conf = e_ehr_af_confidence_per.get()
        if not check_content(ehr_af_conf, e_ehr_af_confidence_per, 'ECG房颤置信度'):
            return False
        if not check_per(ehr_af_conf, e_ehr_af_confidence_per, 'ECG房颤置信度'):
            return False
        heart_fast = e_heart_fast.get()
        if not check_content(heart_fast, e_heart_fast, '心率过快'):
            return False
        heart_slow = e_heart_slow.get()
        if not check_content(heart_slow, e_heart_slow, '心率过慢'):
            return False
        bhr_af_confidence_per = e_bhr_af_confidence_per.get()
        if not check_content(bhr_af_confidence_per, e_bhr_af_confidence_per, 'PPG房颤置信度'):
            return False
        if not check_per(bhr_af_confidence_per, e_bhr_af_confidence_per, 'PPG房颤置信度'):
            return False
        bhr_af_eff_per = e_bhr_af_eff_per.get()
        if not check_content(bhr_af_eff_per, e_bhr_af_eff_per, 'PPG房颤有效占比'):
            return False
        if not check_per(bhr_af_eff_per, e_bhr_af_eff_per, 'PPG房颤有效占比'):
            return False
        ppg_af_slice = e_ppg_af_slice.get()
        if not check_content(ppg_af_slice, e_ppg_af_slice, 'PPG房颤片段'):
            return False
        if not check_per(ppg_af_slice, e_ppg_af_slice, 'PPG房颤片段'):
            return False
        ppg_ffs = e_ppg_ffs.get()
        if not check_content(ppg_ffs, e_ppg_ffs, 'PPG采样率'):
            return False
        return True

    def check_per(txt, obj, tip_txt):
        if int(txt) > 100 or int(txt) < 1:
            show_message(stats_settings_dlg, '错误提示', f'【{tip_txt}】数据存在非法...', 'err')
            obj.focus_set()
            return False
        return True

    def check_content(content, obj, tip_txt):
        try:
            float(content)  # 尝试将字符串转换为浮点数
            return True
        except ValueError:
            show_message(stats_settings_dlg, '错误提示', f'【{tip_txt}】数据存在非法...', 'err')
            obj.focus_set()
            return False

    def get_settings_data(k):
        variable = tk.StringVar(value=setting_item_dic[k])
        return variable

    def set_entry_value(obj, v):
        obj.delete(0, tk.END)
        obj.insert(0, str(v))

    def load_item_value():
        for k, v in setting_item_dic.items():
            if k == 'ecg_af':
                set_entry_value(e_ehr_af_confidence_per, v)
            elif k == 'heart_fast':
                set_entry_value(e_heart_fast, v)
            elif k == 'heart_slow':
                set_entry_value(e_heart_slow, v)
            elif k == 'ppg_conf':
                set_entry_value(e_bhr_af_confidence_per, v)
            elif k == 'ppg_eff_per':
                set_entry_value(e_bhr_af_eff_per, v)
            elif k == 'ppg_ffs':
                set_entry_value(e_ppg_ffs, v)
            elif k == 'ppg_af_slice':
                set_entry_value(e_ppg_af_slice, v)

    if stats_settings_dlg is None or not (stats_settings_dlg.winfo_exists()):
        my_font = Font(family="微软雅黑", size=11, weight="bold")
        stats_settings_dlg = create_dialog_obj(585, 280, '数据统计设置')
        l_ehr_set = ttk.Label(stats_settings_dlg, text='★ EHR房颤统计设置：', font=my_font)
        l_ehr_set.place(x=10, y=5, width=150, height=25)
        l_ehr_af_confidence = ttk.Label(stats_settings_dlg, text='【ECG房颤】按EHR文件中房颤置信度≥')
        loc = l_ehr_set.place_info()
        l_ehr_af_confidence.place(x=30, y=int(loc['y'])+int(loc['height']), width=217, height=25)
        e_ehr_af_confidence_per = ttk.Entry(stats_settings_dlg)
        loc = l_ehr_af_confidence.place_info()
        e_ehr_af_confidence_per.place(x=int(loc['x']) + int(loc['width']), y=int(loc['y']), width=30)
        label1 = ttk.Label(stats_settings_dlg, text='%进行统计；')
        loc = e_ehr_af_confidence_per.place_info()
        label1.place(x=int(loc['x']) + int(loc['width']), y=int(loc['y'])+1)
        l_bhr_set = ttk.Label(stats_settings_dlg, text='★ BHR相关统计设置：', font=my_font)
        loc = l_ehr_af_confidence.place_info()
        l_bhr_set.place(x=10, y=int(loc['y'])+int(loc['height'])+5, width=150, height=25)
        l_heart_fast = ttk.Label(stats_settings_dlg, text='【心率过快】按BHR文件中脉率≥')
        loc = l_bhr_set.place_info()
        l_heart_fast.place(x=30, y=int(loc['y']) + int(loc['height']), width=182, height=25)
        e_heart_fast = ttk.Entry(stats_settings_dlg)
        loc = l_heart_fast.place_info()
        e_heart_fast.place(x=int(loc['x']) + int(loc['width']), y=int(loc['y']), width=30)
        label2 = ttk.Label(stats_settings_dlg, text='次/分进行统计；')
        loc = e_heart_fast.place_info()
        label2.place(x=int(loc['x']) + int(loc['width']), y=int(loc['y'])+1)
        l_heart_slow = ttk.Label(stats_settings_dlg, text='【心率过慢】按BHR文件中脉率≤')
        loc = l_heart_fast.place_info()
        l_heart_slow.place(x=30, y=int(loc['y']) + int(loc['height']), width=182, height=25)
        e_heart_slow = ttk.Entry(stats_settings_dlg)
        loc = l_heart_slow.place_info()
        e_heart_slow.place(x=int(loc['x']) + int(loc['width']), y=int(loc['y']), width=30)
        label3 = ttk.Label(stats_settings_dlg, text='次/分进行统计；')
        loc = e_heart_slow.place_info()
        label3.place(x=int(loc['x']) + int(loc['width']), y=int(loc['y'])+1)
        l_bhr_af_confidence = ttk.Label(stats_settings_dlg, text='【PPG房颤】BHR文件中发生房颤置信度≥')
        loc = l_heart_slow.place_info()
        l_bhr_af_confidence.place(x=30, y=int(loc['y']) + int(loc['height']), width=230, height=25)
        e_bhr_af_confidence_per = ttk.Entry(stats_settings_dlg)
        loc = l_bhr_af_confidence.place_info()
        e_bhr_af_confidence_per.place(x=int(loc['x']) + int(loc['width']), y=int(loc['y']), width=30)
        label4 = ttk.Label(stats_settings_dlg, text='%且有效占比≥')
        loc = e_bhr_af_confidence_per.place_info()
        label4.place(x=int(loc['x']) + int(loc['width']), y=int(loc['y']), width=85)
        e_bhr_af_eff_per = ttk.Entry(stats_settings_dlg)
        loc = label4.place_info()
        e_bhr_af_eff_per.place(x=int(loc['x']) + int(loc['width']), y=int(loc['y']), width=30)
        label5 = ttk.Label(stats_settings_dlg, text='%时，按≥50%真实负荷统计；')
        loc = e_bhr_af_eff_per.place_info()
        label5.place(x=int(loc['x']) + int(loc['width']), y=int(loc['y'])+1)
        l_ppg_af_slice = ttk.Label(stats_settings_dlg, text='【PPG房颤片段】按连续时长≥')
        loc = l_bhr_af_confidence.place_info()
        l_ppg_af_slice.place(x=30, y=int(loc['y']) + int(loc['height']), width=170, height=25)
        e_ppg_af_slice = ttk.Entry(stats_settings_dlg)
        loc = l_ppg_af_slice.place_info()
        e_ppg_af_slice.place(x=int(loc['x']) + int(loc['width']), y=int(loc['y']), width=30)
        label6 = ttk.Label(stats_settings_dlg, text='秒进行分片统计；')
        loc = e_ppg_af_slice.place_info()
        label6.place(x=int(loc['x']) + int(loc['width']), y=int(loc['y'])+1)
        l_ppg_ffs = ttk.Label(stats_settings_dlg, text='【PPG采样率】按规定采样率25.6±')
        loc = l_ppg_af_slice.place_info()
        l_ppg_ffs.place(x=30, y=int(loc['y']) + int(loc['height']), width=192, height=25)
        e_ppg_ffs = ttk.Entry(stats_settings_dlg)
        loc = l_ppg_ffs.place_info()
        e_ppg_ffs.place(x=int(loc['x']) + int(loc['width']), y=int(loc['y']), width=50)
        label6 = ttk.Label(stats_settings_dlg, text='进行统计。')
        loc = e_ppg_ffs.place_info()
        label6.place(x=int(loc['x']) + int(loc['width']), y=int(loc['y'])+1)

        btn_save_apply_data = ttk.Button(stats_settings_dlg, text='点击保存并应用', command=save_apply_data,
                                     style='primary.TButton')
        loc = l_ppg_ffs.place_info()
        btn_save_apply_data.place(x=int(550 / 2.7), y=int(loc['y']) + 40, width=150, height=35)
        set_dialog_style(stats_settings_dlg, window)
        e_ehr_af_confidence_per.focus_set()
        load_item_value()

def file_type_settings_dlg():
    global fileType_settings_dlg

    def dropdown_changed(event):
        selected_value = combobox.get()
        label2.config(text=f'<{selected_value}>支持的文件类型：')
        add_btn.config(text=f'新增【{str(combobox.get()).split("--")[1]}】文件类型')
        get_listbox_item()

    def get_listbox_item():
        listbox.delete(0, tk.END)
        tmp = file_types_dic[combobox.get()]
        tmp_list = str(tmp).split(';')
        for item in tmp_list:
            if item != '':
                listbox.insert(tk.END, item)

    def get_add_file_type_data(obj):
        item = obj.get()
        if not '.' in item:
            item = '.' + item
        if not '*' in item:
            item = '*' + item
        return item.lower()   # 统一转为小写

    def add_device_type_data():
        def validate_date(name, suf):
            flg = True
            if len(name) > 0 and len(suf) > 0:
                for i in range(len(suf)):
                    if not str(suf[i]).isalpha():
                        show_message(deviceType_add_dlg, '错误提示', f'设备类型后缀【{suf}】包含非字母数据，请重新输入...', 'err')
                        flg = False
                        break
                if flg:   # 表示前面处理suf时已为假了，就不用再处理后续数据
                    for item in combobox['values']:
                        tmp_list = str(item).split('--')
                        if name == tmp_list[0]:
                            show_message(deviceType_add_dlg, '错误提示', f'设备类型名称【{name}】已存在，请重新输入...', 'err')
                            flg = False
                            break
                        if suf == tmp_list[1]:
                            show_message(deviceType_add_dlg, '错误提示', f'设备类型后缀【{suf}】已存在，请重新输入...', 'err')
                            flg = False
                            break
            elif len(name) == 0:
                show_message(deviceType_add_dlg, '错误提示', f'设备类型名称不能为空...', 'err')
                flg = False
            elif len(suf) == 0:
                show_message(deviceType_add_dlg, '错误提示', f'设备类型后缀不能为空...', 'err')
                flg = False
            return flg

        def save_apply_data():
            name = e_type.get()
            suf = e_suf_type.get()
            if validate_date(name, suf):
                combobox["values"] += tuple([name+'--'+suf])
                combobox.set(tuple([name+'--'+suf]))
                file_types_dic[combobox.get()] = ''
                device_type_dic['xjk_device_type'] += f',{name}--{suf}'
                # 保存修改后的数据
                save_ini(deviceType_add_dlg, ini_fileName, '添加数据成功...', True)

        deviceType_add_dlg = create_dialog_obj(350, 120, f'新增设备类型')
        # 创建红色的标签样式
        style = ttk.Style(deviceType_add_dlg)
        style.configure("Red.TLabel", foreground="red")
        label = ttk.Label(deviceType_add_dlg, text=f'设备类型名称:')
        label.place(x=10, y=5, width=80, height=35)
        e_type = ttk.Entry(deviceType_add_dlg)
        e_type.focus()
        loc = label.place_info()
        e_type.place(x=int(loc['x']) + int(loc['width']), y=int(loc['y'])+5, width=80)
        labe2 = ttk.Label(deviceType_add_dlg, text=f'--后缀：')
        loc = e_type.place_info()
        labe2.place(x=int(loc['x'])+int(loc['width']), y=int(loc['y'])-7, width=45, height=35)
        loc = labe2.place_info()
        e_suf_type = ttk.Entry(deviceType_add_dlg)
        e_suf_type.place(x=int(loc['x']) + int(loc['width']), y=int(loc['y'])+7, width=70)

        save_btn = ttk.Button(deviceType_add_dlg, text="保存并应用", command=save_apply_data)
        save_btn.place(x=120, y=int(loc['y']) + int(loc['height'])+20)
        set_dialog_style(deviceType_add_dlg, fileType_settings_dlg)

    def add_file_type_data():
        data_prefix = str(combobox.get()).split('--')[1]
        def add_listbox_item():
            item = get_add_file_type_data(e_type)
            listbox.insert('end', item)

        def prefix_validate(add_file_type_data):
            flg = True
            if data_prefix in add_file_type_data:
                tmp = add_file_type_data[2:5]
                if tmp != data_prefix:
                    show_message(fileType_add_dlg, '错误提示', f'添加的文件类型:{add_file_type_data}'
                                                           f',不符合：前三位字母必须以：{data_prefix}'
                                                           f'开头的规则！请重新输入...', 'err')
                    flg = False
            else:
                show_message(fileType_add_dlg, '错误提示', f'添加的文件类型:{add_file_type_data}'
                                                       f'，与选择的设备：{combobox.get()}不匹配！请重新输入...', 'err')
                flg = False
            return flg

        def save_apply_data():
            if len(e_type.get()) > 0:
                add_file_type_data = get_add_file_type_data(e_type)
                if prefix_validate(add_file_type_data):
                    if add_file_type_data not in listbox.get(0, tk.END):  # 检查项目是否已经存在于列表中
                        add_listbox_item()
                        apply_save_data(fileType_add_dlg, True)
                        e_type.delete(0, tk.END)  # 清空输入框
                    else:
                        show_message(fileType_add_dlg, '错误提示',
                                     f'添加的文件类型:{add_file_type_data}已存在！请重新输入...', 'err')
            else:
                show_message(fileType_add_dlg, '错误提示', f'文件类型不能为空...', 'err')

        fileType_add_dlg = create_dialog_obj(270, 120, f'新增【{data_prefix}】文件类型')
        # 创建红色的标签样式
        style = ttk.Style(fileType_add_dlg)
        style.configure("Red.TLabel", foreground="red")
        label = ttk.Label(fileType_add_dlg, text=f'输入以【{data_prefix}】开头的文件类型:')
        label.place(x=10, y=5, width=170, height=35)
        e_type = ttk.Entry(fileType_add_dlg)
        e_type.focus()
        loc = label.place_info()
        e_type.place(x=int(loc['x'])+int(loc['width'])+5, y=int(loc['y'])+5, width=70)
        label4 = ttk.Label(fileType_add_dlg, text=f"注意：请严格按照《新文件协议》规定填写!", width=150, style="Red.TLabel")
        label4.place(x=int(loc['x']), y=int(loc['y']) + int(loc['height']))
        save_btn = ttk.Button(fileType_add_dlg, text="保存并应用", command=save_apply_data)
        save_btn.place(x=int(230 / 2.4), y=int(loc['y']) + int(loc['height']) + 30)
        set_dialog_style(fileType_add_dlg, fileType_settings_dlg)

    def delete_selected(listbox):
        # 获取选中的项的索引
        selected_indices = [i for i in listbox.curselection()]
        # 逆序删除以避免索引错位的问题
        for index in reversed(selected_indices):
            listbox.delete(index)
            break

    def apply_save_data(obj, flg):
        all_itemes = listbox.get(0, tk.END)
        file_types_dic[combobox.get()] = ''
        f_ty = ''
        for item in all_itemes:
            f_ty += (item + ';')
        file_types_dic[combobox.get()] = f_ty
        # 重新获得所有文件类型
        global all_file_types
        all_file_types = get_all_file_types()
        # 保存修改后的数据
        save_ini(obj, ini_fileName, '添加数据成功...', flg)

    def del_file_tyep_data():
        select_item = listbox.curselection()
        if len(select_item) != 0:
            v = show_message(fileType_settings_dlg, '删除提示',
                             f'请问真的要删除选择的文件类型：{listbox.get(select_item[0])}吗？', 'ask', tip_txt='')
            if v == 'yes':
                delete_selected(listbox)
                apply_save_data(fileType_settings_dlg, False)
        else:
            show_message(fileType_settings_dlg, '错误提示', f'请先选中要删除的文件类型数据...', 'err')


    if fileType_settings_dlg is None or not (fileType_settings_dlg.winfo_exists()):
        my_font = Font(family="微软雅黑", size=11, weight="bold")
        fileType_settings_dlg = create_dialog_obj(320, 380, '文件类型配置')
        label1 = ttk.Label(fileType_settings_dlg, text='设备类型：', font=my_font)
        label1.place(x=10, y=5, width=70, height=25)
        # 创建下拉列表
        combobox = ttk.Combobox(fileType_settings_dlg, state='readonly')
        loc = label1.place_info()
        combobox.place(x=int(loc['x'])+int(loc['width'])+5, y=int(loc['y']), width=120)
        # 绑定"变化"事件，每次选择时都会触发
        combobox.bind("<<ComboboxSelected>>", dropdown_changed)
        # 下拉列表的可能选项
        tmp = list(device_type_dic.values())
        tmp_list = tmp[0].split(',')
        combobox["values"] = tmp_list
        # device_type_tuple = tuple(tmp_list)
        # combobox["values"] = device_type_tuple
        combobox.current(0)  # 设置默认选中第一个选项
        add_type_btn = ttk.Button(fileType_settings_dlg, text=f'新增设备类型', command=add_device_type_data,
                             style='primary.TButton')
        loc = combobox.place_info()
        add_type_btn.place(x=int(loc['x'])+int(loc['width'])+5, y=int(loc['y'])-2)
        data_prefix = str(combobox.get()).split('--')[1]
        label2 = ttk.Label(fileType_settings_dlg, text=f'<{combobox.get()}>支持的文件类型：')
        loc = label1.place_info()
        label2.place(x=10, y=int(loc['y'])+int(loc['height'])+10, height=25)
        listbox = tk.Listbox(fileType_settings_dlg)
        loc = label2.place_info()
        loc2 = combobox.place_info()
        listbox.place(x=int(loc2['x']), y=int(loc['y'])+int(loc['height']), width=160, height=260)
        add_btn = ttk.Button(fileType_settings_dlg, text=f'新增【{data_prefix}】文件类型', command=add_file_type_data, style='primary.TButton')
        del_btn = ttk.Button(fileType_settings_dlg, text='删除选中类型', command=del_file_tyep_data, style='primary.TButton')
        loc = listbox.place_info()
        add_btn.place(x=int(loc['x'])-30, y=int(loc['y'])+ int(loc['height'])+10, width=125)
        loc2 = add_btn.place_info()
        del_btn.place(x=int(loc2['x'])+int(loc2['width'])+10, y=int(loc['y'])+ int(loc['height'])+10)
        get_listbox_item()
        set_dialog_style(fileType_settings_dlg, window)

def disp_about_dlg():
    messagebox.showinfo('消息提示', '本工具仅支持【新文件协议】的相关解析...\n'
                                'V1.0.0.0-->新文件协议解析工具首次发版；\n'
                                'V1.0.0.1-->1）增加了修改计步文件的功能；\n'
                                '                   2）修改JKsense文件时更新文件名开始时间与结束时间的功能；\n'
                                '                   3）修改部分已知Bug；\n'
                                'V1.0.0.2-->增加了：文件类型配置的功能。\n')

def timestamp_to_date_dlg():
    messagebox.showinfo('消息提示', '功能开发中，敬请期待...')

def copy_txt_content():
    cur_item = tree_view.item(tree_view.focus())
    window.clipboard_clear()
    window.clipboard_append(cur_item['text'])

# 将分析结果数据体中的所有数据导出到csv中
def pack_data_export_to_csv():
    all_data_list = []
    for item in pack_data_list:
        i = 0
        for k, v in item.items():
            if i > 4:  # 丢掉前4个时间与数据长度等数据
                if i == 5:    # 第5行为数据表头
                    s = v.split('：')
                    table_head_list, loc_list = disope_table_head(s[1])
                    if len(table_head_list) > 1:
                        s_list = []
                        for item1 in table_head_list:
                            for item2 in item1:
                                s_list.append(item2)
                        all_data_list.append(s_list)
                    else:
                        all_data_list = table_head_list.copy()
                else:   # 第6行开始为数据
                    if len(v) == 1:
                        all_data_list.append(v[0])
                    else:
                        s_list = []
                        if len(loc_list) > 0:
                            if len(loc_list) == 1:
                                m = 0
                                for idx in loc_list:
                                    j = 1
                                    channel = len(table_head_list[m])
                                    for v3 in v[idx-1]:
                                        s_list.append(v3)
                                        if (j % channel) == 0:
                                            all_data_list.append(s_list.copy())
                                            s_list.clear()
                                        j += 1
                                    m += 1
                            elif len(loc_list) > 1:
                                m = 0
                                # for idx in loc_list:
                                idx = loc_list[0] - 1
                                idx2 = loc_list[1] - 1
                                j = 1
                                channel = len(table_head_list[m])
                                for v3 in v[idx]:
                                    s_list.append(v3)
                                    if (j-1) < len(v[idx2]):
                                        s_list.append(v[idx2][j-1])
                                    if (j % channel) == 0:
                                        all_data_list.append(s_list.copy())
                                        s_list.clear()
                                    j += 1
                                    m += 1
                        else:
                            stmp_list = []
                            for value in v:
                                if len(value) == 1:
                                    stmp_list.append(value[0])
                                else:
                                    stmp_list.append(value)
                            all_data_list.append(stmp_list)
            i += 1
    if len(all_data_list) > 0:
        # 写入csv
        (file_path, fileName) = os.path.split(file_name.get())
        try:
            with open(f'{file_path}/{fileName}.csv', 'w', newline='') as f:
                w = csv.writer(f)
                w.writerows(all_data_list)
                msg = f'导出包数据成功，文件名为[{file_path}/{fileName}.csv]...'
                k = show_message(window, '消息提示', msg, 'ask')
                if k == 'yes':
                    # 根据操作系统使用不同的方法打开Excel文件
                    if sys.platform.startswith('win'):
                        os.startfile(f'{file_path}/{fileName}.csv')
                    else:
                        os.subprocess.run(['open', f'{file_path}/{fileName}.csv'])  # 对于Mac
        except Exception as e:
            err = '导出包数据失败：文件已被占用，请先关闭后再重试...'
            show_message(window, '消息提示', err, 'err')
    else:
        err = f'导出包数据失败：没有包数据...'
        show_message(window, '消息提示', err, 'err')

def create_menu():
    # 创建菜单栏
    menubar = tk.Menu(window)
    window.config(menu=menubar)
    # 创建一级菜单
    setting_menu = tk.Menu(menubar, tearoff=0)
    setting_menu.add_command(label='MetaInfo配置', command=data_metaInfo_settings_dlg)
    setting_menu.add_separator()
    setting_menu.add_command(label='数据统计设置', command=data_stats_settings_dlg)
    setting_menu.add_separator()
    setting_menu.add_command(label='文件类型配置', command=file_type_settings_dlg)

    menubar.add_cascade(label='首选项', menu=setting_menu)

    tools_menu = tk.Menu(menubar, tearoff=0)
    tools_menu.add_command(label='修改文件数据', command=modify_fileData_dlg)
    tools_menu.add_separator()
    tools_menu.add_command(label='文  件  解  密', command=decrypt_file_dlg)
    # tools_menu.add_separator()
    # tools_menu.add_command(label='时 间 戳 转 换', command=timestamp_to_date_dlg)
    menubar.add_cascade(label='工 具', menu=tools_menu)

    about_menu = tk.Menu(menubar, tearoff=0)
    about_menu.add_command(label='关于...', command=disp_about_dlg)
    menubar.add_cascade(label='说 明', menu=about_menu)

def popup(event):
    popup_menu.post(event.x_root, event.y_root)
    window.update()

def home_layout():
    l_select_file.place(x=8, y=2, width=l_width, height=l_height)
    l_select_file_location = l_select_file.place_info()
    file_name.place(x=int(l_select_file_location['width']), y=int(l_select_file_location["y"])+7,
                    width=width-int(l_select_file_location['width'])-95)
    file_name.focus()
    btn_select = ttk.Button(window, text='选择', command=option_file, style='primary.TButton')
    file_name_location = file_name.place_info()
    btn_select.place(x=int(file_name_location['width'])+int(l_select_file_location['width'])+4,
                     y=int(file_name_location["y"])-1, width=70)
    btn_parse = ttk.Button(window, text='点击开始解析',command=start_parse_file, style='primary.TButton')
    btn_parse.place(x=int(width/2)-70, y=int(l_select_file_location['height']) * 1.1, width=150, height=35)
    location = btn_parse.place_info()
    # tree_view.pack(fill=BOTH, expand=YES)
    tree_view.place(x=3, y=int(location['y'])+int(location['height'])+5, width=width-20,
                    height=height-int(location['y'])+int(location['height'])-90)
    tree_view.insert('', 0, text='暂时无数')
    location = tree_view.place_info()
    ybar.set(location['x']+location['width'], location['y'])

def clear_treeView_data(obj):
    # 删除原节点
    for _ in map(obj.delete, obj.get_children("")):
        pass

# 表格内容插入
def fill_data_to_tree(head_data_list=None, mateInfo_length=0, mateInfo_list=None, pack_data_list=None, sum_result='无', err_msg='无'):
    # 删除原节点
    clear_treeView_data(tree_view)
    if head_data_list is None or len(head_data_list) == 0:
        head_data_list = '无'
    if mateInfo_list is None or len(mateInfo_list) == 0:
        mateInfo_list = '无'
    if pack_data_list is None or len(pack_data_list) == 0:
        pack_data_list = '无'
    # 表示没有统计结果
    if len(sum_result) == 0:
        sum_result = '无'
    # 表示没有异常
    if len(err_msg) == 0:
        err_msg = '无'
    # 更新插入新节点
    dic_data = [{"node":'文件头',
                'data': head_data_list},
                {"node": 'MetaDataInfo：'+str(mateInfo_length)+'Bytes',
                 'data': mateInfo_list},
                {"node": '数据体',
                 'data': pack_data_list},
                {'node': '统计结果',
                 'data': sum_result},
                {'node': '解析异常',
                 'data': err_msg}
                ]
    dic_len = len(dic_data)
    try:
        logging.info('开始填充数据到显示控件...')
        global progress_val
        progress_val += 5
        update_progress(progress_val)
        for i in range(dic_len):
            data_node = dic_data[i]['node']
            item = tree_view.insert("", i, text=data_node)
            progress_val += 10
            update_progress(progress_val)
            if not dic_data[i]['data'] == None:
                data_len = len(dic_data[i]['data'])
                for j in range(data_len):
                    start_filling(item, j, dic_data[i]['data'][j])

        # 调用一个展开treeView控件一级节点的功能
        open_treeView_node(tree_view, True)
        logging.info('填充数据到显示控件结束...')
    except Exception as e:
        logging.error(f'填充数据到显示控件出错啦！原因为：{e}...')

def fill_treeview(item, j, dic_data):
    if not 'node' in dic_data:
        tree_view.insert(item, j, text=dic_data)
    else:  # 表明还包含有node
        data_node2 = dic_data['node']
        item2 = tree_view.insert(item, j, text=data_node2)
        item2_data_len = len(dic_data)
        j = 0
        data_count = 305   # 由于显示加载会出现卡顿的情况，故此处只添加显示前300项
        for k in range(1, item2_data_len):
            if j < data_count:
                tree_view.insert(item2, k - 1, text=dic_data[f'data{k}'])
            else:
                tree_view.insert(item2, k - 1, text=f'此处{(data_count-5)}项之后的数据省略了，若要查看全部数据请导出CSV...')
                break
            # 假设每插入一定数量的项就停止一段时间
            if k % (1000 // 10) == 0:
                window.update()  # 允许处理其他事件
            j += 1

def start_filling(item, j, dic_data):
    thread = Thread(target=fill_treeview, args=(item, j, dic_data))
    thread.daemon = True
    thread.start()

# def hide_title_bar(hwnd):
#     style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
#     style &= ~win32con.WS_CAPTION
#     win32gui.SetWindowLong(hwnd, win32con.GWL_STYLE, style)
#     win32gui.SetWindowPos(hwnd, win32con.HWND_TOP, 0, 0, 0, 0, win32con.SWP_FRAMECHANGED)

# 设置窗体的背景颜色
def change_titlebar_color(obj, color):
    # 这个函数是一个示例，但它不会工作，因为Tkinter不支持直接更改标题栏颜色
    obj.configure(background=color)

if __name__ == '__main__':
    decrypt_dialog = None
    modify_dlg = None
    stats_settings_dlg = None
    fileType_settings_dlg = None
    metaInfo_settings_dlg = None
    ini_fileName = 'systemInfo.ini'
    create_time = time.strftime('%Y%m%d', time.localtime())
    config_logging("./log/", create_time + '.log', logging.INFO, logging.INFO)
    # 初始化加解密对象
    folder = os.path.split(os.path.abspath(__file__))[0]
    path = '/dll'
    dll_obj = File_decrypt('DataEncryptorDll.dll', folder+path)
    window = tk.Tk()
    path = tk.StringVar()
    l_select_file = ttk.Label(window, text='选择文件：')
    file_name = ttk.Entry(window, textvariable=path)
    # 垂直水平滚动条
    ybar = ttk.Scrollbar(window)
    ybar.pack(side=RIGHT, fill=Y)
    # # 水平滚动条
    xbar = ttk.Scrollbar(window, orient=HORIZONTAL)
    xbar.pack(side=BOTTOM, fill=X)
    tree_view = ttk.Treeview(window, yscrollcommand=ybar.set, xscrollcommand=xbar.set)
    ybar.config(command=tree_view.yview)
    xbar.config(command=tree_view.xview)
    tree_view['show'] = 'tree'  # 隐藏表头
    # tool_tip.createToolTip(tree_view,'单击鼠标右键可打开弹出菜单')
    l_width = 70
    l_height = 35
    s_width = window.winfo_screenwidth()
    s_height = window.winfo_screenheight()
    width = 1300
    height = 850
    left = int((s_width - width) / 2)
    top = int((s_height - height) / 2)
    window.title('【新文件协议】解析工具-->V1.0.0.2')
    window.geometry('%dx%d+%d+%d' % (width, height, left, top))
    window.resizable(0, 0)  # 隐藏最小、最大化
    style = ttk.Style()
    # 设置Treeview的字体
    style.configure('Treeview', font=('宋体', 12))
    f_width = window.winfo_width()
    create_menu()
    home_layout()
    # 创建一个弹出菜单
    popup_menu = tk.Menu(window, tearoff=False)
    popup_menu.add_command(label='复制选择行内容', command=copy_txt_content)
    popup_menu.add_separator()
    popup_menu.add_command(label='导出包数据(csv)', command=pack_data_export_to_csv)
    tree_view.bind('<Button-3>', popup)
    pack_data_list = []
    window.columnconfigure(0, weight=1)
    # 读取ini文件
    if os.path.exists('./' + ini_fileName):
        if not getSysFileData(f'./{ini_fileName}'):
            exit(0)
    else:
        logging.info(f'没有找到配置文件：{ini_fileName}...')
        exit(0)
    all_file_types = get_all_file_types()
    window.update()
    window.mainloop()
