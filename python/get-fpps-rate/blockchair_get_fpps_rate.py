#!/usr/bin/python
# test.py
import requests
import pymysql
import decimal

start = 1542348010
end = 1542348010
start_height = 557241
end_height = 557396

local_conn = pymysql.connect(host='localhost', port=3306, user='root', passwd='', db='blocks',
                             cursorclass=pymysql.cursors.DictCursor, charset='utf8')
local_cur = local_conn.cursor()

def get_data():
    api_url = "https://api.blockchair.com/bitcoin-cash/blocks?q=id(557241..557397)&limit=100&offset=100"
    headers = {'Test': "test"}
    blocks = []
    result = requests.get(url=api_url, headers=headers)
    try:
        result_json = result.json()
        blocks = result_json['data']
        print(len(blocks))
    except Exception as e:
        print(e)
    else:
        pass
    finally:
        pass
    return blocks

data = []
def insert(blocks):
    for row in blocks:
        try:
            local_cur.execute(
                            "INSERT INTO `bch_blocks` (`height`, `hash`, `fee_total`, `reward`)VALUES(%s, %s, %s, %s);",
                            (row['id'], row['hash'], row['fee_total'], row['reward']))
            local_conn.commit()
        except Exception as e:
            print(e)

def fetch():
    sql = "select * from bch_blocks where height >= " + str(start_height) + " and height <= " + str(end_height) +" order by reward desc;"
    print(sql)
    local_cur.execute(sql, ())
    for row in local_cur:
        data.append(row)

def calculate(count):
    optimize_number = round(count * 0.05)
    slice_array = data[optimize_number:count-optimize_number]
    print("去高去低之后的数量" + str(len(slice_array)))
    reward_fees = 0
    reward_block = 0
    for item in slice_array:
        reward_fees += item['fee_total']
        reward_block += item['reward']
    print(reward_block)
    print(reward_fees)
    print(reward_fees / reward_block)
    print(float_to_str(reward_fees / reward_block))


def float_to_str(f):
    """
    Convert the given float to a string,
    without resorting to scientific notation
    """
    ctx = decimal.Context()
    ctx.prec = 20
    d1 = ctx.create_decimal(repr(f))
    return format(d1, 'f')

if __name__ == '__main__':
    blocks = get_data()
    insert(blocks)
    fetch()
    print(len(data))
    calculate(len(data))