# coding=utf-8
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php.
from unittest import TestCase

from mock import Mock, patch
from pyqrllib.pyqrllib import bin2hstr, hstr2bin

from qrl.core.misc import logger
from qrl.core.AddressState import AddressState
from qrl.daemon.walletd import WalletD
from qrl.generated import qrlwallet_pb2, qrl_pb2
from qrl.services.WalletAPIService import WalletAPIService
from tests.misc.helper import get_alice_xmss, get_bob_xmss, set_qrl_dir, replacement_getTime

logger.initialize_default()


@patch('qrl.core.misc.ntp.getTime', new=replacement_getTime)
class TestWalletAPI(TestCase):
    def __init__(self, *args, **kwargs):
        self.passphrase = '你好'
        self.qaddress = "Q010400ff39df1ba4d1d5b8753e6d04c51c34b95b01fc3650c10ca7b296a18bdc105412c59d0b3b"
        self.hex_seed = "0104008441d43524996f76236141d16b7b324323abf796e77ad" \
                        "7c874622a82f5744bb803f9b404d25733d0db82be7ac6f3c4cf"
        self.mnemonic = "absorb drank lute brick cure evil inept group grey " \
                        "breed hood reefy eager depict weed image law legacy " \
                        "jockey calm lover freeze fact lively wide dread spiral " \
                        "jaguar span rinse salty pulsar violet fare"
        super(TestWalletAPI, self).__init__(*args, **kwargs)

    def test_addNewAddress(self):
        with set_qrl_dir("wallet_ver1"):
            walletd = WalletD()
            service = WalletAPIService(walletd)
            resp = service.AddNewAddress(qrlwallet_pb2.AddNewAddressReq(), context=None)
            self.assertEqual(resp.code, 0)
            self.assertEqual(resp.address[0], 'Q')

    def test_addNewAddressWithSlaves(self):
        with set_qrl_dir("wallet_ver1"):
            walletd = WalletD()
            walletd._public_stub.PushTransaction = Mock(
                return_value=qrl_pb2.PushTransactionResp(error_code=qrl_pb2.PushTransactionResp.SUBMITTED))

            service = WalletAPIService(walletd)
            resp = service.AddNewAddressWithSlaves(qrlwallet_pb2.AddNewAddressWithSlavesReq(), context=None)
            self.assertEqual(resp.code, 0)
            self.assertEqual(resp.address[0], 'Q')

    def test_addAddressFromSeed(self):
        with set_qrl_dir("wallet_ver1"):
            qaddress = "Q010400ff39df1ba4d1d5b8753e6d04c51c34b95b01fc3650c10ca7b296a18bdc105412c59d0b3b"
            hex_seed = "0104008441d43524996f76236141d16b7b324323abf796e77ad7c874622a82f5744bb803f9b404d25733d0db82be7ac6f3c4cf"

            walletd = WalletD()
            service = WalletAPIService(walletd)
            resp = service.AddAddressFromSeed(qrlwallet_pb2.AddAddressFromSeedReq(seed=hex_seed), context=None)
            self.assertEqual(resp.code, 0)
            self.assertEqual(resp.address, qaddress)

    def test_addAddressFromSeed2(self):
        with set_qrl_dir("wallet_ver1"):
            walletd = WalletD()
            service = WalletAPIService(walletd)
            resp = service.AddAddressFromSeed(qrlwallet_pb2.AddAddressFromSeedReq(seed=self.mnemonic), context=None)
            self.assertEqual(resp.code, 0)
            self.assertEqual(resp.address, self.qaddress)

    def test_listAddresses(self):
        with set_qrl_dir("wallet_ver1"):
            walletd = WalletD()
            service = WalletAPIService(walletd)

            resp = service.AddNewAddress(qrlwallet_pb2.AddNewAddressReq(), context=None)
            address = resp.address

            resp = service.ListAddresses(qrlwallet_pb2.ListAddressesReq(), context=None)
            self.assertEqual(resp.addresses[0], address)

    def test_removeAddress(self):
        with set_qrl_dir("wallet_ver1"):
            walletd = WalletD()
            service = WalletAPIService(walletd)

            resp = service.AddNewAddress(qrlwallet_pb2.AddNewAddressReq(), context=None)
            address = resp.address

            resp = service.ListAddresses(qrlwallet_pb2.ListAddressesReq(), context=None)
            self.assertEqual(len(resp.addresses), 1)

            resp = service.RemoveAddress(qrlwallet_pb2.RemoveAddressReq(address=address), context=None)
            self.assertEqual(resp.code, 0)

            resp = service.ListAddresses(qrlwallet_pb2.ListAddressesReq(), context=None)
            self.assertEqual(len(resp.addresses), 0)

    def test_validateAddress(self):
        with set_qrl_dir("wallet_ver1"):
            walletd = WalletD()
            service = WalletAPIService(walletd)

            qaddress = "Q010400ff39df1ba4d1d5b8753e6d04c51c34b95b01fc3650c10ca7b296a18bdc105412c59d0b3b"
            resp = service.ValidateAddress(qrlwallet_pb2.ValidateAddressReq(address=qaddress), context=None)
            self.assertTrue(resp.valid)

            qaddress = "Q010400ff39df1ba4d1d5b8753e6d04c51c34b95b01fc3650c10ca7b296a18bdc105412c59d0b00"
            resp = service.ValidateAddress(qrlwallet_pb2.ValidateAddressReq(address=qaddress), context=None)
            self.assertFalse(resp.valid)

    def test_getRecoverySeeds(self):
        with set_qrl_dir("wallet_ver1"):
            walletd = WalletD()
            service = WalletAPIService(walletd)

            service.AddAddressFromSeed(qrlwallet_pb2.AddAddressFromSeedReq(seed=self.mnemonic), context=None)
            resp = service.GetRecoverySeeds(qrlwallet_pb2.GetRecoverySeedsReq(address=self.qaddress), context=None)

            self.assertEqual(resp.hexseed, self.hex_seed)
            self.assertEqual(resp.mnemonic, self.mnemonic)

    def test_getWalletInfo(self):
        with set_qrl_dir("wallet_ver1"):
            walletd = WalletD()
            service = WalletAPIService(walletd)

            resp = service.GetWalletInfo(qrlwallet_pb2.GetWalletInfoReq(), context=None)

            self.assertEqual(resp.version, 1)
            self.assertEqual(resp.address_count, 0)
            self.assertFalse(resp.is_encrypted)

    def test_relayTransferTxn(self):
        with set_qrl_dir("wallet_ver1"):
            walletd = WalletD()
            service = WalletAPIService(walletd)

            resp = service.AddNewAddress(qrlwallet_pb2.AddNewAddressReq(), context=None)
            qaddress = resp.address

            alice_xmss = get_alice_xmss(4)
            bob_xmss = get_bob_xmss(4)
            qaddresses_to = [alice_xmss.qaddress, bob_xmss.qaddress]
            amounts = [1000000000, 1000000000]

            walletd._public_stub.PushTransaction = Mock(
                return_value=qrl_pb2.PushTransactionResp(error_code=qrl_pb2.PushTransactionResp.SUBMITTED))

            resp = service.RelayTransferTxn(qrlwallet_pb2.RelayTransferTxnReq(addresses_to=qaddresses_to,
                                                                              amounts=amounts,
                                                                              fee=100000000,
                                                                              master_address=None,
                                                                              signer_address=qaddress,
                                                                              ots_index=0), context=None)

            self.assertEqual(resp.code, 0)
            self.assertIsNotNone(resp.tx)

    def test_relayTransferTxnBySlave(self):
        with set_qrl_dir("wallet_ver1"):
            walletd = WalletD()
            walletd._public_stub.PushTransaction = Mock(
                return_value=qrl_pb2.PushTransactionResp(error_code=qrl_pb2.PushTransactionResp.SUBMITTED))

            service = WalletAPIService(walletd)

            resp = service.AddNewAddressWithSlaves(qrlwallet_pb2.AddNewAddressWithSlavesReq(), context=None)
            qaddress = resp.address
            addr_state = AddressState.get_default(walletd.qaddress_to_address(qaddress))
            slaves = walletd.get_slave_list(qaddress)

            addr_state.add_slave_pks_access_type(bytes(hstr2bin(slaves[0][0].pk)), 0)
            walletd._public_stub.GetAddressState = Mock(
                return_value=qrl_pb2.GetAddressStateResp(state=addr_state.pbdata))

            alice_xmss = get_alice_xmss(4)
            bob_xmss = get_bob_xmss(4)
            qaddresses_to = [alice_xmss.qaddress, bob_xmss.qaddress]
            amounts = [1000000000, 1000000000]

            resp = service.RelayTransferTxnBySlave(
                qrlwallet_pb2.RelayTransferTxnBySlaveReq(addresses_to=qaddresses_to,
                                                         amounts=amounts,
                                                         fee=100000000,
                                                         master_address=qaddress), context=None)

            self.assertEqual(resp.code, 0)
            self.assertIsNotNone(resp.tx)

    def test_relayMessageTxn(self):
        with set_qrl_dir("wallet_ver1"):
            walletd = WalletD()
            service = WalletAPIService(walletd)

            resp = service.AddNewAddress(qrlwallet_pb2.AddNewAddressReq(), context=None)
            qaddress = resp.address

            walletd._public_stub.PushTransaction = Mock(
                return_value=qrl_pb2.PushTransactionResp(error_code=qrl_pb2.PushTransactionResp.SUBMITTED))

            resp = service.RelayMessageTxn(qrlwallet_pb2.RelayMessageTxnReq(message=b'Hello QRL!',
                                                                            fee=100000000,
                                                                            master_address=None,
                                                                            signer_address=qaddress,
                                                                            ots_index=0), context=None)

            self.assertEqual(resp.code, 0)
            self.assertIsNotNone(resp.tx)

    def test_relayMessageTxnBySlave(self):
        with set_qrl_dir("wallet_ver1"):
            walletd = WalletD()
            walletd._public_stub.PushTransaction = Mock(
                return_value=qrl_pb2.PushTransactionResp(error_code=qrl_pb2.PushTransactionResp.SUBMITTED))

            service = WalletAPIService(walletd)

            resp = service.AddNewAddressWithSlaves(qrlwallet_pb2.AddNewAddressWithSlavesReq(), context=None)
            qaddress = resp.address
            addr_state = AddressState.get_default(walletd.qaddress_to_address(qaddress))
            slaves = walletd.get_slave_list(qaddress)

            addr_state.add_slave_pks_access_type(bytes(hstr2bin(slaves[0][0].pk)), 0)
            walletd._public_stub.GetAddressState = Mock(
                return_value=qrl_pb2.GetAddressStateResp(state=addr_state.pbdata))

            resp = service.RelayMessageTxnBySlave(
                qrlwallet_pb2.RelayMessageTxnReq(message=b'Hello QRL!',
                                                 fee=100000000,
                                                 master_address=qaddress), context=None)

            self.assertEqual(resp.code, 0)
            self.assertIsNotNone(resp.tx)

    def test_relayTokenTxn(self):
        with set_qrl_dir("wallet_ver1"):
            walletd = WalletD()
            service = WalletAPIService(walletd)

            resp = service.AddNewAddress(qrlwallet_pb2.AddNewAddressReq(), context=None)
            qaddress = resp.address

            alice_xmss = get_alice_xmss(4)
            bob_xmss = get_bob_xmss(4)
            qaddresses = [alice_xmss.qaddress, bob_xmss.qaddress]
            amounts = [1000000000, 1000000000]

            walletd._public_stub.PushTransaction = Mock(
                return_value=qrl_pb2.PushTransactionResp(error_code=qrl_pb2.PushTransactionResp.SUBMITTED))

            resp = service.RelayTokenTxn(qrlwallet_pb2.RelayTokenTxnReq(symbol=b'QRL',
                                                                        name=b'Quantum Resistant Ledger',
                                                                        owner=alice_xmss.qaddress,
                                                                        decimals=5,
                                                                        addresses=qaddresses,
                                                                        amounts=amounts,
                                                                        fee=100000000,
                                                                        master_address=None,
                                                                        signer_address=qaddress,
                                                                        ots_index=0), context=None)

            self.assertEqual(resp.code, 0)
            self.assertIsNotNone(resp.tx)

    def test_relayTokenTxnBySlave(self):
        with set_qrl_dir("wallet_ver1"):
            walletd = WalletD()
            walletd._public_stub.PushTransaction = Mock(
                return_value=qrl_pb2.PushTransactionResp(error_code=qrl_pb2.PushTransactionResp.SUBMITTED))

            service = WalletAPIService(walletd)

            resp = service.AddNewAddressWithSlaves(qrlwallet_pb2.AddNewAddressWithSlavesReq(), context=None)
            qaddress = resp.address
            addr_state = AddressState.get_default(walletd.qaddress_to_address(qaddress))
            slaves = walletd.get_slave_list(qaddress)

            addr_state.add_slave_pks_access_type(bytes(hstr2bin(slaves[0][0].pk)), 0)
            walletd._public_stub.GetAddressState = Mock(
                return_value=qrl_pb2.GetAddressStateResp(state=addr_state.pbdata))

            alice_xmss = get_alice_xmss(4)
            bob_xmss = get_bob_xmss(4)
            qaddresses = [alice_xmss.qaddress, bob_xmss.qaddress]
            amounts = [1000000000, 1000000000]

            resp = service.RelayTokenTxnBySlave(
                qrlwallet_pb2.RelayTokenTxnBySlaveReq(symbol=b'QRL',
                                                      name=b'Quantum Resistant Ledger',
                                                      owner=alice_xmss.qaddress,
                                                      decimals=5,
                                                      addresses=qaddresses,
                                                      amounts=amounts,
                                                      fee=100000000,
                                                      master_address=qaddress), context=None)

            self.assertEqual(resp.code, 0)
            self.assertIsNotNone(resp.tx)

    def test_relayTransferTokenTxn(self):
        with set_qrl_dir("wallet_ver1"):
            walletd = WalletD()
            service = WalletAPIService(walletd)

            resp = service.AddNewAddress(qrlwallet_pb2.AddNewAddressReq(), context=None)
            qaddress = resp.address

            alice_xmss = get_alice_xmss(4)
            bob_xmss = get_bob_xmss(4)
            qaddresses_to = [alice_xmss.qaddress, bob_xmss.qaddress]
            amounts = [1000000000, 1000000000]

            walletd._public_stub.PushTransaction = Mock(
                return_value=qrl_pb2.PushTransactionResp(error_code=qrl_pb2.PushTransactionResp.SUBMITTED))

            resp = service.RelayTransferTokenTxn(qrlwallet_pb2.RelayTransferTokenTxnReq(addresses_to=qaddresses_to,
                                                                                        amounts=amounts,
                                                                                        token_txhash='',
                                                                                        fee=100000000,
                                                                                        master_address=None,
                                                                                        signer_address=qaddress,
                                                                                        ots_index=0), context=None)

            self.assertEqual(resp.code, 0)
            self.assertIsNotNone(resp.tx)

    def test_relayTransferTokenTxnBySlave(self):
        with set_qrl_dir("wallet_ver1"):
            walletd = WalletD()
            walletd._public_stub.PushTransaction = Mock(
                return_value=qrl_pb2.PushTransactionResp(error_code=qrl_pb2.PushTransactionResp.SUBMITTED))

            service = WalletAPIService(walletd)

            resp = service.AddNewAddressWithSlaves(qrlwallet_pb2.AddNewAddressWithSlavesReq(), context=None)
            qaddress = resp.address
            addr_state = AddressState.get_default(walletd.qaddress_to_address(qaddress))
            slaves = walletd.get_slave_list(qaddress)

            addr_state.add_slave_pks_access_type(bytes(hstr2bin(slaves[0][0].pk)), 0)
            walletd._public_stub.GetAddressState = Mock(
                return_value=qrl_pb2.GetAddressStateResp(state=addr_state.pbdata))

            alice_xmss = get_alice_xmss(4)
            bob_xmss = get_bob_xmss(4)
            qaddresses_to = [alice_xmss.qaddress, bob_xmss.qaddress]
            amounts = [1000000000, 1000000000]

            resp = service.RelayTransferTokenTxnBySlave(
                qrlwallet_pb2.RelayTransferTokenTxnBySlaveReq(addresses_to=qaddresses_to,
                                                              amounts=amounts,
                                                              token_txhash='',
                                                              fee=100000000,
                                                              master_address=qaddress), context=None)

            self.assertEqual(resp.code, 0)
            self.assertIsNotNone(resp.tx)

    def test_relaySlaveTxn(self):
        with set_qrl_dir("wallet_ver1"):
            walletd = WalletD()
            service = WalletAPIService(walletd)

            resp = service.AddNewAddress(qrlwallet_pb2.AddNewAddressReq(), context=None)
            qaddress = resp.address

            alice_xmss = get_alice_xmss(4)
            slave_pks = [alice_xmss.pk]
            access_types = [0]

            walletd._public_stub.PushTransaction = Mock(
                return_value=qrl_pb2.PushTransactionResp(error_code=qrl_pb2.PushTransactionResp.SUBMITTED))

            resp = service.RelaySlaveTxn(qrlwallet_pb2.RelaySlaveTxnReq(slave_pks=slave_pks,
                                                                        access_types=access_types,
                                                                        fee=100000000,
                                                                        master_address=None,
                                                                        signer_address=qaddress,
                                                                        ots_index=0), context=None)

            self.assertEqual(resp.code, 0)
            self.assertIsNotNone(resp.tx)

    def test_relaySlaveTxnBySlave(self):
        with set_qrl_dir("wallet_ver1"):
            walletd = WalletD()
            walletd._public_stub.PushTransaction = Mock(
                return_value=qrl_pb2.PushTransactionResp(error_code=qrl_pb2.PushTransactionResp.SUBMITTED))

            service = WalletAPIService(walletd)

            resp = service.AddNewAddressWithSlaves(qrlwallet_pb2.AddNewAddressWithSlavesReq(), context=None)
            qaddress = resp.address
            addr_state = AddressState.get_default(walletd.qaddress_to_address(qaddress))
            slaves = walletd.get_slave_list(qaddress)

            addr_state.add_slave_pks_access_type(bytes(hstr2bin(slaves[0][0].pk)), 0)
            walletd._public_stub.GetAddressState = Mock(
                return_value=qrl_pb2.GetAddressStateResp(state=addr_state.pbdata))

            alice_xmss = get_alice_xmss(4)
            slave_pks = [alice_xmss.pk]
            access_types = [0]

            resp = service.RelaySlaveTxnBySlave(
                qrlwallet_pb2.RelaySlaveTxnBySlaveReq(slave_pks=slave_pks,
                                                      access_types=access_types,
                                                      fee=100000000,
                                                      master_address=qaddress), context=None)

            self.assertEqual(resp.code, 0)
            self.assertIsNotNone(resp.tx)

    def test_encryptWallet(self):
        with set_qrl_dir("wallet_ver1"):
            walletd = WalletD()
            service = WalletAPIService(walletd)

            service.AddNewAddress(qrlwallet_pb2.AddNewAddressReq(), context=None)

            resp = service.EncryptWallet(qrlwallet_pb2.EncryptWalletReq(), context=None)
            self.assertEqual(resp.code, 1)

            resp = service.EncryptWallet(qrlwallet_pb2.EncryptWalletReq(passphrase=self.passphrase), context=None)
            self.assertEqual(resp.code, 0)

            resp = service.EncryptWallet(qrlwallet_pb2.EncryptWalletReq(passphrase=self.passphrase), context=None)
            self.assertEqual(resp.code, 1)

    def test_lockWallet(self):
        with set_qrl_dir("wallet_ver1"):
            walletd = WalletD()
            service = WalletAPIService(walletd)

            service.AddNewAddress(qrlwallet_pb2.AddNewAddressReq(), context=None)

            resp = service.ListAddresses(qrlwallet_pb2.ListAddressesReq(), context=None)
            self.assertEqual(resp.code, 0)
            self.assertEqual(len(resp.addresses), 1)

            resp = service.EncryptWallet(qrlwallet_pb2.EncryptWalletReq(passphrase=self.passphrase), context=None)
            self.assertEqual(resp.code, 0)

            resp = service.ListAddresses(qrlwallet_pb2.ListAddressesReq(), context=None)
            self.assertEqual(resp.code, 1)

            resp = service.UnlockWallet(qrlwallet_pb2.UnlockWalletReq(passphrase=self.passphrase), context=None)
            self.assertEqual(resp.code, 0)

            resp = service.ListAddresses(qrlwallet_pb2.ListAddressesReq(), context=None)
            self.assertEqual(resp.code, 0)

            resp = service.LockWallet(qrlwallet_pb2.LockWalletReq(), context=None)
            self.assertEqual(resp.code, 0)

            resp = service.ListAddresses(qrlwallet_pb2.ListAddressesReq(), context=None)
            self.assertEqual(resp.code, 1)

    def test_unlockWallet(self):
        with set_qrl_dir("wallet_ver1"):
            walletd = WalletD()
            service = WalletAPIService(walletd)

            service.AddNewAddress(qrlwallet_pb2.AddNewAddressReq(), context=None)

            resp = service.ListAddresses(qrlwallet_pb2.ListAddressesReq(), context=None)
            self.assertEqual(resp.code, 0)
            self.assertEqual(len(resp.addresses), 1)

            resp = service.EncryptWallet(qrlwallet_pb2.EncryptWalletReq(passphrase=self.passphrase), context=None)
            self.assertEqual(resp.code, 0)

            resp = service.ListAddresses(qrlwallet_pb2.ListAddressesReq(), context=None)
            self.assertEqual(resp.code, 1)

            resp = service.UnlockWallet(qrlwallet_pb2.UnlockWalletReq(passphrase=self.passphrase), context=None)
            self.assertEqual(resp.code, 0)

            resp = service.ListAddresses(qrlwallet_pb2.ListAddressesReq(), context=None)
            self.assertEqual(resp.code, 0)

            resp = service.LockWallet(qrlwallet_pb2.LockWalletReq(), context=None)
            self.assertEqual(resp.code, 0)

            resp = service.ListAddresses(qrlwallet_pb2.ListAddressesReq(), context=None)
            self.assertEqual(resp.code, 1)

            resp = service.UnlockWallet(qrlwallet_pb2.UnlockWalletReq(), context=None)
            self.assertEqual(resp.code, 1)

            resp = service.UnlockWallet(qrlwallet_pb2.UnlockWalletReq(passphrase="wrong"), context=None)
            self.assertEqual(resp.code, 1)

    def test_changePassphrase(self):
        with set_qrl_dir("wallet_ver1"):
            walletd = WalletD()
            service = WalletAPIService(walletd)

            service.AddNewAddress(qrlwallet_pb2.AddNewAddressReq(), context=None)

            resp = service.ListAddresses(qrlwallet_pb2.ListAddressesReq(), context=None)
            self.assertEqual(resp.code, 0)
            self.assertEqual(len(resp.addresses), 1)

            resp = service.EncryptWallet(qrlwallet_pb2.EncryptWalletReq(passphrase=self.passphrase), context=None)
            self.assertEqual(resp.code, 0)

            resp = service.ListAddresses(qrlwallet_pb2.ListAddressesReq(), context=None)
            self.assertEqual(resp.code, 1)

            resp = service.UnlockWallet(qrlwallet_pb2.UnlockWalletReq(passphrase=self.passphrase), context=None)
            self.assertEqual(resp.code, 0)

            resp = service.ListAddresses(qrlwallet_pb2.ListAddressesReq(), context=None)
            self.assertEqual(resp.code, 0)

            resp = service.LockWallet(qrlwallet_pb2.LockWalletReq(), context=None)
            self.assertEqual(resp.code, 0)

            new_passphrase = "Hello World"
            resp = service.ChangePassphrase(
                qrlwallet_pb2.ChangePassphraseReq(oldPassphrase=self.passphrase,
                                                  newPassphrase=new_passphrase), context=None)
            self.assertEqual(resp.code, 0)

            resp = service.UnlockWallet(qrlwallet_pb2.UnlockWalletReq(passphrase=self.passphrase), context=None)
            self.assertEqual(resp.code, 1)

            resp = service.UnlockWallet(qrlwallet_pb2.UnlockWalletReq(passphrase=new_passphrase), context=None)
            self.assertEqual(resp.code, 0)

    def test_getTransactionsByAddress(self):
        with set_qrl_dir("wallet_ver1"):
            walletd = WalletD()
            service = WalletAPIService(walletd)

            walletd._public_stub.GetTransactionsByAddress = Mock(
                return_value=qrl_pb2.GetTransactionsByAddressResp(mini_transactions=[],
                                                                  balance=0))

            resp = service.GetTransactionsByAddress(
                qrlwallet_pb2.TransactionsByAddressReq(address=get_alice_xmss(4).qaddress), context=None)

            self.assertEqual(resp.code, 0)
            self.assertEqual(len(resp.mini_transactions), 0)
            self.assertEqual(resp.balance, 0)

    def test_getTransaction(self):
        with set_qrl_dir("wallet_ver1"):
            walletd = WalletD()
            service = WalletAPIService(walletd)

            tx = qrl_pb2.Transaction()
            tx.fee = 10
            tx.transaction_hash = b'1234'
            tx.message.message_hash = b'hello'
            pk = '01020016ecb9f39b9f4275d5a49e232346a15ae2fa8c50a2927daeac189b8c5f2d1' \
                 '8bc4e3983bd564298c49ae2e7fa6e28d4b954d8cd59398f1225b08d6144854aee0e'
            tx.public_key = bytes(hstr2bin(pk))

            walletd._public_stub.GetTransaction = Mock(
                return_value=qrl_pb2.GetTransactionResp(tx=tx, confirmations=10))

            resp = service.GetTransaction(qrlwallet_pb2.TransactionReq(tx_hash=tx.transaction_hash), context=None)

            self.assertEqual(resp.code, 0)
            self.assertIsNotNone(resp.tx)
            self.assertEqual(bin2hstr(tx.transaction_hash), resp.tx.transaction_hash)

    def test_getBalance(self):
        with set_qrl_dir("wallet_ver1"):
            walletd = WalletD()
            service = WalletAPIService(walletd)

            walletd._public_stub.GetBalance = Mock(
                return_value=qrl_pb2.GetBalanceResp(balance=1000))

            resp = service.GetBalance(qrlwallet_pb2.BalanceReq(address=self.qaddress), context=None)

            self.assertEqual(resp.code, 0)
            self.assertEqual(resp.balance, 1000)

    def test_getOTS(self):
        with set_qrl_dir("wallet_ver1"):
            walletd = WalletD()
            service = WalletAPIService(walletd)

            walletd._public_stub.GetOTS = Mock(
                return_value=qrl_pb2.GetOTSResp(ots_bitfield=[b'\x00'] * 10, next_unused_ots_index=1))

            resp = service.GetOTS(qrlwallet_pb2.OTSReq(address=self.qaddress), context=None)

            self.assertEqual(resp.code, 0)
            self.assertEqual(resp.ots_bitfield, [b'\x00'] * 10)
            self.assertEqual(resp.next_unused_ots_index, 1)

    def test_getHeight(self):
        with set_qrl_dir("wallet_ver1"):
            walletd = WalletD()
            service = WalletAPIService(walletd)

            walletd._public_stub.GetHeight = Mock(
                return_value=qrl_pb2.GetHeightResp(height=1001))

            resp = service.GetHeight(qrlwallet_pb2.HeightReq(), context=None)

            self.assertEqual(resp.code, 0)
            self.assertEqual(resp.height, 1001)

    def test_getBlock(self):
        with set_qrl_dir("wallet_ver1"):
            walletd = WalletD()
            service = WalletAPIService(walletd)

            block = qrl_pb2.Block()
            block.header.hash_header = b'001122'
            block.header.block_number = 1

            walletd._public_stub.GetBlock = Mock(
                return_value=qrl_pb2.GetBlockResp(block=block))

            resp = service.GetBlock(qrlwallet_pb2.BlockReq(header_hash=b'001122'), context=None)

            self.assertEqual(resp.code, 0)
            self.assertEqual(resp.block.header.hash_header, bin2hstr(block.header.hash_header))
            self.assertEqual(resp.block.header.block_number, block.header.block_number)

    def test_getBlockByNumber(self):
        with set_qrl_dir("wallet_ver1"):
            walletd = WalletD()
            service = WalletAPIService(walletd)

            block = qrl_pb2.Block()
            block.header.hash_header = b'001122'
            block.header.block_number = 1

            walletd._public_stub.GetBlockByNumber = Mock(
                return_value=qrl_pb2.GetBlockResp(block=block))

            resp = service.GetBlockByNumber(qrlwallet_pb2.BlockByNumberReq(block_number=1), context=None)

            self.assertEqual(resp.code, 0)
            self.assertEqual(resp.block.header.hash_header, bin2hstr(block.header.hash_header))
            self.assertEqual(resp.block.header.block_number, block.header.block_number)

    def test_getAddressFromPK(self):
        with set_qrl_dir("wallet_ver1"):
            walletd = WalletD()
            service = WalletAPIService(walletd)

            pk = '01020016ecb9f39b9f4275d5a49e232346a15ae2fa8c50a2927daeac189b8c5f2d1' \
                 '8bc4e3983bd564298c49ae2e7fa6e28d4b954d8cd59398f1225b08d6144854aee0e'

            resp = service.GetAddressFromPK(qrlwallet_pb2.AddressFromPKReq(pk=pk), context=None)

            self.assertEqual(resp.code, 0)
            self.assertEqual(resp.address,
                             'Q010200670246b0026436b717f199e3ec5320ba6ab61d5eddff811ac199a9e9b871d3280178b343')
