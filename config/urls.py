# -*- coding: utf-8 -*-
"""
    config.urls
    ~~~~~~~~~~~~~~

    List of urls that will be consulted

    :copyright: (c) 2019 by Software Clever, Palace Resorts CEDIS.
    :license: Private.
"""

#: Clever's url
#: NOTE auth and dtc are reserved and will be added automatically.
URLS = {
    "dev": {
        "rates": "http://rates-api-qa.clever.palace-resorts.local",
        "auth": "http://auth-api-qa.clever.palace-resorts.local",
        'wire_reservation': 'http://wire-dev6/clever_reservation/api',
        'payment': 'http://finance-api-qa.clever.palace-resorts.local',
        'wire_clever':'http://wire-dev2/AspNetCoreWebService/api',
        'clever-frm' : 'http://frm-api-qa.clever.palace-resorts.local',
        'clever_code' : 'http://core-api-qa.clever.palace-resorts.local',
        'apiAssetsPy':'http://awsutil-api-qa.clever.palace-resorts.local',
        'bengine':'http://localhost:5000',
        'bengine_public':'http://localhost:3000',
        'charges_service': 'http://web-test19:8087/WireServiceInterface/service.asmx',
        "webfiles_palace": "https://s3.amazonaws.com/webfiles_palace"
    },
    "qa": {
        "rates": "http://rates-api-qa.clever.palace-resorts.local",
        "auth": "http://auth-api-qa.clever.palace-resorts.local",
        'wire_reservation': 'http://wire-dev6/clever_reservation/api',
        'payment': 'http://finance-api-qa.clever.palace-resorts.local',
        'wire_clever':'https://wireclever.web.palace-resorts.local/api',
        'clever-frm' : 'http://frm-api-qa.clever.palace-resorts.local',
        'clever_code' : 'http://core-api-qa.clever.palace-resorts.local',
        'apiAssetsPy':'http://awsutil-api-qa.clever.palace-resorts.local',
        'bengine':'http://bengine-api-qa.clever.palace-resorts.local',
        'bengine_public': 'http://bengine-public-qa.clever.palace-resorts.local',
        'charges_service': 'http://web-test19:8087/WireServiceInterface/service.asmx',
        "webfiles_palace": "https://s3.amazonaws.com/webfiles_palace"
    },
    "pro": {
        "rates": "http://rates-api.clever.palace-resorts.local",
        "auth": "http://auth-api.clever.palace-resorts.local",
        'wire_reservation': 'http://web-asp/resv/api',
        'payment': 'http://finance-api.clever.palace-resorts.local',
        'wire_clever':'https://wireclever.web.palace-resorts.local/api',
        'clever-frm' : 'http://frm-api.clever.palace-resorts.local',
        'clever_code' : 'http://core-api.clever.palace-resorts.local',
        'apiAssetsPy':'http://awsutil-api.clever.palace-resorts.local',
        'bengine':'http://bengine-api.clever.palace-resorts.local',
        'bengine_public' : 'https://onlinebookingspr.palaceresorts.com',
        'charges_service': 'http://cpr.web.palace-resorts.local:8087/WireServiceInterface/service.asmx',
        "webfiles_palace": "https://s3.amazonaws.com/webfiles_palace"
    },
}
