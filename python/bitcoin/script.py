#!/usr/bin/env python3
import decimal
import hashlib
from binascii import hexlify, unhexlify
from bitcoinrpc.authproxy import AuthServiceProxy   # PyPi: python-bitcoinrpc
from bitcoin.transaction import serialize   # PyPi: bitcoin
from bitcoin.main import b58check_to_hex, hex_to_b58check
from pprint import pprint

# testnet5
p = AuthServiceProxy("http://%s:%s@127.0.0.1:18554" % ('rpc', '123456'))

address1 = 'mfnCSPtgXEGdt8mJPguvgmhiswfgkqEjAx'
address2 = 'n3xBmjjCNGDkkt5fdCdV7G7pdx1zxUJXAo'
address3 = 'mnFMaBdF6YdB1Y6AKtXqfS3Z9U26iHPP1E'
pubkey1 = p.validateaddress(address1)['pubkey']
pubkey2 = p.validateaddress(address2)['pubkey']
pubkey3 = p.validateaddress(address3)['pubkey']

multisigaddress = p.createmultisig(2, [pubkey1, pubkey2, pubkey3])['address']
redeemscript = p.createmultisig(2, [pubkey1, pubkey2, pubkey3])['redeemScript']

p.addmultisigaddress(2, [pubkey1, pubkey2, pubkey3])
p.addwitnessaddress(multisigaddress)

print('multisigaddress:', multisigaddress, '\nredeemscript:', redeemscript)

def bytes_to_hex_str(byte_str):
    return hexlify(byte_str).decode('ascii')

def hex_str_to_bytes(hex_str):
    return unhexlify(hex_str.encode('ascii'))

def ripemd160(s):
    return hashlib.new('ripemd160', s).digest()

def sha256(s):
    return hashlib.new('sha256', s).digest()

def mk_p2wsh_script():
    """生成p2wsh的脚本"""
    scripthash = bytes_to_hex_str(sha256(hex_str_to_bytes(redeemscript)))
    pkscript = "0020" + scripthash
    return pkscript

def mk_p2sh_script(addr):
    print('b58check_to_hex(addr)', b58check_to_hex(addr))
    return 'a914' + b58check_to_hex(addr) + '87'

def mk_p2wpkh_script(addr):
    return '0014' + b58check_to_hex(addr)

def mk_p2pkh_script(addr):
    return '76a914' + b58check_to_hex(addr) + '88ac'

def mk_p2wpkh_in_p2sh_script(addr):
    # p2wpkh
    pubkey_20_byte_hash = '0014' + b58check_to_hex(addr)
    # p2sh
    p2sh_script_hash256 = bytes_to_hex_str(
        sha256(hex_str_to_bytes(pubkey_20_byte_hash))
    )
    p2sh_script_hash160 = bytes_to_hex_str(
        ripemd160(hex_str_to_bytes(p2sh_script_hash256))
    )
    print('p2sh-p2wpkh addr>>', hex_to_b58check(p2sh_script_hash160, 196))  # 5
    schash = 'a914' + p2sh_script_hash160 + '87'
    return schash


def mk_p2wsh_in_p2sh_script():
    # p2wsh
    scripthash = bytes_to_hex_str(sha256(hex_str_to_bytes(redeemscript)))
    pkscript = "0020" + scripthash
    # p2sh
    p2sh_script_hash256 = bytes_to_hex_str(sha256(hex_str_to_bytes(pkscript)))
    p2sh_script_hash160 = bytes_to_hex_str(
        ripemd160(hex_str_to_bytes(p2sh_script_hash256))
    )
    print('hex_to_b58check', hex_to_b58check(p2sh_script_hash160, 196))     # 5
    schash = 'a914' + p2sh_script_hash160 + '87'
    return schash

def select_utxo(amount):
    """
    :param amount: 总额(加上手续费)
    :return: [交易的输入，所有输入的总额]
    """
    ins = []
    ins_amount = 0
    
    # listunspent = p.listunspent()

    listunspent = [
        {
            'txid': '224f3c21169e6eeeb7154583dcccf6ffb6ebd7bc73bb5976b6568c82fa7f16bf',
            'vout': 0, 'amount': 0.0891, 'spendable': True
        }
    ]

    for unspent in listunspent:
        if not unspent['spendable']:
            continue

        if ins_amount < amount:
            txin = {
                'script': '',
                'outpoint': {
                    'index': unspent['vout'],
                    'hash': unspent['txid']
                },
                'sequence': 4294967295
            }
            ins.append(txin)
            ins_amount += unspent['amount']
        else:
            break

    if ins_amount <= amount:
        return 0

    return [ins, ins_amount]

def create_tx(send_list, my_fee, change_addr):
    """
    :param send_list: [{'address':xxx, 'value':0},...]，输出
    :param my_fee: 单位BTC
    :param change_addr: 找零地址
    :return: txid
    """
    # tx
    tx = {'version': 1, 'ins': [], 'outs': [], 'locktime': 0}

    # out
    out_value_sum = 0
    for out in send_list:
        out_script = mk_p2pkh_script(out['address'])
        if out['type'] == 'p2wsh':
            out_script = mk_p2wsh_script()
        elif out['type'] == 'p2sh':
            out_script = mk_p2sh_script(out['address'])
        elif out['type'] == 'p2wpkh':
            out_script = mk_p2wpkh_script(out['address'])
        elif out['type'] == 'p2pkh':
            out_script = mk_p2pkh_script(out['address'])
        elif out['type'] == 'p2sh-p2wpkh':
            out_script = mk_p2wpkh_in_p2sh_script(out['address'])
        elif out['type'] == 'p2sh-p2wsh':
            out_script = mk_p2wsh_in_p2sh_script()
        txout = {
            'value': int(decimal.Decimal(out['value'] * 10**8)),
            'script': out_script
        }
        tx['outs'].append(txout)
        out_value_sum += out['value']

    # in
    select = select_utxo(round(out_value_sum + my_fee, 8))
    # print(select)
    if select:
        ins = select[0]
        ins_value_sum = select[1]
    else:
        return '余额不足'

    tx['ins'] = ins

    # change to myself
    change_value = float(ins_value_sum) - out_value_sum - my_fee
    # print(change_value, ins_value_sum, out_value_sum, my_fee)

    if change_addr:
        txout = {
            'value': int(decimal.Decimal(change_value * 10**8)),
            'script': mk_p2pkh_script(change_addr)
        }
        tx['outs'].append(txout)

    print('tx:→', tx)

    # serialize
    raw_tx = serialize(tx)

    # sign
    sign_raw_tx = p.signrawtransaction(raw_tx)

    pprint(p.decoderawtransaction(sign_raw_tx['hex']))

    return p.sendrawtransaction(sign_raw_tx['hex'], False)


if __name__ == '__main__':

    change_address = ''
    fee = 0.00003

    pay_to = [
        {'address': 'mfnCSPtgXEGdt8mJPguvgmhiswfgkqEjAx', 'value': 0.01, 'type': 'p2wsh'},
        {'address': '2N71hQLY9GGbTry3WsLscBnK3jtYVyzLyeM', 'value': 0.01, 'type': 'p2sh'},
        {'address': 'mfnCSPtgXEGdt8mJPguvgmhiswfgkqEjAx', 'value': 0.01, 'type': 'p2wpkh'},
        {'address': 'mfnCSPtgXEGdt8mJPguvgmhiswfgkqEjAx', 'value': 0.01, 'type': 'p2pkh'},
        {'address': 'mjLTwdup9YH9Yq1F3X2mLezEeypLVN6qiW', 'value': 0.01, 'type': 'p2sh-p2wpkh'},
        {'address': 'mfnCSPtgXEGdt8mJPguvgmhiswfgkqEjAx', 'value': 0.01, 'type': 'p2sh-p2wsh'},
    ]

    txid = create_tx(pay_to, fee, change_address)
    print('txid:→', txid)

# txid:→ 6fcafce56db51b2863e27a3786132e3f6ee24686f29d4c9a0752d936a548585a