# coding: utf-8

"""火车票查询CLI

Usage:
    train-tickets [-gdtkz] <from> <to> [<date>]

Options:
    -h,--help   显示帮助菜单
    -g          高铁
    -d          动车
    -t          特快
    -k          快速
    -z          直达

Example:
    train-tickets 北京 上海 2016-10-10
    train-tickets -dg 成都 南京 2016-10-10
"""

from docopt import docopt
from stations import stations
import requests
from trainsCollection import TrainsCollection
from datetime import datetime

# 12306 的余票接口必须"先拿会话 Cookie 再查", 直接 GET 接口只会拿到一个
# HTML 反爬页面, 于是 requests.json() 直接抛 JSONDecodeError(原代码的老毛病)。
# 正确姿势:
#   1) 先 GET 余票首页(init), 让服务端下发 cookie;
#   2) 再带 Referer / X-Requested-With / User-Agent 去查 query 接口。
# 另外 verify=False 会刷一屏 InsecureRequestWarning, 这里改回校验证书。
UA = ('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
      'Chrome/124.0 Safari/537.36')
INIT_URL = 'https://kyfw.12306.cn/otn/leftTicket/init?linktypeid=dc'
QUERY_URL = 'https://kyfw.12306.cn/otn/leftTicket/query'


def cli():
    ''' command-line interface'''
    arguments = docopt(__doc__)
    date = arguments.get('<date>') or datetime.now().strftime('%Y-%m-%d')
    from_station = stations.get(arguments.get('<from>'))
    to_station = stations.get(arguments.get('<to>'))
    if not from_station or not to_station:
        raise SystemExit('车站名不认识: %s -> %s (用 --stations 关键字 可以查有哪些站)' % (
            arguments.get('<from>'), arguments.get('<to>')))

    session = requests.Session()
    session.headers.update({'User-Agent': UA})
    try:
        session.get(INIT_URL, timeout=20)
    except requests.RequestException as exc:
        raise SystemExit('连不上 12306: %s' % exc)

    params = {
        'leftTicketDTO.train_date': date,
        'leftTicketDTO.from_station': from_station,
        'leftTicketDTO.to_station': to_station,
        'purpose_codes': 'ADULT',
    }
    headers = {
        'Referer': INIT_URL,
        'X-Requested-With': 'XMLHttpRequest',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
    }
    try:
        res = session.get(QUERY_URL, params=params, headers=headers, timeout=25)
    except requests.RequestException as exc:
        raise SystemExit('查询失败: %s' % exc)

    try:
        body = res.json()
    except ValueError:
        raise SystemExit('12306 没返回 JSON(被反爬拦截了)。稍后再试, 或换个网络')

    if body.get('httpstatus') != 200 or body.get('status') is False:
        raise SystemExit('12306 说不行: %s' % (body.get('messages') or ['未知错误'])[0])

    trains = (body.get('data') or {}).get('result') or []
    if not trains:
        raise SystemExit('%s %s -> %s 没有车次(可能没票、日期没放票, 或车次太少)' % (
            date, arguments.get('<from>'), arguments.get('<to>')))

    options = ''.join([
        k for k,v in arguments.items() if v == True
    ])
    TrainsCollection(trains, options).pretty_print()

if __name__ == '__main__':
    cli()
