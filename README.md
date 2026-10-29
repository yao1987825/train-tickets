# train-tickets

可在命令行下查询 12306 火车余票的 Python cli 工具。

## 用法

```bash
pip install -r requirements.txt      # requests / colorama / docopt / prettytable
python trainTickets.py 北京 上海 2026-10-30
python trainTickets.py -dg 成都 南京 2026-10-30     # 只看高铁/动车
```

## 2026-10 修复了什么(原版已经跑不动了)

12306 这几年改过接口, 原版直接跑会报 `JSONDecodeError`。三处修复:

1. **必须先拿会话 Cookie 再查接口**。直接 GET 余票查询接口只会返回 HTML 反爬页,
   不是 JSON。现在先 GET 余票首页(`/otn/leftTicket/init`)拿 cookie, 再带
   `Referer` / `X-Requested-With` / `User-Agent` 去查。
2. **座位字段下标整体错位了一格**。原版把 `[21]` 当成"高级软卧", 实际 12306 的
   固定位置是: `21 高级软卧 / 22 其他 / 23 软卧 / 24 软座 / 25 特等座 / 26 无座 /
   28 硬卧 / 29 硬座 / 30 二等座 / 31 一等座 / 32 商务座 / 33 动卧`。
   错位表现为"二等座"那一列永远是空的。已逐个车次核对:
   `G1 [30]=有 二等 / [31]=有 一等 / [32]=13 商务`, `K545 [29]=有 硬座 / [28]=无 硬卧`。
   另外出发/到达站改用 `[6]/[7]`(这一段实际上车的站), 而不是 `[4]/[5]`(始发/终点)。
3. **新版 prettytable 删掉了私有方法 `_set_field_names`**。现在用公开 API
   `field_names`(老版本仍用 `_set_field_names`)。

顺带: `verify=False` 改回校验证书(不再刷一屏 InsecureRequestWarning);
车站名不认识、网络不通、日期没放票这些情况给的都是人话, 不是堆栈。

## 镜像里已经有更好的版本

Debian U 盘系统(debian-usb-builder)里的 `train` 命令是**重写版**: 只用标准库
(不装 requests/docopt/prettytable/colorama), 支持 `明天/后天/+3` 日期写法、
`--json` 输出、车票类型筛选。参考:
https://github.com/yao1987825/debian-usb-builder
