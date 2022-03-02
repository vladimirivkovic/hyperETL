#!/usr/bin/python

import requests
import datetime
import random
import time
import json

from constants import *

URL = "http://localhost:3000"
TIME_SLEEP = 3
CASES_NO = 15


def api_call(path, payload=None):
    if payload == None:
        return requests.post(f"{URL}{path}")

    return requests.post(
        f"{URL}{path}", headers=DEFAULT_HEADERS, data=json.dumps(payload))


def buy_bike_and_claim_file(username, is_theft):
    start = datetime.datetime.now()
    end = start + datetime.timedelta(days=7)

    payload = {"user": {"username": username, **DEFAULT_BIKE}, "contractTypeUuid": DEFAULT_CONTRACT_TYPE,
               "additionalInfo": DEFAULT_BIKE, "startDate": start.isoformat(), "endDate": end.isoformat()}
    res = api_call("/shop/api/enter-contract", payload)

    if res.status_code != 200:
        return None

    time.sleep(TIME_SLEEP)

    body = json.loads(res.content)
    password = body["loginInfo"]["password"]
    uuid = body["loginInfo"]["uuid"]

    payload = {"user": {"username": username, "password": password},
               "contractUuid": uuid, "claim": {"isTheft": is_theft, "description": DEFAULT_DESCRIPTION}}
    res = api_call("/insurance/api/file-claim", payload)

    if res.status_code != 200:
        return None

    time.sleep(TIME_SLEEP)

    body = json.loads(res.content)
    claim_uuid = body["uuid"]

    return password, uuid, claim_uuid


def repair_bike(contract_uuid, claim_uuid):
    payload = {"contractUuid": contract_uuid,
               "uuid": claim_uuid, "status": "R", "reimbursable": 0}
    res = api_call("/insurance/api/process-claim", payload)

    if res.status_code != 200:
        return None

    time.sleep(TIME_SLEEP)

    res = api_call("/repair-shop/api/repair-orders")
    body = json.loads(res.content)
    body_filtered = filter(lambda x: x["claimUuid"] == claim_uuid, body)
    repair_order_uuid = list(body_filtered)[0]["uuid"]

    payload = {"uuid": repair_order_uuid}
    res = api_call("/repair-shop/api/complete-repair-order", payload)

    time.sleep(TIME_SLEEP)
    return res.status_code == 200


def police_report(contract_uuid, claim_uuid, is_theft):
    payload = {"contractUuid": contract_uuid, "uuid": claim_uuid,
               "isTheft": is_theft, "fileReference": DEFAULT_REPORT}
    res = api_call("/police/api/process-claim", payload)

    if res.status_code != 200:
        return False

    time.sleep(TIME_SLEEP)
    return True


def resolve_claim(contract_uuid, claim_uuid, status, reimbursable):
    payload = {"contractUuid": contract_uuid, "uuid": claim_uuid,
               "status": status, "reimbursable": reimbursable}
    res = api_call("/insurance/api/process-claim", payload)
    print(res.content)
    if res != 200:
        return False

    time.sleep(TIME_SLEEP)
    print(res.content)
    return True


def get_random_bool():
    return bool(random.getrandbits(1))


def random_case():
    is_theft = get_random_bool()
    user = random.choice(USERS)
    password, contract_uuid, claim_uuid = buy_bike_and_claim_file(
        user, is_theft)

    if is_theft:
        print("theft claimed")
        police_confirmed = get_random_bool()
        police_report(contract_uuid, claim_uuid, police_confirmed)

        if police_confirmed:
            print("theft confirmed")
            reimbursable = random.random() * REIMBURSEMENT_MAX
            resolve_claim(contract_uuid, claim_uuid, 'F', reimbursable)
            print("reimbursement ", reimbursable)
        else:
            print("theft rejected")
    else:
        print("problem claimed")
        insurance_rejected = get_random_bool()

        if insurance_rejected:
            print("insurance rejected")
            resolve_claim(contract_uuid, claim_uuid, 'J', 0)
            return

        repairable = get_random_bool()

        if repairable:
            print("bike repaired")
            repair_bike(contract_uuid, claim_uuid)
        else:
            reimbursable = random.random() * REIMBURSEMENT_MAX
            resolve_claim(contract_uuid, claim_uuid, 'F', reimbursable)
            print("reimbursement ", reimbursable)


if __name__ == "__main__":
    for i in range(CASES_NO):
        print("\nCASE ", i+1)
        random_case()
