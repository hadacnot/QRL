# coding=utf-8
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php.
from pyqrllib.pyqrllib import hstr2bin

from qrl.core.AddressState import AddressState


def parse_hexblob(blob: str) -> bytes:
    """
    Binary conversions from hexstring are handled by bytes(hstr2bin()).
    :param blob:
    :return:
    """
    return bytes(hstr2bin(blob))


def parse_qaddress(qaddress: str) -> bytes:
    """
    Converts from a Qaddress to an Address.
    qaddress: 'Q' + hexstring representation of an XMSS tree's address
    address: binary representation, the Q is ignored when transforming from qaddress.
    :param qaddress:
    :return:
    """
    try:
        qaddress = parse_hexblob(qaddress[1:])
        if not AddressState.address_is_valid(qaddress):
            raise ValueError("Invalid Addresss ", qaddress)
    except Exception as e:
        raise ValueError("Failed To Decode Address", e)

    return qaddress
