from model.key import *
from util.logger import get_logger
from util.keys import replace_nonprintable


class KeyExtractor:
    keys = {}
    logger = get_logger(__name__)

    @staticmethod
    def process_transactions(transactions):
        for tx in transactions:
            KeyExtractor._merge_results(
                KeyExtractor._get_rw_keys_for_transaction(tx))
        return KeyExtractor.keys

    @staticmethod
    def _merge_results(rw_sets):
        for key_change in rw_sets:
            k = key_change.rwset["key"]
            if k not in KeyExtractor.keys:
                KeyExtractor.keys[k] = Key(k)
                KeyExtractor.logger.debug(
                    f"New key: {replace_nonprintable(k)}, namespace: {key_change.namespace}")
            KeyExtractor.keys[k].history.append(key_change)

    @staticmethod
    def _get_rw_keys_for_transaction(tx):
        read_sets, rq_sets, write_sets = tx.get_rw_sets()
        rw_sets = []

        for rws in read_sets:
            rw_sets.append(KeyChange(tx, *rws, READ))

        for rqi in rq_sets:
            rw_sets.append(KeyChange(tx, *rqi, RANGE_QUERY))

        for rws in write_sets:
            rw_sets.append(KeyChange(tx, *rws, WRITE))

        return rw_sets

    @staticmethod
    def key_reference_exists(wk: str, rk: str):
        '''
        Does wk contain uuid of rk?
        '''
        wkey = Key(wk)
        rkey = Key(rk)
        wk_set = set(wkey.components[1:])
        rk_set = set(rkey.components[1:])
        return wk_set.intersection(rk_set) != set()
