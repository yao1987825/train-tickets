from prettytable import PrettyTable
import colorama
from stations import stations


class TrainsCollection:
    header = '车次 车站 时间 历时 商务/特等 一等 二等 高软 软卧 动卧 硬卧 软座 硬座 无座 其他'.split()
    # 座位字段下标是 12306 返回格式里的固定位置, 别改(改错整列都会错位):
    #   21 高级软卧 22 其他 23 软卧 24 软座 25 特等座 26 无座
    #   28 硬卧 29 硬座 30 二等座 31 一等座 32 商务座 33 动卧
    code2station = {v: k for k, v in stations.items()}  # 车站数据的value:key翻转

    def __init__(self, trains_list, options=''):
        self.trains_list = trains_list
        self.options = options

    def parse_trains(self, train):
        tmp_list = train.split('|')
        train_no = tmp_list[3]

        if self.options and not train_no[0].lower() in self.options:
            return

        # 出发站/到达站用 [6]/[7](这一段实际上车的站), 不是 [4]/[5](始发/终点)
        from_station = self.code2station.get(tmp_list[6]) or tmp_list[6]
        to_station = self.code2station.get(tmp_list[7]) or tmp_list[7]
        from_time = tmp_list[8]
        to_time = tmp_list[9]
        elapse = tmp_list[10]

        # 座位字段下标: 上游整体错位了一格(表现为"二等座"那列全是空的)。
        # 2026-10 真机逐个车次核对过:
        #   G1   复兴号 [30]=有 二等 / [31]=有 一等 / [32]=13 商务
        #   K545 普速   [29]=有 硬座 / [28]=无 硬卧 / [26]=有 无座
        gr_num = tmp_list[21] or '--'  # 高级软卧
        qt_num = tmp_list[22] or '--'  # 其他
        rw_num = tmp_list[23] or '--'  # 软卧
        rz_num = tmp_list[24] or '--'  # 软座
        tz_num = tmp_list[25] or '--'  # 特等座
        wz_num = tmp_list[26] or '--'  # 无座
        # yb_num = tmp_list[27] or '--' #
        yw_num = tmp_list[28] or '--'  # 硬卧
        yz_num = tmp_list[29] or '--'  # 硬座
        ze_num = tmp_list[30] or '--'  # 二等座
        zy_num = tmp_list[31] or '--'  # 一等座
        swz_num = tmp_list[32] or '--'  # 商务座
        srrb_num = tmp_list[33] or '--'  # 动卧
        swz_tz_num = swz_num or tz_num or '--'  # 商务/特等座

        nums = [swz_tz_num, zy_num, ze_num, gr_num, rw_num, srrb_num, yw_num, rz_num, yz_num, wz_num, qt_num]
        nums = [self.color_ticket_num(num) for num in nums]

        return [
            train_no,
            '\n'.join([
                colorama.Fore.GREEN + from_station + colorama.Fore.RESET,
                colorama.Fore.RED + to_station + colorama.Fore.RESET]),
            '\n'.join([
                colorama.Fore.GREEN + from_time + colorama.Fore.RESET,
                colorama.Fore.RED + to_time + colorama.Fore.RESET]),
            elapse
        ] + nums

    def get_new_trains(self):
        for train in self.trains_list:
            new_trains = self.parse_trains(train)
            if new_trains:
                yield new_trains
            else:
                continue

    def color_ticket_num(self, num):
        '''为余票数量着色'''
        Fore = colorama.Fore
        return Fore.GREEN + num + Fore.RESET if num == '有' or num.isdigit() and int(num) > 0 else (
            Fore.RED + num + Fore.RESET if num == '无' else num)

    def pretty_print(self):
        pt = PrettyTable()
        # 新版 prettytable(>=0.7) 的公开 API 是 field_names,
        # 原来的私有方法 _set_field_names 已经被删掉, 直接调会 AttributeError。
        try:
            pt.field_names = TrainsCollection.header
        except (AttributeError, TypeError):
            pt._set_field_names(TrainsCollection.header)
        colorama.init()
        for train in self.get_new_trains():
            pt.add_row(train)
        print(pt)
