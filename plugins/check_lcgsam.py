#!/usr/bin/env python
#
# Copyright (c) 2015, Science and Technology Facilities Council
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
# NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
# Based on https://github.com/jcasals/nagios-plugins-lcgsam

import json
import optparse
import urllib2
import sys

OK=0
WARNING=1
CRITICAL=2
UNKNOWN=3

def get_sam_results(VO,SITE,PROFILE):
    SAMPI="http://wlcg-sam-" + VO + ".cern.ch/dashboard/request.py/latestresultssmry-json?profile=" + PROFILE + "&site=" + SITE
    try:
        return urllib2.urlopen(SAMPI).read()
    except Exception as e:
        print "Error retrieving results: %s" % e
        sys.exit(UNKNOWN)

def lcgsam3(VO,SITE,PROFILE):
    rtnSummary = "Service Status: "
    rtnDetails = ""
    problems = 0
    rtnCode = 0
    resultsjson=get_sam_results(VO,SITE,PROFILE)
    try:
        jsondata=json.loads(resultsjson)
    except Exception as e:
        print "Invalid JSON: %s" % e
        sys.exit(UNKNOWN)
    flavours=jsondata["data"]["results"][0]["flavours"]
    for flavour in flavours:
        rtnSummary = rtnSummary + flavour["flavourname"] + " = " + flavour["flavourStatus"]+ " // "
        if flavour["flavourStatus"] not in ["OK"]:
            problems=1
            if not rtnDetails:
                rtnDetails = "\nProblem details:\n"
            for flavourhost in flavour["hosts"]:
                rtnDetails = rtnDetails + flavourhost["hostname"] + " " + flavourhost["hostStatus"] + "\n"
    if problems:
        if "UNKNOWN" in rtnSummary:
            rtnCode=UNKNOWN
        elif "WARNING" in rtnSummary:
            rtnCode=WARNING
        elif "CRITICAL" in rtnSummary:
            rtnCode=CRITICAL
    return rtnSummary.rstrip(' // '), rtnDetails, rtnCode
    
if __name__ == "__main__":
    parser = optparse.OptionParser()
    parser.add_option("-v","--vo", dest="VO", metavar="<VO>", help="Choose one from alice, atlas, cms or lhcb")
    parser.add_option("-s","--site", dest="SITE", metavar="<SITE-NAME>")
    parser.add_option("-p","--profile", dest="PROFILE", metavar="<PROFILE>")
    (option, args) = parser.parse_args()
    if not (option.VO or option.SITE or option.PROFILE) :
        parser.print_help()
        sys.exit(3)
    (summary,details,rc)=lcgsam3(option.VO,option.SITE,option.PROFILE)
    print summary,details
    sys.exit(rc)
